# -*- coding:utf-8 -*-
# @Time : 2019/9/12 10:19 

"""
    私密代理使用示例
    接口鉴权说明：
    目前支持的鉴权方式有 "simple" 和 "hmacsha1" 两种，默认使用 "simple"鉴权。
    所有方法均可添加关键字参数sign_type修改鉴权方式。
"""
import redis
import kdl,requests

rds = redis.StrictRedis(host='192.168.17.60', port=6379, db=7)
def get_proxy_from_redis():
    one_proxy = str(rds.randomkey(),encoding="utf-8")
    username = "****"
    password = "******"

    proxies = {
            "http": "http://%(user)s:%(pwd)s@%(ip)s/" % {'user': username, 'pwd': password, 'ip': one_proxy},
            "https": "http://%(user)s:%(pwd)s@%(ip)s/" % {'user': username, 'pwd': password, 'ip': one_proxy}
    }
    return proxies

def func_get_proxy_to_redis():
    auth = kdl.Auth("916825982332963", "evj97414slmqj2h4afcfpq7rpsaixioa")
    client = kdl.Client(auth)

    # 获取订单到期时间, 返回时间字符串
    # expire_time = client.get_order_expire_time()
    # print("expire time", expire_time)

    # 获取ip白名单, 返回ip列表
    # ip_whitelist = client.get_ip_whitelist()
    # print("ip whitelist", ip_whitelist)

    # 设置ip白名单，参数类型为字符串或列表或元组
    # 成功则返回True, 否则抛出异常
    # client.set_ip_whitelist([])
    # client.set_ip_whitelist("127.0.0.1, 192.168.0.139")
    # print(client.get_ip_whitelist())
    # client.set_ip_whitelist(tuple())

    # 提取私密代理ip, 第一个参数为提取的数量, 其他参数以关键字参数的形式传入(不需要传入signature和timestamp)
    # 具体有哪些参数请参考帮助中心: "https://help.kuaidaili.com/api/getdps/"
    # 返回ip列表
    # 注意：若您使用的是python2, 且在终端调用，或在文件中调用且没有加 "# -*- coding: utf-8 -*-" 的话
    # 传入area参数时，请传入unicode类型，如 area=u'北京,上海'
    # ips = client.get_dps(1, sign_type='simple', format='json', pt=2, area='北京,上海,广东')
    # print("dps proxy: ", ips)


    # 检测私密代理有效性： 返回 ip: true/false 组成的dict
    #ips = client.get_dps(1, sign_type='simple', format='json')
    # valids = client.check_dps_valid(ips)
    # print("valids: ", valids)

    # 获取私密代理剩余时间: 返回 ip: seconds(剩余秒数) 组成的dict
    ips = client.get_dps(1, format='json')
    seconds = client.get_dps_valid_time(ips)
    # print("seconds: ", seconds)
    for key in seconds:
        rds.set(key, key, ex=int(seconds[key]) - 3)

    # 获取计数版ip余额（仅私密代理计数版）
    # balance = client.get_ip_balance(sign_type='hmacsha1')
    # print("balance: ", balance)
def proxy_test(proxies):
    page_url = "http://dev.kdlapi.com/testproxy/"
    headers = {
            "Accept-Encoding": "Gzip",  # 使用gzip压缩传输数据让访问更快
    }

    res = requests.get(url=page_url, proxies=proxies, headers=headers)
    # print(res.status_code)  # 获取Reponse的返回码
    if res.status_code == 200:
        print(res.content.decode('utf-8'))  # 获取页面内容

def get_proxy_dic(max_proxies=None):
    if not max_proxies:
        max_proxies = 8
    res = rds.scan()
    if len(res[1]) < max_proxies:
        func_get_proxy_to_redis()
        return get_proxy_from_redis()
    else:
        return get_proxy_from_redis()

def get_proxy(proxies_num=None):
    if proxies_num:
        proxies = get_proxy_dic(max_proxies=proxies_num)
        # print("get a IP %s" % str(proxies))
        return proxies
    else:
        return None

if __name__ == "__main__":
    proxy_pool_dic = get_proxy(1)
    print(proxy_pool_dic)
    proxy_test(proxy_pool_dic)
