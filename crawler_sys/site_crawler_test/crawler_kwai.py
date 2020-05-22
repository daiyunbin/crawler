# -*- coding:utf-8 -*-
# @Time : 2019/4/17 9:15
# @Author : litao
# -*- coding: utf-8 -*-

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
from crawler.crawler_sys.proxy_pool.func_get_proxy_form_kuaidaili import get_proxy
from crawler.crawler_sys.utils.func_verification_code import Login
from crawler.crawler_sys.utils.trans_str_play_count_to_int import trans_play_count

class Crawler_kwai():

    def __init__(self, timeout=None, platform='kwai'):
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
        self.loginObj = Login()
        self.get_cookies_and_front = self.loginObj.get_cookies_and_front


    def get_cookies_and_font(self,releaserUrl):
        self.cookie_dic, self.uni_code_dic = self.get_cookies_and_front(releaserUrl)
        # self.cookie_dic = {}
        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # #      driver = webdriver.Remote(command_executor='http://192.168.18.11:4444/wd/hub',
        # # desired_capabilities=DesiredCapabilities.CHROME)
        # driver = webdriver.Chrome(r'chromedriver', options=chrome_options)
        # driver.get(url)
        # time.sleep(2)
        # driver.get(url)
        # cookie = driver.get_cookies()
        # for k in cookie:
        #     self.cookie_dic[k["name"]] = k["value"]
        # # print(self.cookie_dic)
        #
        # font_face = driver.find_element_by_xpath("/html/head/style[1]")
        # font_woff_link = re.findall("url\('(.*?)'\)\s+format\('woff'\)", font_face.get_attribute("innerHTML"))
        # woff_name = font_woff_link[0].split("/")[-1]
        # print(woff_name)
        # woff = requests.get(font_woff_link[0]).content
        # os_path = "/home/hanye/"
        # this_path = os.path.isdir(os_path)
        # if not this_path:
        #     os_path = "."
        # try:
        #     f = open("%s/%s.xml" % (os_path, woff_name), encoding="utf-8")
        # except:
        #     woff = requests.get(font_woff_link[0],
        #                         headers={
        #                                 "Referer": url,
        #                                 "Sec-Fetch-Mode": "cors",
        #                                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}).content
        #     with open("%s/%s" % (os_path, woff_name), "wb") as f:
        #         f.write(woff)
        #     font = TTFont("%s/%s" % (os_path, woff_name))
        #     font.saveXML("%s/%s.xml" % (os_path, woff_name))
        #     f = open("%s/%s.xml" % (os_path, woff_name), encoding="utf-8")
        # #f = open("./%s.xml" % woff_name, encoding="utf-8")
        # self.xml_text = f.read()
        # driver.quit()
        # self.uni_code_dic = self.get_num_dic()

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


    # def get_num_dic(self):
    #     xml_re = {
    #             '<TTGlyph name="(.*)" xMin="32" yMin="-6" xMax="526" yMax="729">': 0,
    #             '<TTGlyph name="(.*)" xMin="32" yMin="7" xMax="526" yMax="742">': 0,
    #             '<TTGlyph name="(.*)" xMin="98" yMin="13" xMax="363" yMax="726">': 1,
    #             '<TTGlyph name="(.*)" xMin="98" yMin="26" xMax="363" yMax="739">': 1,
    #             '<TTGlyph name="(.*)" xMin="32" yMin="13" xMax="527" yMax="732">': 2,
    #             '<TTGlyph name="(.*)" xMin="32" yMin="26" xMax="527" yMax="745">': 2,
    #             '<TTGlyph name="(.*)" xMin="25" yMin="-6" xMax="525" yMax="730">': 3,
    #             '<TTGlyph name="(.*)" xMin="25" yMin="7" xMax="525" yMax="743">': 3,
    #             '<TTGlyph name="(.*)" xMin="26" yMin="13" xMax="536" yMax="731">': 4,
    #             '<TTGlyph name="(.*)" xMin="26" yMin="26" xMax="536" yMax="744">': 4,
    #             '<TTGlyph name="(.*)" xMin="33" yMin="-5" xMax="526" yMax="717">': 5,
    #             '<TTGlyph name="(.*)" xMin="33" yMin="8" xMax="526" yMax="730">': 5,
    #             '<TTGlyph name="(.*)" xMin="39" yMin="-5" xMax="530" yMax="732">': 6,
    #             '<TTGlyph name="(.*)" xMin="39" yMin="8" xMax="530" yMax="745">': 6,
    #             '<TTGlyph name="(.*)" xMin="38" yMin="13" xMax="536" yMax="717">': 7,
    #             '<TTGlyph name="(.*)" xMin="38" yMin="26" xMax="536" yMax="730">': 7,
    #             '<TTGlyph name="(.*)" xMin="33" yMin="-7" xMax="525" yMax="731">': 8,
    #             '<TTGlyph name="(.*)" xMin="33" yMin="6" xMax="525" yMax="744">': 8,
    #             '<TTGlyph name="(.*)" xMin="37" yMin="-7" xMax="521" yMax="730">': 9,
    #             '<TTGlyph name="(.*)" xMin="37" yMin="6" xMax="521" yMax="743">': 9
    #     }
    #     uni_code_dic = {}
    #     try:
    #         for re_code in xml_re:
    #             code_dic = re.findall(re_code, self.xml_text)
    #             if code_dic:
    #                 uni_code_dic[code_dic[0].replace("uni", "\\\\u").lower()] = xml_re[re_code]
    #         print("uni_code_dic", uni_code_dic)
    #         return uni_code_dic
    #     except:
    #         print(self.xml_text,"error front_error")
    #         return False
    #
    def unicode_to_num(self,uni_str):
        count_num = str(uni_str.encode("unicode_escape"))[2:-1]
        #print(count_num)
        for i in self.uni_code_dic:
            if i in count_num:
                count_num = count_num.replace(i, str(self.uni_code_dic[i]))
        #print(count_num)
        return count_num

    @staticmethod
    def get_video_image(data):
        pass

    #    @logged
    def releaser_page(self, releaserUrl,
                      output_to_file=False,
                      filepath=None,
                      releaser_page_num_max=10000,
                      output_to_es_raw=False,
                      es_index=None,
                      doc_type=None,
                      output_to_es_register=False,
                      push_to_redis=False,proxies_num=None):

        """
        get video info from api instead of web page html
        the most scroll page is 1000
        """
        releaser = ""
        proxies = get_proxy(proxies_num)
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
        pcursor = None
        principalId = releaser_id
        self.video_data['releaserUrl'] = releaserUrl
        while count <= releaser_page_num_max and count <= 1000 and pcursor != "no_more":
            self.get_cookies_and_font(releaserUrl)
            variables = {"principalId": principalId, "pcursor": pcursor, "count": 24}
            url_dic = {"operationName": "publicFeedsQuery",
                       "variables": variables,
                       "query": "query publicFeedsQuery($principalId: String, $pcursor: String, $count: Int) {\n  publicFeeds(principalId: $principalId, pcursor: $pcursor, count: $count) {\n    pcursor\n    live {\n      user {\n        id\n        avatar\n        name\n        __typename\n      }\n      watchingCount\n      poster\n      coverUrl\n      caption\n      id\n      playUrls {\n        quality\n        url\n        __typename\n      }\n      quality\n      gameInfo {\n        category\n        name\n        pubgSurvival\n        type\n        kingHero\n        __typename\n      }\n      hasRedPack\n      liveGuess\n      expTag\n      __typename\n    }\n    list {\n      id\n      thumbnailUrl\n      poster\n      workType\n      type\n      useVideoPlayer\n      imgUrls\n      imgSizes\n      magicFace\n      musicName\n      caption\n      location\n      liked\n      onlyFollowerCanComment\n      relativeHeight\n      timestamp\n      width\n      height\n      counts {\n        displayView\n        displayLike\n        displayComment\n        __typename\n      }\n      user {\n        id\n        eid\n        name\n        avatar\n        __typename\n      }\n      expTag\n      __typename\n    }\n    __typename\n  }\n}\n"}
            api_url = 'https://live.kuaishou.com/m_graphql'
            if proxies:
                get_page = requests.post(api_url, headers=headers, json=url_dic, cookies=self.cookie_dic,timeout=5,proxies=proxies)
            else:
                get_page = requests.post(api_url, headers=headers, json=url_dic, cookies=self.cookie_dic,timeout=5)
            #print(get_page.content)
            page_dic = get_page.json()
            data_list = page_dic.get("data").get("publicFeeds").get("list")
            #print(data_list)
            if data_list == []:
                print("no more data at releaser: %s page: %s " % (releaser, count))
                self.loginObj.delete_cookies(self.cookie_dic)
                retry_time += 1
                if retry_time > 2:
                    pcursor = "no_more"
                continue
            else:
                pcursor = page_dic.get("data").get("publicFeeds").get("pcursor")
                print("get data at releaser: %s page: %s" % (releaser, count))
                count += 1
                for info_dic in data_list:
                    video_dic = copy.deepcopy(self.video_data)
                    video_dic['title'] = info_dic.get('caption')
                    releaser_id = info_dic.get('user').get("eid")
                    video_dic['url'] = "https://live.kuaishou.com/u/%s/%s" % (releaser_id, info_dic.get('id'))
                    video_dic['releaser'] = info_dic.get('user').get("name")
                    video_dic['release_time'] = info_dic.get('timestamp')
                    video_dic['play_count'] = trans_play_count(info_dic.get('counts').get("displayView"))
                    video_dic['comment_count'] = trans_play_count(info_dic.get('counts').get("displayComment"))
                    video_dic['favorite_count'] = trans_play_count(info_dic.get('counts').get("displayLike"))
                    video_dic['video_id'] = info_dic.get('id')
                    video_dic['fetch_time'] = int(time.time() * 1e3)
                    video_dic['releaser_id_str'] = "kwai_%s"% (releaser_id)
                    video_dic['releaserUrl'] = 'https://live.kuaishou.com/profile/%s' % releaser_id
                    video_dic['video_img'] = self.get_video_image(info_dic)
                    if video_dic['play_count'] is False or video_dic['comment_count'] is False or video_dic['favorite_count'] is False:
                        print(info_dic)
                        continue
                    else:
                        yield video_dic

    def releaser_page_by_time(self, start_time, end_time, url,**kwargs):
        data_lis = []
        count_false = 0
        output_to_file = kwargs.get("output_to_file")
        filepath = kwargs.get("filepath")
        push_to_redis = kwargs.get("push_to_redis")
        output_to_es_register = kwargs.get("output_to_es_register")
        output_to_es_raw = kwargs.get("output_to_es_raw")
        es_index = kwargs.get("es_index")
        doc_type = kwargs.get("doc_type")
        for res in self.releaser_page(url,proxies_num=kwargs.get("proxies_num")):
            video_time = res["release_time"]
            # print(res)
            if video_time:
                if start_time < video_time:
                    if video_time < end_time:
                        data_lis.append(res)

                        if len(data_lis) >= 100:
                            output_result(result_Lst=data_lis,
                                          platform=self.platform,
                                          output_to_file=output_to_file,
                                          filepath=filepath,
                                          push_to_redis=push_to_redis,
                                          output_to_es_register=output_to_es_register,
                                          output_to_es_raw=output_to_es_raw,
                                          es_index=es_index,
                                          doc_type=doc_type)
                            data_lis.clear()

                else:
                    count_false += 1
                    if count_false > 50:
                        break
                    else:
                        continue

        if data_lis != []:
            output_result(result_Lst=data_lis,
                          platform=self.platform,
                          output_to_file=output_to_file,
                          filepath=filepath,
                          push_to_redis=push_to_redis,
                          output_to_es_register=output_to_es_register,
                          output_to_es_raw=output_to_es_raw,
                          es_index=es_index,
                          doc_type=doc_type)
    @staticmethod
    def get_video_image(data):
        return data.get("poster")


    def get_releaser_follower_num(self, releaserUrl):
        self.get_cookies_and_font(releaserUrl)
        releaser_id = self.get_releaser_id(releaserUrl)
        releaserUrl = 'https://live.kuaishou.com/graphql'
        post_dic = {"operationName":"userInfoQuery","variables":{"principalId":releaser_id},"query":"query userInfoQuery($principalId: String) {\n  userInfo(principalId: $principalId) {\n    id\n    principalId\n    kwaiId\n    eid\n    userId\n    profile\n    name\n    description\n    sex\n    constellation\n    cityName\n    living\n    watchingCount\n    isNew\n    privacy\n    feeds {\n      eid\n      photoId\n      thumbnailUrl\n      timestamp\n      __typename\n    }\n    verifiedStatus {\n      verified\n      description\n      type\n      new\n      __typename\n    }\n    countsInfo {\n      fan\n      follow\n      photo\n      liked\n      open\n      playback\n      private\n      __typename\n    }\n    bannedStatus {\n      banned\n      defriend\n      isolate\n      socialBanned\n      __typename\n    }\n    __typename\n  }\n}\n"}
        releaser_page = requests.post(releaserUrl, headers=self.first_page_headers, cookies=self.cookie_dic,json=post_dic)
        res_dic = releaser_page.json()

        try:
            releaser_follower_num_str =res_dic["data"]["userInfo"]["countsInfo"]["fan"]
            releaser_follower_num = self.re_cal_count(self.unicode_to_num(releaser_follower_num_str))
            print(releaser_follower_num)
            releaser_img = self.get_releaser_image(data=res_dic)
            return releaser_follower_num,releaser_img
        except:
            return None

    def get_releaser_image(self, releaserUrl=None,data=None):
        if releaserUrl:
            self.get_cookies_and_font(releaserUrl)
            releaser_id = self.get_releaser_id(releaserUrl)
            releaserUrl = 'https://live.kuaishou.com/graphql'
            post_dic = {"operationName": "userInfoQuery", "variables": {"principalId": releaser_id},
                        "query": "query userInfoQuery($principalId: String) {\n  userInfo(principalId: $principalId) {\n    id\n    principalId\n    kwaiId\n    eid\n    userId\n    profile\n    name\n    description\n    sex\n    constellation\n    cityName\n    living\n    watchingCount\n    isNew\n    privacy\n    feeds {\n      eid\n      photoId\n      thumbnailUrl\n      timestamp\n      __typename\n    }\n    verifiedStatus {\n      verified\n      description\n      type\n      new\n      __typename\n    }\n    countsInfo {\n      fan\n      follow\n      photo\n      liked\n      open\n      playback\n      private\n      __typename\n    }\n    bannedStatus {\n      banned\n      defriend\n      isolate\n      socialBanned\n      __typename\n    }\n    __typename\n  }\n}\n"}
            releaser_page = requests.post(releaserUrl, headers=self.first_page_headers, cookies=self.cookie_dic,
                                          json=post_dic)
            res_dic = releaser_page.json()
            try:
                releaser_img = res_dic["data"]["userInfo"]["profile"]
                print(releaser_img)
                return releaser_img
            except:
                return None
        else:
            releaser_img = data["data"]["userInfo"]["profile"]
            print(releaser_img)
            return releaser_img

