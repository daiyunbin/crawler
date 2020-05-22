# -*- coding:utf-8 -*-
# @Time : 2019/10/21 17:53 
# @Author : litao
from write_data_into_es.func_get_releaser_id import get_releaser_id as get_id
import redis, elasticsearch, time, datetime, sys
from crawler.crawler_sys.framework.update_data_in_redis_multi_process_auto_task import get_crawler
from write_data_into_es.target_releaser_add import write_to_es
from concurrent.futures import ThreadPoolExecutor
from maintenance.send_email_with_file_auto_task import write_email_task_to_redis
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
import re

pool = redis.ConnectionPool(host='192.168.17.60', port=6379, db=2, decode_responses=True)
rds = redis.Redis(connection_pool=pool)


def check_releaserUrl(file):
    bulk_all_body = ""
    count = 0
    try:
        f = open(file, 'r', encoding="gb18030")
        head = f.readline()
        head_list = head.strip().split(',')
    except:
        f = file
    for i in f:
        if type(file) != list:
            line_list = i.strip().split(',')
            line_dict = dict(zip(head_list, line_list))
        else:
            line_dict = i
        # print(i)
        for k in line_dict:
            line_dict[k] = line_dict[k].strip().replace("\r", "").replace("\n", "").replace("\t", "")
        platform = line_dict['platform']
        releaser = line_dict['releaser']
        releaserUrl = line_dict['releaserUrl']
        releaser_id = get_id(platform=platform, releaserUrl=releaserUrl)
        if releaser_id:
            releaser_doc_id = platform + "_" + releaser_id
        else:
            releaser_doc_id = platform + "_" + releaser
        rds.lpush("releaser_doc_id_list", releaser_doc_id)


def carw_data_by_seleium(platfrom, releaserUrl, driver):
    if platfrom == "weibo":
        try:
            # driver.get(releaserUrl)
            # driver.save_screenshot("./screenshot.png")
            res = driver.find_element_by_xpath('//*[@id="Pl_Core_CustTab__2"]/div/div/table/tbody/tr/td[1]/a')
            url = res.get_attribute("href")
            releaser_id = get_id(platform="weibo", releaserUrl=url)
            print(url, releaser_id)
            if releaser_id:
                return releaser_id, url
            else:
                return None, None
        except:
            return None, None
    elif platfrom == "抖音":
        try:
            res = driver.page_source
            releaser_id = re.findall('uid: "(\d*)",', res, flags=re.DOTALL)[0]
            url = driver.current_url
            return "抖音_%s" % releaser_id, url
        except:
            return None, None
    elif platfrom == "miaopai":
        try:
            res = driver.find_element_by_xpath('//*[@id="app"]/div/header/div[1]/img')
            releaser_id = get_id(platform="miaopai", releaserUrl=releaserUrl)
            url = driver.current_url
            if releaser_id in url:
                return "miaopai_%s" % releaser_id, url
            else:
                return None, None
        except:
            return None, None
    return None, None


def delete_by_id(_id):
    data = ""
    data = data + ('{"delete": {"_id":"%s"}}\n' % _id)
    es.bulk(body=data, index="target_releasers", doc_type="doc")


