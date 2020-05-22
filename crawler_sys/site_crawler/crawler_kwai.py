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
from selenium.webdriver.common.proxy import Proxy,ProxyType
from crawler.crawler_sys.framework.video_fields_std import Std_fields_video
from crawler.crawler_sys.utils.output_results import output_result
from crawler.crawler_sys.utils.util_logging import logged
from fontTools.ttLib import *
from crawler.crawler_sys.utils.func_verification_code import Login
try:
    from crawler_sys.framework.func_get_releaser_id import *
except:
    from func_get_releaser_id import *
from crawler.crawler_sys.proxy_pool.func_get_proxy_form_kuaidaili import get_proxy
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from crawler.crawler_sys.utils.trans_str_play_count_to_int import trans_play_count

class Crawler_kwai():

    def __init__(self, timeout=None, platform='kwai'):
        if timeout is None:
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

    # def __del__(self):
    #     try:
    #         self.driver.quit()
    #         os.remove(self.plugin_path)
    #     except:
    #         pass


    def create_proxyauth_extension(self,proxy_host, proxy_port,
                                   proxy_username, proxy_password,
                                   scheme='http', plugin_path=None):
        """Proxy Auth Extension

        args:
            proxy_host (str): domain or ip address, ie proxy.domain.com
            proxy_port (int): port
            proxy_username (str): auth username
            proxy_password (str): auth password
        kwargs:
            scheme (str): proxy scheme, default http
            plugin_path (str): absolute path of the extension

        return str -> plugin_path
        """
        import string
        import zipfile

        if plugin_path is None:
            plugin_path = '/home/hanye/vimm_chrome_proxyauth_plugin_%s.zip' % int(datetime.datetime.now().timestamp()*1e3)

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = string.Template(
                """
                var config = {
                        mode: "fixed_servers",
                        rules: {
                          singleProxy: {
                            scheme: "${scheme}",
                            host: "${host}",
                            port: parseInt(${port})
                          },
                          bypassList: ["foobar.com"]
                        }
                      };
        
                chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        
                function callbackFn(details) {
                    return {
                        authCredentials: {
                            username: "${username}",
                            password: "${password}"
                        }
                    };
                }
        
                chrome.webRequest.onAuthRequired.addListener(
                            callbackFn,
                            {urls: ["<all_urls>"]},
                            ['blocking']
                );
                """
        ).substitute(
                host=proxy_host,
                port=proxy_port,
                username=proxy_username,
                password=proxy_password,
                scheme=scheme,
        )
        with zipfile.ZipFile(plugin_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        self.plugin_path = plugin_path
        return plugin_path

    def get_cookies_and_font(self, releaserUrl):
       # print(releaserUrl)
        self.cookie_dic, self.uni_code_dic = self.get_cookies_and_front(releaserUrl)


    def get_releaser_id(self, releaserUrl):
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
    #         print(self.xml_text)
    #         return False

    def unicode_to_num(self, uni_str):
        count_num = str(uni_str.encode("unicode_escape"))[2:-1]
        # print(count_num)
        for i in self.uni_code_dic:
            if i in count_num:
                count_num = count_num.replace(i, str(self.uni_code_dic[i]))
        # print(count_num)
        return count_num

    #    @logged

    def get_releaser_follower_num(self, releaserUrl):
        count_true = 0
        headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "content-type": "application/json",
                "Referer": releaserUrl,
                "Origin": "https://live.kuaishou.com",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Host": "live.kuaishou.com",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
        }
        while count_true < 5:
            proxies = get_proxy(proxies_num=1)
            self.get_cookies_and_font(releaserUrl)
            releaser_id = self.get_releaser_id(releaserUrl)
            if not releaser_id:
                return None,None
            post_url = 'https://live.kuaishou.com/graphql'
            post_dic = {"operationName":"userInfoQuery","variables":{"principalId":releaser_id},"query":"query userInfoQuery($principalId: String) {\n  userInfo(principalId: $principalId) {\n    id\n    principalId\n    kwaiId\n    eid\n    userId\n    profile\n    name\n    description\n    sex\n    constellation\n    cityName\n    living\n    watchingCount\n    isNew\n    privacy\n    feeds {\n      eid\n      photoId\n      thumbnailUrl\n      timestamp\n      __typename\n    }\n    verifiedStatus {\n      verified\n      description\n      type\n      new\n      __typename\n    }\n    countsInfo {\n      fan\n      follow\n      photo\n      liked\n      open\n      playback\n      private\n      __typename\n    }\n    bannedStatus {\n      banned\n      defriend\n      isolate\n      socialBanned\n      __typename\n    }\n    __typename\n  }\n}\n"}
            try:
                releaser_page = requests.post(post_url, headers=headers, cookies=self.cookie_dic,json=post_dic,proxies=proxies,timeout=2)
            except:
                releaser_page = requests.post(post_url, headers=headers, cookies=self.cookie_dic,
                                              json=post_dic)
            res_dic = releaser_page.json()
            print(res_dic)
            if res_dic.get("errors"):
                self.loginObj.delete_cookies(self.cookie_dic)
            try:
                releaser_follower_num_str =res_dic["data"]["userInfo"]["countsInfo"]["fan"]
                releaser_follower_num = self.re_cal_count(self.unicode_to_num(releaser_follower_num_str))
                print(releaser_follower_num)
                releaser_img = self.get_releaser_image(data=res_dic)
                return releaser_follower_num,releaser_img
            except:
                if count_true == 4:
                    self.loginObj.delete_cookies(self.cookie_dic)
                count_true += 1
        return None,None

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

    @staticmethod
    def get_video_image(data):
        return data.get("poster")

    def releaser_page(self, releaserUrl,
                      output_to_file=False,
                      filepath=None,
                      releaser_page_num_max=30,
                      output_to_es_raw=False,
                      es_index=None,
                      doc_type=None,
                      output_to_es_register=False,
                      push_to_redis=False, proxies_num=None, **kwargs):

        """
        get video info from api instead of web page html
        the most scroll page is 1000
        # """

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
                       "query": "query publicFeedsQuery($principalId: String, $pcursor: String, $count: Int) {\n  publicFeeds(principalId: $principalId, pcursor: $pcursor, count: $count) {\n    pcursor\n    live {\n      user {\n        id\n        avatar\n        name\n        __typename\n      }\n      watchingCount\n      poster\n      coverUrl\n      caption\n      id\n      playUrls {\n        quality\n        url\n        __typename\n      }\n      quality\n      gameInfo {\n        category\n        name\n        pubgSurvival\n        type\n        kingHero\n        __typename\n      }\n      hasRedPack\n      liveGuess\n      expTag\n      __typename\n    }\n    list {\n      id\n      thumbnailUrl\n      poster\n      workType\n      type\n      useVideoPlayer\n      imgUrls\n      imgSizes\n      magicFace\n      musicName\n      caption\n      location\n      liked\n      onlyFollowerCanComment\n      relativeHeight\n      timestamp\n      width\n      height\n      counts {\n        displayView\n        displayLike\n        displayComment\n        __typename\n      }\n      user {\n        id\n        eid\n        name\n        avatar\n        __typename\n      }\n      expTag\n      __typename\n    }\n    __typename\n  }\n}\n"}
            api_url = 'https://live.kuaishou.com/m_graphql'
            if proxies_num:
                proxies = get_proxy(proxies_num)
                get_page = requests.post(api_url, headers=headers, json=url_dic, cookies=self.cookie_dic,
                                         proxies=proxies, timeout=5)
            else:
                get_page = requests.post(api_url, headers=headers, json=url_dic, cookies=self.cookie_dic,timeout=5)
            # print(get_page.content)
            time.sleep(0.5)
            page_dic = get_page.json()
            data_list = page_dic.get("data").get("publicFeeds").get("list")
            # print(data_list)
            if data_list == []:
                print("no more data at releaser: %s page: %s " % (releaser, count))
                retry_time += 1
                if retry_time > 2:
                    pcursor = "no_more"
                if not pcursor:
                    self.loginObj.delete_cookies(self.cookie_dic)
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
                    video_dic['release_time'] = info_dic.get('timestamp')
                    video_dic['releaser'] = info_dic.get('user').get("name")
                    video_dic['play_count'] = trans_play_count(info_dic.get('counts').get("displayView"))
                    video_dic['comment_count'] =trans_play_count(info_dic.get('counts').get("displayComment"))
                    video_dic['favorite_count'] = trans_play_count(info_dic.get('counts').get("displayLike"))
                    video_dic['video_id'] = info_dic.get('id')
                    video_dic['fetch_time'] = int(time.time() * 1e3)
                    video_dic['releaser_id_str'] = "kwai_%s" % (releaser_id)
                    video_dic['releaserUrl'] = 'https://live.kuaishou.com/profile/%s' % releaser_id
                    video_dic['video_img'] = self.get_video_image(info_dic)
                    if video_dic['play_count'] is False or video_dic['comment_count'] is False or video_dic[
                        'favorite_count'] is False:
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
    test = Crawler_kwai()
    url = 'https://live.kuaishou.com/profile/IIloveyoubaby'
    user_lis = [

            "https://live.kuaishou.com/profile/3xk2seyy6u5zgcc",
            "https://live.kuaishou.com/profile/3xyudn6sz9nwksq",
            "https://live.kuaishou.com/profile/3x4g7ckzcvn4avw",
            "https://live.kuaishou.com/profile/newscctv",
            "https://live.kuaishou.com/profile/3x4du3ykwwi6e2e",
            "https://live.kuaishou.com/profile/3xqqcujmyyw2qwu",
            "https://live.kuaishou.com/profile/3xkq27yxyxcbr8a",
            "https://live.kuaishou.com/profile/qhbtv2019",
            "https://live.kuaishou.com/profile/3xrexqmb76zv7sc",
            "https://live.kuaishou.com/profile/3xsew4zi5ujve4i",
            "https://live.kuaishou.com/profile/YANGSHIWANG",
            "https://live.kuaishou.com/profile/QLTV88881234",
            "https://live.kuaishou.com/profile/3xtqwqv33gfjh8c",
            "https://live.kuaishou.com/profile/lizhixinwen"
    ]
    for u in user_lis:
        ttt = test.releaser_page(releaserUrl="https://live.kuaishou.com/profile/3x4g7ckzcvn4avw", output_to_es_raw=True,
                                 es_index='crawler-data-raw',
                                 doc_type='doc',
                                 releaser_page_num_max=10,proxies_num=1)
        test.get_releaser_follower_num(u)
        # break
#    sr_tud = test.search_page(keyword='任正非 BBC', search_pages_max=2)