if __name__ == '__main__':
    test = Crawler_kwai()
    url = 'https://live.kuaishou.com/profile/IIloveyoubaby'
    user_lis = [
            "https://live.kuaishou.com/profile/3xw8s48b2q7htx9",
            "https://live.kuaishou.com/profile/3x7zjfzv3tw2rq2",
            "https://live.kuaishou.com/profile/3x9d2uynzb5anwc",
            "https://live.kuaishou.com/profile/3xpvev7ziw57zn2",
            "https://live.kuaishou.com/profile/3xqb2kbuidsgtuy",
            "https://live.kuaishou.com/profile/3xetpxwv59yakh2",
            "https://live.kuaishou.com/profile/3xqw5f8prir5hjy",
            "https://live.kuaishou.com/profile/3xfy32ce2ae74yq",
            "https://live.kuaishou.com/profile/3xn4rrvjv2rfsug",
            "https://live.kuaishou.com/profile/3xqfjpvpijfxq26",
            "https://live.kuaishou.com/profile/3xxagpqendgxndm",
            "https://live.kuaishou.com/profile/3x2s6rhdnz7svzy",
            "https://live.kuaishou.com/profile/3x2kubzhwfvwc7y",
            "https://live.kuaishou.com/profile/3xmyhdcda33jaek",
            "https://live.kuaishou.com/profile/3x35wz99psxxzxa",
            "https://live.kuaishou.com/profile/3x6dg3ffvrvhip4",
            "https://live.kuaishou.com/profile/3xfkqzaezgjr52a",
            "https://live.kuaishou.com/profile/3xpwasuwu38eqby",
            "https://live.kuaishou.com/profile/3xbywas62b3xxp9",
            "https://live.kuaishou.com/profile/3xa46jbx9x5itrc",
            "https://live.kuaishou.com/profile/3xkxef6mjf3tdx9",
            "https://live.kuaishou.com/profile/3xajbep9vsm3hgi",
            "https://live.kuaishou.com/profile/3xq5pmqdzcmdf7s",
            "https://live.kuaishou.com/profile/3xvzbpj8pue64cm",
            "https://live.kuaishou.com/profile/3xwnsfvwp2f5ags",
            "https://live.kuaishou.com/profile/3xpecxr23ptuyti",
            "https://live.kuaishou.com/profile/3xbndwrqr8mpekc",
            "https://live.kuaishou.com/profile/3xx7p9sas39ssmw",
            "https://live.kuaishou.com/profile/3xde7q377pq6ebm",
            "https://live.kuaishou.com/profile/3xw3gtjxrjszrw2",
            "https://live.kuaishou.com/profile/3xzevrh52abg632",
            "https://live.kuaishou.com/profile/3xpe4w4aiwgzc6s",
            "https://live.kuaishou.com/profile/3xqyrfjzgtgqq9q",
            "https://live.kuaishou.com/profile/3x7hf6p86t2vz7m",
            "https://live.kuaishou.com/profile/3xkty7h9hdqcnhw",
            "https://live.kuaishou.com/profile/3xcicym295esmdm",
            "https://live.kuaishou.com/profile/3xjg7f34rezj9c9",
            "https://live.kuaishou.com/profile/3xhbchtw8hxv3ac",
            "https://live.kuaishou.com/profile/3xs23bvvwtx4pb6",
            "https://live.kuaishou.com/profile/3xk22av9inmpk5g",
            "https://live.kuaishou.com/profile/3xm8quf6bbkvjkw",
            "https://live.kuaishou.com/profile/3xwxm8mj4v7wb3s",
            "https://live.kuaishou.com/profile/3xdr7ms8bjbhdss",
            "https://live.kuaishou.com/profile/3xrv5bi63spudng",
            "https://live.kuaishou.com/profile/3xbakxygv3w78vg",
            "https://live.kuaishou.com/profile/3x8csfrcq7gdnrk",
            "https://live.kuaishou.com/profile/3xjt6gsvx8ak22i",
            "https://live.kuaishou.com/profile/3xv23y98juzc6e4",
            "https://live.kuaishou.com/profile/3x2izajr6bdz5xg",
            "https://live.kuaishou.com/profile/3xqbgzrugm5kq36",
            "https://live.kuaishou.com/profile/3xxfhbssqbi9jsi",
            "https://live.kuaishou.com/profile/3xf6xffvgjigcrq",
            "https://live.kuaishou.com/profile/3xfyiua6ezi25tu",
            "https://live.kuaishou.com/profile/3xprsvh7zwxq9yq",
            "https://live.kuaishou.com/profile/3xyz2byfq7q3awq",
            "https://live.kuaishou.com/profile/3xexekrvnik44kq",
            "https://live.kuaishou.com/profile/3x69bkxchj656wy",
            "https://live.kuaishou.com/profile/3xxmrk764fsg8xk",
            "https://live.kuaishou.com/profile/3xqu3dusau3ajx4",
            "https://live.kuaishou.com/profile/3xtfz8f2zf5hmk4",
            "https://live.kuaishou.com/profile/3xdeay2ayc2v6gi",
            "https://live.kuaishou.com/profile/3xam9fuy95d3bzg",
            "https://live.kuaishou.com/profile/3x6pp2dtdreprsk",
            "https://live.kuaishou.com/profile/3x36h6jih78n7r6",
            "https://live.kuaishou.com/profile/3xqphaz663ez5pu",
            "https://live.kuaishou.com/profile/3xw8aq2s8b59ihk",
            "https://live.kuaishou.com/profile/3xs85vss8cubvm2",
            "https://live.kuaishou.com/profile/3xri78cm428rzzs",
            "https://live.kuaishou.com/profile/3x5u43aa3eh94xa",
            "https://live.kuaishou.com/profile/3x5hke2m257xp9s",
            "https://live.kuaishou.com/profile/3xw2xrap8hqfv9y",
            "https://live.kuaishou.com/profile/3x68qxknviu9a9k",
            "https://live.kuaishou.com/profile/3xah5a289xjwmc9",
            "https://live.kuaishou.com/profile/3xznbziq7h27i29",
            "https://live.kuaishou.com/profile/3x7q3bwrhae65hu",
            "https://live.kuaishou.com/profile/3x28vpis8aqasf2",
            "https://live.kuaishou.com/profile/3x8bwugg4b224ss",
            "https://live.kuaishou.com/profile/3xh92xfx5bgui7y",
            "https://live.kuaishou.com/profile/3xk2vxum34jqtdg",
            "https://live.kuaishou.com/profile/3xa24fpd5x8drmm",
            "https://live.kuaishou.com/profile/3xy8454u6qykpve",
            "https://live.kuaishou.com/profile/3xssvvqbimn4769",
            "https://live.kuaishou.com/profile/3xdkvxj83q83kxy",
            "https://live.kuaishou.com/profile/3xrswkbbfs6t89i",
            "https://live.kuaishou.com/profile/3xfjfdnmb78vh3m",
            "https://live.kuaishou.com/profile/3x4xhryw2rrrz24",
            "https://live.kuaishou.com/profile/3x457wrev4re8sq",
            "https://live.kuaishou.com/profile/3xwapzqbhsrj99s",
            "https://live.kuaishou.com/profile/ny18887453",
            "https://live.kuaishou.com/profile/3xi9yr7kdq4j23e",
            "https://live.kuaishou.com/profile/3xpiswkwghdtefq",
            "https://live.kuaishou.com/profile/3xj76a4cup65dia",
            "https://live.kuaishou.com/profile/3xczbuqu8dhh3ts",
            "https://live.kuaishou.com/profile/3xhipzd4hzjvksg",
            "https://live.kuaishou.com/profile/3xu2cqukscnh9d2",
            "https://live.kuaishou.com/profile/3xe3djw5bvuwmdg",
            "https://live.kuaishou.com/profile/3xtedja7vw7utwm",
            "https://live.kuaishou.com/profile/3xk8ebi92jt64xk",
            "https://live.kuaishou.com/profile/3xurvuj6fupq8nk",
            "https://live.kuaishou.com/profile/3xieptyduwdu2ik",
            "https://live.kuaishou.com/profile/3xuq22dd9diqv3g",
            "https://live.kuaishou.com/profile/Northeast-1st-farm",
            "https://live.kuaishou.com/profile/3xuq22dd9diqv3g",
            "https://live.kuaishou.com/profile/3xgykx7nx3fwbs4",
            "https://live.kuaishou.com/profile/3xdnwg4987swfse",
            "https://live.kuaishou.com/profile/3xy3gfahbe9xayu",
            "https://live.kuaishou.com/profile/3xwewus275hp9ty",
            "https://live.kuaishou.com/profile/3x62qjb5j97gk2q",
            "https://live.kuaishou.com/profile/3xzbkrxxz2wzvy2",
            "https://live.kuaishou.com/profile/3xzfimu49gdt8ny",
            "https://live.kuaishou.com/profile/3xwkfzm28zefdik",
            "https://live.kuaishou.com/profile/3xqnrjgz7k6m3em",
            "https://live.kuaishou.com/profile/3xczki2m45jd8ik",
            "https://live.kuaishou.com/profile/3xnxvbdj4u8vwqw",
            "https://live.kuaishou.com/profile/3xkakwcdfjmv7qg",
            "https://live.kuaishou.com/profile/3xdeqc5e3u7pwv6",
            "https://live.kuaishou.com/profile/3xrpqdesnuvnv62",
            "https://live.kuaishou.com/profile/3xzpuhtgptbz4wk",
            "https://live.kuaishou.com/profile/3xhmhwhveezuh5s",
            "https://live.kuaishou.com/profile/3xqmntxfgpu5mj4",
            "https://live.kuaishou.com/profile/3xpq4w66xm3v3si",
            "https://live.kuaishou.com/profile/3xpykz5vfzuwvvc",
            "https://live.kuaishou.com/profile/3xv9si4mtzeis4q",
            "https://live.kuaishou.com/profile/3xj9c7dgtybz4sa",
            "https://live.kuaishou.com/profile/3xncxdk3s6sasmw",
            "https://live.kuaishou.com/profile/3x9xwsrwaishejc",
            "https://live.kuaishou.com/profile/3xkp34ert34djh6",
            "https://live.kuaishou.com/profile/3xr4dnd4n2zazwa",
            "https://live.kuaishou.com/profile/3xnsbzhca84t2bs",
            "https://live.kuaishou.com/profile/3x8ftn8sgq9nd9s",
            "https://live.kuaishou.com/profile/3xa77jxau2xrrue",
            "https://live.kuaishou.com/profile/3xhz3r9mbaz6ctu",
    ]
    for u in user_lis:
        ttt = test.releaser_page_by_time(1556640000000,1574073745559 ,u, output_to_es_raw=True,
                                 es_index='crawler-data-raw',
                                 doc_type='doc',
                                 releaser_page_num_max=200,proxies_num=1)
    #     break
