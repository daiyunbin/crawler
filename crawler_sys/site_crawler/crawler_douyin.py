# -*- coding:utf-8 -*-
# @Time : 2019/9/4 18:19 
# @Author : litao

import os
import re
import time
import copy
import requests
import datetime
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from crawler.crawler_sys.framework.video_fields_std import Std_fields_video
from crawler.crawler_sys.utils.output_results import output_result
from crawler.crawler_sys.utils.util_logging import logged
from fontTools.ttLib import *
try:
    from crawler_sys.framework.func_get_releaser_id import *
except:
    from func_get_releaser_id import *

class Crawler_douyin():

    def __init__(self, timeout=None, platform='douyin'):
        if timeout == None:
            self.timeout = 10
        else:
            self.timeout = timeout
        self.platform = platform
        self.TotalVideo_num = None
        self.midstepurl = None
        std_fields = Std_fields_video()
        self.video_data = std_fields.video_data
        self.video_data['platform'] = self.platform
        unused_key_list = ['channel', 'describe', 'repost_count', 'isOriginal']
        for key in unused_key_list:
            self.video_data.pop(key)

    def get_cookies_and_font(self,url):
        self.first_page_headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Host": "live.kuaishou.com",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
        }
        self.cookie_dic = {}
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        #      driver = webdriver.Remote(command_executor='http://192.168.18.11:4444/wd/hub',
        # desired_capabilities=DesiredCapabilities.CHROME)
        driver = webdriver.Chrome(r'chromedriver', options=chrome_options)
        driver.get(url)
        time.sleep(2)
        driver.get(url)
        cookie = driver.get_cookies()
        for k in cookie:
            self.cookie_dic[k["name"]] = k["value"]
        # print(self.cookie_dic)

        font_face = driver.find_element_by_xpath("/html/head/style[1]")
        font_woff_link = re.findall("url\('(.*?)'\)\s+format\('woff'\)", font_face.get_attribute("innerHTML"))
        woff_name = font_woff_link[0].split("/")[-1]
        print(woff_name)
        woff = requests.get(font_woff_link[0]).content
        try:
            f = open("./" + woff_name, "r", encoding="utf-8")
        except:
            with open("./" + woff_name, "wb") as f:
                f.write(woff)
            font = TTFont("./" + woff_name)
            font.saveXML("./%s.xml" % woff_name)
        f = open("./%s.xml" % woff_name, encoding="utf-8")
        self.xml_text = f.read()
        driver.quit()
        self.uni_code_dic = self.get_num_dic()


    def get_releaser_id(self,releaserUrl):
        return get_releaser_id(platform=self.platform, releaserUrl=releaserUrl)

    @staticmethod
    def re_cal_count(count_num):
        if isinstance(count_num, int):
            return count_num
        if isinstance(count_num, str):
            if count_num[-1] == "w":
                return int(float(count_num[:-1]) * 10000)
            try:
                return int(count_num)
            except:
                return False
        return False


    def get_releaser_follower_num(self,releaserUrl):
        self.get_cookies_and_font(releaserUrl)
        releaser_id = self.get_releaser_id(releaserUrl)
        releaserUrl = 'https://live.kuaishou.com/profile/%s' % releaser_id
        pcursor = None
        releaser_page = requests.get(releaserUrl,headers=self.first_page_headers,cookies=self.cookie_dic)
        soup = BeautifulSoup(releaser_page.text, 'html.parser')
        try:
            releaser_follower_num_str = soup.find('div', {'class': 'user-data-item fans'}).string
            releaser_follower_num = self.re_cal_count(self.unicode_to_num(releaser_follower_num_str))
            print(releaser_follower_num)
            return releaser_follower_num
        except:
            return None


    def releaser_page(self, releaserUrl,
                      output_to_file=False,
                      filepath=None,
                      releaser_page_num_max=30,
                      output_to_es_raw=False,
                      es_index=None,
                      doc_type=None,
                      output_to_es_register=False,
                      push_to_redis=False,**kwargs):

        """
        get video info from api instead of web page html
        the most scroll page is 1000
        """
        self.get_cookies_and_font(releaserUrl)
        releaser = ""
        headers = {
            "accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "content-type": "application/json",
            "Host": "live.kuaishou.com",
            "Origin": "https://live.kuaishou.com",
            "Referer": releaserUrl,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
        }

        count = 1
        #        has_more = True
        retry_time = 0
        result_list = []
        releaser_id = self.get_releaser_id(releaserUrl)
        releaserUrl = 'https://live.kuaishou.com/profile/%s' % releaser_id
        pcursor = None
        principalId = releaser_id
        self.video_data['releaserUrl'] = releaserUrl

        # firset_page = requests.get(releaserUrl, headers=self.first_page_headers)
        # cookie = firset_page.cookies
        # firset_page = requests.get(releaserUrl, headers=self.first_page_headers,cookies=cookie)
        # cookie = firset_page.cookies

        while count <= releaser_page_num_max and count <= 1000 and pcursor != "no_more":
            variables = {"principalId": principalId, "pcursor": pcursor, "count": 24}
            url_dic = {"operationName": "publicFeedsQuery",
                       "variables": variables,
                       "query": "query publicFeedsQuery($principalId: String, $pcursor: String, $count: Int) {\n publicFeeds(principalId: $principalId, pcursor: $pcursor, count: $count) {\n pcursor\n live {\n user {\n id\n kwaiId\n eid\n profile\n name\n living\n __typename\n }\n watchingCount\n src\n title\n gameId\n gameName\n categoryId\n liveStreamId\n playUrls {\n quality\n url\n __typename\n }\n followed\n type\n living\n redPack\n liveGuess\n anchorPointed\n latestViewed\n expTag\n __typename\n }\n list {\n photoId\n caption\n thumbnailUrl\n poster\n viewCount\n likeCount\n commentCount\n timestamp\n workType\n type\n useVideoPlayer\n imgUrls\n imgSizes\n magicFace\n musicName\n location\n liked\n onlyFollowerCanComment\n relativeHeight\n width\n height\n user {\n id\n eid\n name\n profile\n __typename\n }\n expTag\n __typename\n }\n __typename\n }\n}\n"}
            api_url = 'https://live.kuaishou.com/graphql'
            get_page = requests.post(api_url, headers=headers, json=url_dic, cookies=self.cookie_dic)
            #print(get_page.content)
            page_dic = get_page.json()
            data_list = page_dic.get("data").get("publicFeeds").get("list")
            #print(data_list)
            if data_list == []:
                print("no more data at releaser: %s page: %s " % (releaser, count))
                pcursor = "no_more"
                continue
            else:
                pcursor = page_dic.get("data").get("publicFeeds").get("pcursor")
                print("get data at releaser: %s page: %s" % (releaser, count))
                count += 1
                for info_dic in data_list:
                    video_dic = copy.deepcopy(self.video_data)
                    video_dic['title'] = info_dic.get('caption')
                    video_dic['url'] = "https://live.kuaishou.com/u/%s/%s" % (releaser_id, info_dic.get('photoId'))
                    video_dic['releaser'] = info_dic.get('user').get("name")
                    video_dic['releaserUrl'] = releaserUrl
                    video_dic['release_time'] = info_dic.get('timestamp')
                    video_dic['play_count'] = self.re_cal_count(self.unicode_to_num(info_dic.get('viewCount')))
                    video_dic['comment_count'] = self.re_cal_count(self.unicode_to_num(info_dic.get('commentCount')))
                    video_dic['favorite_count'] = self.re_cal_count(self.unicode_to_num(info_dic.get('likeCount')))
                    video_dic['video_id'] = info_dic.get('photoId')
                    video_dic['fetch_time'] = int(time.time() * 1e3)
                    releaser_id = info_dic.get('user').get("id")
                    video_dic['releaser_id_str'] = "kwai_%s"% (releaser_id)
                    if video_dic['play_count'] is False or video_dic['comment_count'] is False or video_dic['favorite_count'] is False:
                        print(info_dic)
                        continue
                    else:
                        result_list.append(video_dic)
                    if len(result_list) >= 100:
                        output_result(result_Lst=result_list,
                                      platform=self.platform,
                                      output_to_file=output_to_file,
                                      filepath=filepath,
                                      output_to_es_raw=output_to_es_raw,
                                      es_index=es_index,
                                      doc_type=doc_type,
                                      output_to_es_register=output_to_es_register)
                        print(len(result_list))
                        result_list.clear()
        if result_list != []:
            output_result(result_Lst=result_list,
                          platform=self.platform,
                          output_to_file=output_to_file,
                          filepath=filepath,
                          output_to_es_raw=output_to_es_raw,
                          es_index=es_index,
                          doc_type=doc_type,
                          output_to_es_register=output_to_es_register)
            print(len(result_list))
            result_list.clear()
        return result_list


# test
if __name__ == '__main__':
    test = Crawler_douyin()
    url = 'https://www.iesdouyin.com/share/user/104881369596'
    user_lis = [

    ]
    for u in user_lis:
        ttt = test.releaser_page(releaserUrl="https://www.iesdouyin.com/share/user/104881369596", output_to_es_raw=True,
                                 es_index='crawler-data-raw',
                                 doc_type='doc',
                                 releaser_page_num_max=200)
        #test.get_releaser_follower_num(u)
        #break