def get_releaserUrl_from_es(releaser_id_str):
    global email_dic
    try:
        search_res = es.get("target_releasers", "doc", releaser_id_str)
    except:
        return None
    # print(search_res)
    res_data = search_res["_source"]
    releaserUrl = res_data["releaserUrl"]
    releaser = res_data["releaser"]
    platform = res_data["platform"]
    post_by = res_data.get("post_by")
    print(platform, releaserUrl)
    crawler = get_crawler(platform)
    count_false = 0
    has_data = False
    if crawler:
        while count_false < 5:
            try:
                # 访问有效有数据
                crawler_instant = crawler()
                crawler_releaser_page = crawler_instant.releaser_page
                for single_data in crawler_releaser_page(releaserUrl=releaserUrl, proxies_num=1,
                                                         releaser_page_num_max=3):
                    if single_data["releaser_id_str"] == releaser_id_str:
                        res_data.update({"is_valid": "true", "has_data": 2})
                        # print(res_data)
                        write_to_es([res_data], push_to_redis=False)
                        count_false = 5
                        has_data = True
                        break
                    else:
                        delete_by_id(releaser_id_str)
                        if post_by:
                            if not email_dic.get(post_by):
                                email_dic[post_by] = []
                            email_dic[post_by].append(
                                    releaser + " " + platform + " " + releaserUrl + " 错误,将替换为 %s \n" % single_data[
                                        "releaserUrl"])

                        res_data.update({"is_valid": "true", "has_data": 2, "releaserUrl": single_data["releaserUrl"]})
                        write_to_es([res_data], push_to_redis=False)
                        # print(res_data)
                        has_data = True
                        count_false = 5
                        break
                if not has_data:
                    count_false = 5
                    raise Exception("has no data in", platform, releaserUrl)
            except Exception as e:
                # 访问有效无数据
                print(e)
                if count_false <= 5:
                    count_false += 1
                    continue
                res_data.update({"is_valid": "true", "has_data": 1})
                if post_by:
                    if not email_dic.get(post_by):
                        email_dic[post_by] = []
                    email_dic[post_by].append(
                            releaser + " " + platform + " " + releaserUrl + " 该releaserUrl 访问无数据\n")
                # print(res_data)
                write_to_es([res_data], push_to_redis=False)
                count_false = 5
    else:
        # 供应商数据
        if res_data["platform"] in ["weixin"]:
            if post_by:
                if not email_dic.get(post_by):
                    email_dic[post_by] = []
                email_dic[post_by].append(
                        releaser + " " + platform + " " + releaserUrl + " 供应商数据暂无法解析 \n")
            res_data.update({"is_valid": "true", "has_data": 0})
            write_to_es([res_data], push_to_redis=False)
        elif res_data["platform"] in ["抖音", "miaopai", "weibo"]:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(releaserUrl)
            driver.implicitly_wait(5)
            check_id, check_url = carw_data_by_seleium(platform, releaserUrl, driver)
            driver.quit()
            if check_id:
                if check_id == releaser_id_str:
                    res_data.update({"is_valid": "true", "has_data": 2})
                    # print(res_data)
                    write_to_es([res_data], push_to_redis=False)

                else:
                    delete_by_id(releaser_id_str)
                    if post_by:
                        if not email_dic.get(post_by):
                            email_dic[post_by] = []
                        email_dic[post_by].append(
                                releaser + " " + platform + " " + releaserUrl + " 错误,将替换为 %s \n" % check_url)
                    res_data.update({"is_valid": "true", "has_data": 2, "releaserUrl": check_url})
                    write_to_es([res_data], push_to_redis=False)
                    # print(res_data)

            else:
                res_data.update({"is_valid": "false", "has_data": 0})
                if post_by:
                    if not email_dic.get(post_by):
                        email_dic[post_by] = []
                    email_dic[post_by].append(
                            releaser + " " + platform + " " + releaserUrl + " 该releaserUrl 访问无数据\n")
                # print(res_data)
                write_to_es([res_data], push_to_redis=False)
        else:
            res_data.update({"is_valid": "flase", "has_data": 0})
            if post_by:
                if not email_dic.get(post_by):
                    email_dic[post_by] = []
                email_dic[post_by].append(
                        releaser + " " + platform + " " + releaserUrl + " 该平台数据暂无法解析 \n")
            write_to_es([res_data], push_to_redis=False)


def craw_one_page_from_es():
    global email_dic
    now = datetime.datetime.now()
    while True and now.hour > 1:
        executor = ThreadPoolExecutor(max_workers=12)
        len_releaser_id_list = rds.llen("releaser_doc_id_list")
        while len_releaser_id_list > 0:
            releaser_id_str = rds.lpop("releaser_doc_id_list")
            len_releaser_id_list -= 1
            print(releaser_id_str)
            # get_releaserUrl_from_es(releaser_id_str)
            executor.submit(get_releaserUrl_from_es, releaser_id_str)
        executor.shutdown(wait=True)
        print(email_dic)
        for receiver in email_dic:
            email_msg_body_str = "问好:\n"
            for body in email_dic[receiver]:
                email_msg_body_str += body
            write_email_task_to_redis(
                task_name="check_releaserUrl_%s" % str(int(datetime.datetime.now().timestamp() * 1e3)),
                email_group=[receiver + "@csm.com.cn"],
                sender=receiver + "@csm.com.cn", email_msg_body_str=email_msg_body_str, title_str="添加账号校验结果",
                cc_group=["litao@csm.com.cn", "liushuangdan@csm.com.cn", "gengdi@csm.com.cn"])
        email_dic = {}
        print("timesleep 5")
        time.sleep(5)
        now = datetime.datetime.now()
    sys.exit(0)


if __name__ == "__main__":
    # check_releaserUrl(r"D:\work_file\发布者账号\brief9月需求账号list (version 1).csv")
    email_dic = {}
    hosts = '192.168.17.11'
    port = 80
    user = 'ccr_managesys'
    passwd = 'Lu9i70pcV0Gc'
    http_auth = (user, passwd)
    es = elasticsearch.Elasticsearch(hosts=hosts, port=port, http_auth=http_auth)
    craw_one_page_from_es()
