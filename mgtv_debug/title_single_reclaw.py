# -*- coding: utf-8 -*-
# author: Scandium
# work_location: CSM Peking
# project : crawler
# time: 2019/12/26 10:00

import os, re, csv, json, traceback

import csv,os
from selenium.webdriver import ActionChains
from selenium import webdriver
import time
import redis,copy

#rds_list = redis.StrictRedis(host='127.0.0.1', port=6379, db=3, decode_responses=True)
rds_single = redis.StrictRedis(host='127.0.0.1', port=6379, db=4, decode_responses=True)

all_need_claw = rds_single.keys()
# video_title = '电子竞技：让李晓峰成为SKY'
#
# single_reclaw_url = rds_single.hgetall(video_title)['video_url']

# url = single_reclaw_url
def more_detail_double_click(driver):
	more_detail = driver.find_elements_by_xpath('/html/body/div[2]/div[2]/div[2]/div[1]/div[2]/a')
	action = ActionChains(driver)
	action.click(more_detail[0]).perform()
	action = ActionChains(driver)
	action.click(more_detail[0]).perform()
	del action

def get_video_data(driver):
	more_detail_double_click(driver)
	time.sleep(0.2)
	list_of_video = driver.find_elements_by_xpath('//*[@class="aside-videolist"]/li/a')
	video_count = len(list_of_video)
	#print(video_count)
	dic_theme = []
	for count in range(video_count):
		print(count)
		more_detail_double_click(driver)
		list_of_video = driver.find_elements_by_xpath('//*[@class="aside-videolist"]/li/a')
		more_detail_double_click(driver)
		time.sleep(0.2)
		action = ActionChains(driver)
		action.click(list_of_video[count-1]).perform()
		time.sleep(0.2)
		more_detail_double_click(driver)
		video_button = driver.find_elements_by_xpath("//*[@id='mgtv-video-wrap']/container/video")
		action = ActionChains(driver)
		action.move_to_element(video_button[0]).perform()
		action.click(video_button[0]).perform()
		#more_detail_double_click(driver)
		time.sleep(0.2)
		duration = driver.find_elements_by_xpath(
			'//*[@id="mgtv-video-wrap"]/container/mango-control/mango-control-wrap/mango-control-wrap-left/mango-progresstime/mango-progresstime-total/mango-progresstime-total-value')
		video_title = driver.find_elements_by_xpath(
			'//*[@class = "v-panel-title"]')
		play_count = driver.find_elements_by_xpath(
			'/html/body/div[2]/div[2]/div[2]/div[1]/span/a/span')
		comment_count = driver.find_elements_by_xpath('//*[@id="mango-comment-wrap"]/div/div[1]/span/em')
		#conment_list = driver.find_elements_by_xpath('//*[@class = "c-comment-cont"]/div/div/p')
		#conment_element_list = driver.find_elements_by_xpath('//*[@class = "comment"]/p/span[3]')
		#conment_list = [element.text for element in conment_element_list]
		video_url = driver.current_url
		like_num = driver.find_elements_by_xpath('/html/body/div[2]/div[2]/div[2]/div[1]/div[8]/div/a[1]/em')
		dic_uni_video = {
			"video_title": web_text_select(video_title),
			"comment_count": web_text_select(comment_count),
			"video_url": video_url,
			"play_count": web_text_select(play_count),
			"duration": web_text_select(duration),
			#"conment_list": conment_list,
			"like_num": web_text_select(like_num)}
		print(web_text_select(video_title),web_text_select(duration))
		dic_theme.append(dic_uni_video)

	return dic_theme

def web_text_select(input_web_object_list):
	if input_web_object_list:
		web_text = input_web_object_list[0]
		return web_text.text
	else:
		return ''

def trans_duration(duration_str):
	"""suitable for 20:20, 20:20:10"""
	if type(duration_str) == int:
		return duration_str
	duration_lst = duration_str.split(':')
	if len(duration_lst) == 3:
		duration = int(int(duration_lst[0]) * 3600 + int(duration_lst[1]) * 60 + int(duration_lst[2]))
		return duration
	elif len(duration_lst) == 2:
		duration = int(int(duration_lst[0]) * 60 + int(duration_lst[1]))
		return duration
	else:
		return duration_lst[0]

def divide_line(weight_length,key_input):
	key_list_length = len(key_input)
	num_code = key_list_length//weight_length
	dic_list_out=[]
	for num in range(num_code):
		dic_nx = list(key_input)[num * weight_length:(num + 1) * weight_length]
		dic_list_out.append(dic_nx)
	dic_final = list(key_input)[num_code * weight_length:]
	dic_list_out.append(dic_final)
	print(num_code+1)
	return dic_list_out

def re_get_title_and_update(list_of_key):
	options = webdriver.ChromeOptions()
	options.add_argument("--start-maximized")
	driver = webdriver.Chrome("C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",chrome_options=options)
	driver.implicitly_wait(10)
	num_done = 0
	for key in  list_of_key:
		redis_data = rds_single.hgetall(key)
		try:
			title = redis_data['title']
			print('title_exist')
		except:
			url = redis_data['video_url']
			driver.get(url)
			time.sleep(0.2)
			try:
				more_detail_double_click(driver)
				title = driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div[1]/div/div[1]/div/div[1]/div/h2/span")
				redis_data['title'] = web_text_select(title)
				rds_single.hmset(key,redis_data)
			except:
				print(404)
				continue
		num_done+=1
		print(num_done,key)
	driver.close()

def dic_title_build_by_url(dic_title_url_vip):
	dic_return = {}
	for dic_key in dic_title_url_vip.items():
		title_theme = dic_key[0]
		url  = dic_key[1][0]
		mid_url_num = url.split('/')[-2]
		dic_return[mid_url_num]= title_theme
	return dic_return

def re_get_title_and_update_by_url(list_of_key):
	options = webdriver.ChromeOptions()
	options.add_argument("--start-maximized")
	driver = webdriver.Chrome("C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",chrome_options=options)
	driver.implicitly_wait(10)
	num_done = 0
	for key in  list_of_key:
		redis_data = rds_single.hgetall(key)
		try:
			title = redis_data['title']
			print('title_exist')
		except:
			url = redis_data['video_url']
			url_middle_element = url.split('/')[-2]
			if url_middle_element in dic_theme_convert_url:
				title_key = dic_theme_convert_url[url_middle_element]
				redis_data['title'] = title_key
				rds_single.hmset(key, redis_data)
				continue
			driver.get(url)
			time.sleep(0.2)
			try:
				more_detail_double_click(driver)
				title = driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div[1]/div/div[1]/div/div[1]/div/h2/span")
				redis_data['title'] = web_text_select(title)
				rds_single.hmset(key,redis_data)
			except:
				print(404)
				continue
		num_done+=1
		print(num_done,key)
	driver.close()

if __name__ == '__main__':

	dic_title_url_vip = {'光鸣岛的秘密花园': ['https://www.mgtv.com/b/334638/7331458.html', 'VIP'],
	                     '澳门故事-我们这20年': ['https://www.mgtv.com/b/335582/7332483.html', ''],
	                     '寻情记 2019': ['https://www.mgtv.com/b/327251/7333148.html', ''],
	                     '澳门“食”光': ['https://www.mgtv.com/b/335252/7331079.html', 'VIP'],
	                     '军情纵览 2019': ['https://www.mgtv.com/b/327255/7331241.html', '预告'],
	                     '创新无边界': ['https://www.mgtv.com/b/335466/7329705.html', ''],
	                     '精彩大揭秘 2019': ['https://www.mgtv.com/b/327443/6431457.html', ''],
	                     '中国澳骄': ['https://www.mgtv.com/b/335199/7315972.html', ''],
	                     '军武次位面 第六季': ['https://www.mgtv.com/b/328844/7295972.html', ''],
	                     '世界看湖南 2019': ['https://www.mgtv.com/b/327252/7314382.html', ''],
	                     '谈心社': ['https://www.mgtv.com/b/331028/7312270.html', ''],
	                     '我的纪录片 2019': ['https://www.mgtv.com/b/327250/7238873.html', ''],
	                     '军武大本营 第三季': ['https://www.mgtv.com/b/324120/7241562.html', ''],
	                     '石榴花开': ['https://www.mgtv.com/b/331928/6992646.html', ''],
	                     '致敬北京中轴线': ['https://www.mgtv.com/b/333854/7177303.html', ''],
	                     '十一书': ['https://www.mgtv.com/b/334515/7170081.html', ''],
	                     '断肠明志铸忠魂': ['https://www.mgtv.com/b/334777/7162099.html', ''],
	                     '三湘巨变微纪录·四十年四十村': ['https://www.mgtv.com/b/325333/4541211.html', ''],
	                     '中国出了个毛泽东·东方欲晓': ['https://www.mgtv.com/b/332066/6501610.html', ''],
	                     '习近平的初心': ['https://www.mgtv.com/b/313543/3873418.html', ''],
	                     '长江黄河如此奔腾—解读共和国70年': ['https://www.mgtv.com/b/333459/7021670.html', ''],
	                     '台北故宫': ['https://www.mgtv.com/b/4730/6785616.html', ''],
	                     '美味趣旅行': ['https://www.mgtv.com/b/109841/1508666.html', ''],
	                     '中国通史': ['https://www.mgtv.com/b/311387/3811611.html', ''],
	                     '故事湖南 2010': ['https://www.mgtv.com/b/303429/3639194.html', ''],
	                     '寻情记 2013': ['https://www.mgtv.com/b/303464/3636500.html', ''],
	                     '习近平治国方略：中国这五年': ['https://www.mgtv.com/b/319434/4163699.html', ''],
	                     '功夫学徒': ['https://www.mgtv.com/b/327583/6981241.html', ''],
	                     '艾问顶级人物': ['https://www.mgtv.com/b/331029/7076264.html', ''],
	                     '华人江湖': ['https://www.mgtv.com/b/327187/4991046.html', ''],
	                     '青年新样貌': ['https://www.mgtv.com/b/333658/6984943.html', ''],
	                     '他们正在改变中国': ['https://www.mgtv.com/b/331897/6432893.html', ''],
	                     '一席 2019': ['https://www.mgtv.com/b/328940/6918273.html', ''],
	                     '我们站立的地方': ['https://www.mgtv.com/b/330887/6366040.html', ''],
	                     '最美中国人': ['https://www.mgtv.com/b/333876/6906724.html', '预告'],
	                     '致敬，北极！': ['https://www.mgtv.com/b/332018/6595851.html', ''],
	                     '狂野动物王国': ['https://www.mgtv.com/b/295036/4055590.html', ''],
	                     '不忘初心 继续前进': ['https://www.mgtv.com/b/318725/4128539.html', ''],
	                     '中国高定设计师': ['https://www.mgtv.com/b/330156/6846677.html', ''],
	                     '国歌': ['https://www.mgtv.com/b/332068/6552286.html', ''],
	                     '寻找手艺': ['https://www.mgtv.com/b/319264/4153090.html', ''],
	                     '世界多美丽 2019': ['https://www.mgtv.com/b/327444/6710782.html', ''],
	                     '我家这三代': ['https://www.mgtv.com/b/332022/6724253.html', ''],
	                     '湖南省第四届网络原创视听节目大赛': ['https://www.mgtv.com/b/329390/6663729.html', ''],
	                     '不负青春不负村 第三季': ['https://www.mgtv.com/b/332141/6738144.html', ''],
	                     '剧说 2019': ['https://www.mgtv.com/b/333410/6718386.html', ''],
	                     '一带一路': ['https://www.mgtv.com/b/312918/3857078.html', ''],
	                     '寻情记 2017': ['https://www.mgtv.com/b/308937/4231652.html', '独播'],
	                     '全民纪录 2018': ['https://www.mgtv.com/b/320755/4805202.html', ''],
	                     '喜迎十九大湖南广播电视台公益宣传片': ['https://www.mgtv.com/b/317162/4150717.html', ''],
	                     '2017湖南广播电视台优秀节目评估参评节目': ['https://www.mgtv.com/b/320039/4228971.html', ''],
	                     '全民纪录 2017': ['https://www.mgtv.com/b/310180/4228771.html', ''],
	                     '指尖上的传承': ['https://www.mgtv.com/b/157333/4294351.html', ''],
	                     '长征': ['https://www.mgtv.com/b/303726/3629617.html', ''],
	                     '芒果美食': ['https://www.mgtv.com/b/151128/3062429.html', ''],
	                     '传家本事': ['https://www.mgtv.com/b/299976/3551811.html', ''],
	                     '初次见 第二季': ['https://www.mgtv.com/b/297362/3366109.html', ''],
	                     '重生': ['https://www.mgtv.com/b/294313/3292323.html', ''],
	                     '致前行者': ['https://www.mgtv.com/b/331517/6601026.html', ''],
	                     '穿行新西兰': ['https://www.mgtv.com/b/293131/3134024.html', ''],
	                     'WE留学生': ['https://www.mgtv.com/b/291716/3040213.html', ''],
	                     '艺术很难吗 第二季': ['https://www.mgtv.com/b/291532/2990850.html', ''],
	                     '韦恩·鲁尼：进球背后的男人': ['https://www.mgtv.com/b/290308/2934807.html', ''],
	                     '保罗·加斯科因': ['https://www.mgtv.com/b/290310/2934809.html', ''],
	                     '贝克汉姆：为挚爱的足球而战': ['https://www.mgtv.com/b/168991/2934649.html', '独播'],
	                     '趣科普 第一季': ['https://www.mgtv.com/b/131360/3912006.html', ''],
	                     '我的中国心': ['https://www.mgtv.com/b/332236/6580448.html', ''],
	                     '寻情记 2016': ['https://www.mgtv.com/b/290610/2940226.html', '独播'],
	                     '我的纪录片 2016': ['https://www.mgtv.com/b/290541/3760677.html', '独播'],
	                     '2017湖南广播电视台优秀节目评估广播类参评节目': ['https://www.mgtv.com/b/320120/4236573.html', ''],
	                     '第五届24格·创意媒体嘉年华': ['https://www.mgtv.com/b/323170/4377205.html', ''],
	                     '箭厂视频 2018': ['https://www.mgtv.com/b/323053/4840421.html', ''],
	                     '兴乡计 第一季': ['https://www.mgtv.com/b/322932/4320393.html', ''],
	                     '可爱的中国 第二季': ['https://www.mgtv.com/b/332123/6574421.html', ''],
	                     '太极中国': ['https://www.mgtv.com/b/322750/4310414.html', ''],
	                     '当家菜 2018': ['https://www.mgtv.com/b/322647/4400683.html', ''],
	                     '海外学者看中国': ['https://www.mgtv.com/b/322517/4293156.html', ''],
	                     '千年非遗': ['https://www.mgtv.com/b/322513/4293173.html', ''],
	                     '时代中国': ['https://www.mgtv.com/b/322514/4293157.html', ''],
	                     '旅食家 2018': ['https://www.mgtv.com/b/322488/4318679.html', ''],
	                     '碧血祭长空': ['https://www.mgtv.com/b/322482/4290208.html', ''],
	                     '我的青春在丝路 第一季': ['https://www.mgtv.com/b/322478/4296311.html', '独播'],
	                     '拜见掌门人': ['https://www.mgtv.com/b/322418/4284484.html', '预告'],
	                     '舌尖上的全球美食': ['https://www.mgtv.com/b/322384/4284908.html', ''],
	                     '味道云南': ['https://www.mgtv.com/b/322381/4285242.html', ''],
	                     '时尚台前幕后的故事': ['https://www.mgtv.com/b/322277/4275868.html', ''],
	                     '万物滋养': ['https://www.mgtv.com/b/322101/4265507.html', ''],
	                     '世界多美丽 2018': ['https://www.mgtv.com/b/322075/4776901.html', ''],
	                     '祖国在召唤': ['https://www.mgtv.com/b/332413/6576527.html', ''],
	                     '2017湖南广播电视台优秀节目评估节目精选': ['https://www.mgtv.com/b/321348/4239512.html', ''],
	                     '美食三分钟 2018': ['https://www.mgtv.com/b/320753/4399934.html', ''],
	                     '看鉴地理 2018': ['https://www.mgtv.com/b/320752/4318678.html', ''],
	                     '我的纪录片 2018': ['https://www.mgtv.com/b/320637/4753808.html', '独播'],
	                     '世界看湖南 2018': ['https://www.mgtv.com/b/320635/4878330.html', ''],
	                     '寻情记 2018': ['https://www.mgtv.com/b/320632/4906002.html', '独播'],
	                     '寻找英雄儿女·百名法官': ['https://www.mgtv.com/b/319980/4192247.html', ''],
	                     '西藏时光': ['https://www.mgtv.com/b/319955/4195471.html', ''],
	                     '雷佳民族民间音乐会纪实': ['https://www.mgtv.com/b/319936/4189851.html', ''],
	                     '精彩大揭秘 2017': ['https://www.mgtv.com/b/312435/4219901.html', ''],
	                     '军武大本营 第二季': ['https://www.mgtv.com/b/319766/4386080.html', ''],
	                     '日出之食': ['https://www.mgtv.com/b/319732/4193549.html', ''],
	                     '医院里的故事': ['https://www.mgtv.com/b/319726/4293165.html', ''],
	                     '光阴的故事-中越情谊': ['https://www.mgtv.com/b/319517/4170059.html', ''],
	                     '军事编辑部-战史科': ['https://www.mgtv.com/b/319633/4331228.html', ''],
	                     '军事编辑部-武研社': ['https://www.mgtv.com/b/319632/4331291.html', ''],
	                     '中国表情': ['https://www.mgtv.com/b/319308/4186058.html', ''],
	                     '爱上中国': ['https://www.mgtv.com/b/319152/4147246.html', ''],
	                     '中国梦展播作品 剧情类': ['https://www.mgtv.com/b/318706/4124316.html', ''],
	                     '创新中国 第一季': ['https://www.mgtv.com/b/318832/4235650.html', ''],
	                     '中国梦展播作品 非剧情类': ['https://www.mgtv.com/b/318707/4128470.html', ''],
	                     '社会主义核心价值观主题微电影征集展示活动': ['https://www.mgtv.com/b/318716/4144008.html', ''],
	                     '扶贫纪事': ['https://www.mgtv.com/b/318726/4125986.html', ''],
	                     '强军': ['https://www.mgtv.com/b/318691/4125923.html', ''],
	                     '法观大宝鉴': ['https://www.mgtv.com/b/318650/4119714.html', ''],
	                     '辉煌中国': ['https://www.mgtv.com/b/318340/4110471.html', ''],
	                     '巡视利剑': ['https://www.mgtv.com/b/318067/4095491.html', ''],
	                     '小镇微光': ['https://www.mgtv.com/b/329229/5475881.html', ''],
	                     '大国外交': ['https://www.mgtv.com/b/317827/4080654.html', ''],
	                     '未来生活家': ['https://www.mgtv.com/b/317564/4183946.html', ''],
	                     '了不起我的国 2017': ['https://www.mgtv.com/b/317547/4228916.html', ''],
	                     '快乐向膳': ['https://www.mgtv.com/b/317284/4083950.html', ''],
	                     '这里是西藏': ['https://www.mgtv.com/b/317207/4044948.html', ''],
	                     '武器大讲堂': ['https://www.mgtv.com/b/317127/4053263.html', ''],
	                     '永不失散': ['https://www.mgtv.com/b/316978/4044087.html', ''],
	                     '匠仓': ['https://www.mgtv.com/b/316757/4485412.html', ''],
	                     '建军90周年微讲述': ['https://www.mgtv.com/b/316656/4067009.html', ''],
	                     '吃货集市': ['https://www.mgtv.com/b/316519/4099953.html', ''],
	                     '未视频 2017': ['https://www.mgtv.com/b/316463/4241150.html', ''],
	                     '旅食家 2017': ['https://www.mgtv.com/b/307623/4284648.html', ''],
	                     '美食中国 2017': ['https://www.mgtv.com/b/293540/4244655.html', ''],
	                     'BBC精选': ['https://www.mgtv.com/b/292096/4230066.html', ''],
	                     '看鉴地理 2017': ['https://www.mgtv.com/b/312441/4223831.html', ''],
	                     '军武次位面 第四季': ['https://www.mgtv.com/b/313091/4297345.html', ''],
	                     '美食三分钟 2017': ['https://www.mgtv.com/b/312680/4167194.html', ''],
	                     '湘西': ['https://www.mgtv.com/b/313969/4140176.html', ''],
	                     '舌尖上的承德': ['https://www.mgtv.com/b/316349/3994413.html', ''],
	                     '20年·香港正青春': ['https://www.mgtv.com/b/316332/3995299.html', ''],
	                     '厨法': ['https://www.mgtv.com/b/313927/4138890.html', ''],
	                     '遇见·行走的柠檬': ['https://www.mgtv.com/b/316213/3984606.html', '预告'],
	                     '当家菜': ['https://www.mgtv.com/b/313928/4217581.html', ''],
	                     '光阴的故事-中哈友好': ['https://www.mgtv.com/b/316037/3971646.html', ''],
	                     '看鉴 2017': ['https://www.mgtv.com/b/310229/4229880.html', ''],
	                     '创业家·至美季': ['https://www.mgtv.com/b/315637/4000384.html', ''],
	                     '湖南省第二届网络原创视听节目大赛（网络剧网络电影）': ['https://www.mgtv.com/b/314454/3976756.html', ''],
	                     '湖南省第二届网络原创视听节目大赛（大学生原创作品）': ['https://www.mgtv.com/b/314453/3972596.html', ''],
	                     '湖南省第二届网络原创视听节目大赛（网络视听）': ['https://www.mgtv.com/b/314455/3972602.html', ''],
	                     '趣科普 第二季': ['https://www.mgtv.com/b/315158/3936219.html', ''],
	                     '丁点真相 2017': ['https://www.mgtv.com/b/315139/3926955.html', ''],
	                     '国之利器': ['https://www.mgtv.com/b/314791/3913305.html', ''],
	                     '箭厂视频 2017': ['https://www.mgtv.com/b/314178/4114482.html', ''],
	                     '初次见 第三季': ['https://www.mgtv.com/b/313557/3912369.html', ''],
	                     '宁夏味道': ['https://www.mgtv.com/b/313845/3883086.html', '预告'],
	                     '茶有喝过才能说': ['https://www.mgtv.com/b/301449/4064596.html', ''],
	                     '加油男孩': ['https://www.mgtv.com/b/311199/3795965.html', ''],
	                     '社会主义价值观主题微电影': ['https://www.mgtv.com/b/304990/3657731.html', ''],
	                     '海洋之星': ['https://www.mgtv.com/b/308902/3791927.html', ''],
	                     '味道中山': ['https://www.mgtv.com/b/310637/3779817.html', ''],
	                     '老城新味道': ['https://www.mgtv.com/b/310627/3775218.html', '预告'],
	                     '看鉴 2016': ['https://www.mgtv.com/b/303362/3623830.html', ''],
	                     '全民纪录 2016': ['https://www.mgtv.com/b/294488/3765496.html', ''],
	                     '潜行天下 2017': ['https://www.mgtv.com/b/308900/3732678.html', ''],
	                     '潜女郎来啦': ['https://www.mgtv.com/b/308903/3793386.html', ''],
	                     '初次见 第一季': ['https://www.mgtv.com/b/308678/3724188.html', ''],
	                     '艺术很难吗 第四季': ['https://www.mgtv.com/b/313984/4119084.html', ''],
	                     '我来自西藏': ['https://www.mgtv.com/b/304964/3657108.html', ''],
	                     '未视频 2016': ['https://www.mgtv.com/b/293569/3189761.html', ''],
	                     '湖南省首届原创网络视听节目大赛（公益类视听节目）': ['https://www.mgtv.com/b/294080/3274808.html', ''],
	                     '湖南省首届原创网络视听节目大赛（微电影作品）': ['https://www.mgtv.com/b/294079/3281733.html', ''],
	                     '湖南省首届原创网络视听节目大赛（网络专题节目）': ['https://www.mgtv.com/b/294081/3309385.html', ''],
	                     '聊“天”': ['https://www.mgtv.com/b/294031/3272821.html', ''],
	                     '爸爸的木匠小屋': ['https://www.mgtv.com/b/293970/3266572.html', ''],
	                     '服装里的中国 第二季': ['https://www.mgtv.com/b/291478/3094602.html', ''],
	                     '艺术观察': ['https://www.mgtv.com/b/291130/2990985.html', ''],
	                     '我在故宫修文物': ['https://www.mgtv.com/b/290949/2950099.html', ''],
	                     '故事湖南 2017': ['https://www.mgtv.com/b/311803/3852826.html', '独播'],
	                     'WePeople我的2016': ['https://www.mgtv.com/b/311562/3809967.html', ''],
	                     '直播天使': ['https://www.mgtv.com/b/310801/3783954.html', ''],
	                     '世界看湖南 2017': ['https://www.mgtv.com/b/310172/4229288.html', ''],
	                     '世界多美丽 2017': ['https://www.mgtv.com/b/310149/4227685.html', ''],
	                     '童年画语': ['https://www.mgtv.com/b/310141/3771522.html', ''],
	                     '我们走在大路上': ['https://www.mgtv.com/b/331833/6485697.html', ''],
	                     '宁夏故事': ['https://www.mgtv.com/b/331758/6400350.html', ''],
	                     '我的国学之夏': ['https://www.mgtv.com/b/309985/3762276.html', ''],
	                     '我的纪录片 2017': ['https://www.mgtv.com/b/309730/4192321.html', '独播'],
	                     '青春中国 2017': ['https://www.mgtv.com/b/309470/4231051.html', '独播'],
	                     '留学说': ['https://www.mgtv.com/b/308408/3714516.html', ''],
	                     '胡杨传奇': ['https://www.mgtv.com/b/307102/3695544.html', ''],
	                     'WePeople生而为媒': ['https://www.mgtv.com/b/306808/3685897.html', ''],
	                     '意外之美': ['https://www.mgtv.com/b/306475/4056078.html', ''],
	                     '无悔的青春': ['https://www.mgtv.com/b/305566/3664958.html', ''],
	                     '小睿必达': ['https://www.mgtv.com/b/305564/3664956.html', ''],
	                     '承诺': ['https://www.mgtv.com/b/305537/3664593.html', ''],
	                     '传家微记录': ['https://www.mgtv.com/b/305469/3666205.html', ''],
	                     '让候鸟飞': ['https://www.mgtv.com/b/305362/3661299.html', ''],
	                     '大山里的坚守': ['https://www.mgtv.com/b/304967/3657175.html', ''],
	                     '永远的长征': ['https://www.mgtv.com/b/304604/3652718.html', ''],
	                     '服装里的中国 第一季': ['https://www.mgtv.com/b/166194/1822119.html', ''],
	                     '70年70企70人': ['https://www.mgtv.com/b/329982/6400667.html', ''],
	                     '寻情记 2015': ['https://www.mgtv.com/b/304164/3637391.html', '独播'],
	                     '永远在路上': ['https://www.mgtv.com/b/303800/3630568.html', ''],
	                     '时代更美好': ['https://www.mgtv.com/b/330788/6153622.html', ''],
	                     '世界看湖南 2016': ['https://www.mgtv.com/b/303375/3749513.html', ''],
	                     '那时那你': ['https://www.mgtv.com/b/297209/3363958.html', ''],
	                     '中共六大纪事': ['https://www.mgtv.com/b/294495/3300624.html', ''],
	                     '青春之约': ['https://www.mgtv.com/b/294082/3274813.html', ''],
	                     '不药讲堂': ['https://www.mgtv.com/b/294003/3267737.html', ''],
	                     '光阴的故事': ['https://www.mgtv.com/b/293114/3131064.html', ''],
	                     '艺术很难吗 第三季': ['https://www.mgtv.com/b/292331/3617262.html', ''],
	                     '青春中国 2016': ['https://www.mgtv.com/b/291789/3763653.html', '独播'],
	                     '艺术很难吗 第一季': ['https://www.mgtv.com/b/291273/2970689.html', ''],
	                     '微小计划': ['https://www.mgtv.com/b/291027/2963205.html', ''],
	                     '路过零点 第二季': ['https://www.mgtv.com/b/331195/6397642.html', 'VIP'],
	                     '日出之食 第二季': ['https://www.mgtv.com/b/328368/5144803.html', ''],
	                     '我的纪录片 2015': ['https://www.mgtv.com/b/104866/2936695.html', ''],
	                     '我的纪录片 2014': ['https://www.mgtv.com/b/46093/3634800.html', ''],
	                     '迁徙的人生': ['https://www.mgtv.com/b/331746/6389490.html', ''],
	                     'MUZI看世界 2018': ['https://www.mgtv.com/b/321883/4885036.html', ''],
	                     '川味 第一季': ['https://www.mgtv.com/b/328076/4958206.html', ''],
	                     '木棉说演讲': ['https://www.mgtv.com/b/331324/6272554.html', ''],
	                     '神秘的西夏': ['https://www.mgtv.com/b/109096/1125611.html', ''],
	                     '对望-丝路新旅程': ['https://www.mgtv.com/b/159253/1797735.html', ''],
	                     '辣椒的味道': ['https://www.mgtv.com/b/158521/3044953.html', '独播'],
	                     '我们的偶像': ['https://www.mgtv.com/b/157796/3610197.html', ''],
	                     '美丽乡村': ['https://www.mgtv.com/b/310635/3777839.html', ''],
	                     '超级工程 第一季': ['https://www.mgtv.com/b/317322/4050189.html', ''],
	                     '秘境广西': ['https://www.mgtv.com/b/318026/4103218.html', ''],
	                     '看鉴 2018': ['https://www.mgtv.com/b/320630/4863055.html', ''],
	                     '了不起我的国 2018': ['https://www.mgtv.com/b/322077/4236856.html', ''],
	                     '迷彩虎军情 2018': ['https://www.mgtv.com/b/320749/4914470.html', ''],
	                     '贺兰山': ['https://www.mgtv.com/b/322489/4291403.html', ''],
	                     '解密紫禁城': ['https://www.mgtv.com/b/322490/4291409.html', ''],
	                     '隐秘战士': ['https://www.mgtv.com/b/322498/4293170.html', ''],
	                     '茶马古道': ['https://www.mgtv.com/b/9382/4294350.html', ''],
	                     '迷彩虎讲堂 2018': ['https://www.mgtv.com/b/320751/4888451.html', ''],
	                     '五十军朝鲜战记': ['https://www.mgtv.com/b/322519/4294646.html', ''],
	                     '朝鲜空战记忆': ['https://www.mgtv.com/b/322518/4294647.html', ''],
	                     '洱海渔鹰': ['https://www.mgtv.com/b/322522/4294848.html', ''],
	                     '黄山短尾猴': ['https://www.mgtv.com/b/322516/4294849.html', ''],
	                     '军武次位面 第五季': ['https://www.mgtv.com/b/322611/5331543.html', ''],
	                     '新兵': ['https://www.mgtv.com/b/322983/4336354.html', ''],
	                     '寒冷的高山有犀牛': ['https://www.mgtv.com/b/323238/4336685.html', ''],
	                     '留学的生活': ['https://www.mgtv.com/b/323264/4360635.html', ''],
	                     '2018年“弘扬社会主义核心价值观共筑中国梦”主题原创网络视听节目': ['https://www.mgtv.com/b/323366/4704287.html', ''],
	                     '我爱你，中国 第一季': ['https://www.mgtv.com/b/323385/4370477.html', '独播'],
	                     '芒果小大使 2018': ['https://www.mgtv.com/b/323866/4718298.html', ''],
	                     '奇人奇事 2018': ['https://www.mgtv.com/b/323715/4805440.html', ''],
	                     '谁能不一般': ['https://www.mgtv.com/b/324060/4468119.html', ''],
	                     '湖南省第三届网络原创视听节目大赛（网络剧、网络电影）': ['https://www.mgtv.com/b/324119/4604674.html', ''],
	                     '川流不息': ['https://www.mgtv.com/b/324122/4392049.html', ''],
	                     '小路三分钟': ['https://www.mgtv.com/b/324106/4436743.html', ''],
	                     '中国有瑜伽': ['https://www.mgtv.com/b/324426/4592869.html', ''],
	                     '美食坊': ['https://www.mgtv.com/b/324282/4486480.html', ''],
	                     '盘点委员': ['https://www.mgtv.com/b/324605/4420689.html', ''],
	                     '第三届新湖南微视频大赛': ['https://www.mgtv.com/b/324855/4664229.html', ''],
	                     '赶考路上': ['https://www.mgtv.com/b/324965/4455577.html', ''],
	                     '这条路 My Way 第1季': ['https://www.mgtv.com/b/325046/4448011.html', ''],
	                     '喜马拉雅天梯 电影版': ['https://www.mgtv.com/b/324840/4450518.html', ''],
	                     '奇趣大本营 2018': ['https://www.mgtv.com/b/325288/4750258.html', ''],
	                     '好人·家': ['https://www.mgtv.com/b/325295/4524636.html', ''],
	                     '筑梦者姚明2：光芒': ['https://www.mgtv.com/b/325395/4482106.html', ''],
	                     '功食道': ['https://www.mgtv.com/b/325403/4499181.html', ''],
	                     '我爱你，中国 第二季': ['https://www.mgtv.com/b/325344/4495448.html', '独播'],
	                     '青春中国': ['https://www.mgtv.com/b/325512/4492555.html', ''],
	                     '我的青春在丝路 八月季': ['https://www.mgtv.com/b/325343/4519313.html', ''],
	                     '2018中国梦展播作品 非剧情类': ['https://www.mgtv.com/b/325639/4508409.html', ''],
	                     '2018中国梦展播作品 剧情类': ['https://www.mgtv.com/b/325637/4510500.html', ''],
	                     '中国留学生的四十年': ['https://www.mgtv.com/b/325685/4512574.html', ''],
	                     '我爱你，中国 国庆特辑': ['https://www.mgtv.com/b/325781/4586368.html', ''],
	                     '觅足': ['https://www.mgtv.com/b/325831/4533317.html', ''],
	                     '茶界中国': ['https://www.mgtv.com/b/325916/4544347.html', ''],
	                     '永不停转的车轮': ['https://www.mgtv.com/b/325941/4546127.html', ''],
	                     '13次生还': ['https://www.mgtv.com/b/326084/4559945.html', ''],
	                     '传世匠心': ['https://www.mgtv.com/b/326331/4581492.html', ''],
	                     '揭秘西夏陵': ['https://www.mgtv.com/b/326335/4581546.html', ''],
	                     '从秦始皇到汉武帝': ['https://www.mgtv.com/b/313329/4581693.html', ''],
	                     '玄奘之路': ['https://www.mgtv.com/b/9329/4581703.html', ''],
	                     '传家本事 第二季': ['https://www.mgtv.com/b/326471/4604889.html', 'VIP'],
	                     '湖南省第三届网络原创视听节目大赛（大学生原创作品）': ['https://www.mgtv.com/b/326524/4601231.html', ''],
	                     '我们的谭嗣同': ['https://www.mgtv.com/b/326528/4606458.html', ''],
	                     '湖南省第三届网络原创视听节目大赛（网络视听专业类节目）': ['https://www.mgtv.com/b/326523/4796797.html', ''],
	                     '2018年中国湖南国际旅游节开幕式暨湖南瓷旅之夜': ['https://www.mgtv.com/b/326678/4624251.html', ''],
	                     '极致中国': ['https://www.mgtv.com/b/326755/4643312.html', ''],
	                     '不负青春不负村': ['https://www.mgtv.com/b/326749/4666054.html', ''],
	                     '艺术很难吗 第五季': ['https://www.mgtv.com/b/326801/4881539.html', ''],
	                     '在那遥远的地方': ['https://www.mgtv.com/b/326525/4679036.html', ''],
	                     '我的青春在丝路 第三季': ['https://www.mgtv.com/b/329081/5432409.html', ''],
	                     '四十不惑': ['https://www.mgtv.com/b/327663/4858545.html', ''],
	                     '必由之路': ['https://www.mgtv.com/b/327478/4809306.html', ''],
	                     '亚洲公益影像库系列': ['https://www.mgtv.com/b/330131/6219198.html', ''],
	                     '艺术很难吗之壹公里': ['https://www.mgtv.com/b/331125/6202111.html', ''],
	                     '海上丝绸之路': ['https://www.mgtv.com/b/330467/5985899.html', ''],
	                     '可爱的中国 第一季': ['https://www.mgtv.com/b/330277/5909697.html', ''],
	                     '我在中国做生意': ['https://www.mgtv.com/b/52522/663871.html', ''],
	                     '湖湘讲堂': ['https://www.mgtv.com/b/549/45280.html', ''],
	                     '后会有期': ['https://www.mgtv.com/b/330876/6103938.html', 'VIP'],
	                     '湘江': ['https://www.mgtv.com/b/239/9460.html', ''],
	                     '湘怀天下': ['https://www.mgtv.com/b/167564/2966046.html', ''],
	                     '我的一年级 大学季': ['https://www.mgtv.com/b/166786/2952346.html', '独播'],
	                     '青春中国 2015': ['https://www.mgtv.com/b/304400/3642880.html', ''],
	                     '故事湖南 2015': ['https://www.mgtv.com/b/303436/3639813.html', ''],
	                     '故事湖南 2016': ['https://www.mgtv.com/b/290543/3623539.html', ''],
	                     '寻情记 2014': ['https://www.mgtv.com/b/303465/3636175.html', ''],
	                     '湘当韵味 2016': ['https://www.mgtv.com/b/304685/3653554.html', ''],
	                     '湘当韵味 2015': ['https://www.mgtv.com/b/304683/3653532.html', ''],
	                     '世界看湖南 2015': ['https://www.mgtv.com/b/303455/3629309.html', ''],
	                     '消防安全宣传': ['https://www.mgtv.com/b/330968/6148574.html', ''],
	                     '故事湖南 2009': ['https://www.mgtv.com/b/303428/3638442.html', ''],
	                     '世界看湖南 2012': ['https://www.mgtv.com/b/303451/3625496.html', ''],
	                     '世界看湖南 2013': ['https://www.mgtv.com/b/303452/3625535.html', ''],
	                     '赢家大讲堂': ['https://www.mgtv.com/b/4741/362706.html', ''],
	                     '人间正道是沧桑': ['https://www.mgtv.com/b/328436/5247143.html', ''],
	                     '世界看湖南2014': ['https://www.mgtv.com/b/303454/3629277.html', ''],
	                     '世界看湖南 2011': ['https://www.mgtv.com/b/303450/3625426.html', ''],
	                     '思想的力量': ['https://www.mgtv.com/b/4030/338686.html', ''],
	                     '乡村教师公益微视频': ['https://www.mgtv.com/b/50870/628907.html', ''],
	                     '故事湖南 2011': ['https://www.mgtv.com/b/303430/3639066.html', ''],
	                     '故事湖南 2012': ['https://www.mgtv.com/b/303431/3639214.html', ''],
	                     '我的中国梦': ['https://www.mgtv.com/b/5763/496532.html', ''],
	                     '道德的力量': ['https://www.mgtv.com/b/44799/523110.html', ''],
	                     '故事湖南 2008': ['https://www.mgtv.com/b/303427/3637607.html', ''],
	                     '故事湖南 2013': ['https://www.mgtv.com/b/303434/3639297.html', ''],
	                     '故事湖南 2014': ['https://www.mgtv.com/b/303433/3639419.html', ''],
	                     '野生救援协会公益视频': ['https://www.mgtv.com/b/101476/1080553.html', ''],
	                     '身边好人': ['https://www.mgtv.com/b/3344/335450.html', ''],
	                     '辛亥青春祭': ['https://www.mgtv.com/b/2350/208536.html', ''],
	                     '中国工农红军': ['https://www.mgtv.com/b/48721/588090.html', ''],
	                     '一线造梦人·特殊职业': ['https://www.mgtv.com/b/329422/5947470.html', ''],
	                     '我最亲爱的': ['https://www.mgtv.com/b/109840/1706815.html', ''],
	                     '歌手背后的故事': ['https://www.mgtv.com/b/5761/401700.html', ''],
	                     '吐鲁番传奇': ['https://www.mgtv.com/b/2599/228351.html', ''],
	                     '青春放歌': ['https://www.mgtv.com/b/2239/201787.html', ''],
	                     '那年七月': ['https://www.mgtv.com/b/1345/110859.html', ''],
	                     '微型萌宠大本营': ['https://www.mgtv.com/b/168612/2963216.html', '预告'],
	                     '箭厂视频 2019': ['https://www.mgtv.com/b/327447/5758768.html', ''],
	                     '乡村教师公益微视频征集': ['https://www.mgtv.com/b/42964/496869.html', '预告'],
	                     '善之映画': ['https://www.mgtv.com/b/57008/2994956.html', ''],
	                     '我热爱的生活': ['https://www.mgtv.com/b/330682/6065484.html', ''],
	                     'MUZI看世界 2019': ['https://www.mgtv.com/b/327445/6085363.html', ''],
	                     '暖茶': ['https://www.mgtv.com/b/166098/1814987.html', ''],
	                     '新龙的温度': ['https://www.mgtv.com/b/159463/1802528.html', ''],
	                     '2015大学生公益视频大赛': ['https://www.mgtv.com/b/150153/1766528.html', ''],
	                     '活出个味来': ['https://www.mgtv.com/b/109851/2938048.html', ''],
	                     '湘当韵味 2013': ['https://www.mgtv.com/b/304681/3653496.html', ''],
	                     '湘当韵味 2014': ['https://www.mgtv.com/b/304682/3653559.html', ''],
	                     '看中国': ['https://www.mgtv.com/b/52518/663825.html', ''],
	                     '丁点真相': ['https://www.mgtv.com/b/50058/1010252.html', ''],
	                     '湘江蝶变': ['https://www.mgtv.com/b/4362/343379.html', ''],
	                     '洞庭': ['https://www.mgtv.com/b/4031/339015.html', ''],
	                     '千年菩提路': ['https://www.mgtv.com/b/3998/332409.html', ''],
	                     '毛泽东遗物的故事': ['https://www.mgtv.com/b/2505/223013.html', ''],
	                     '越界': ['https://www.mgtv.com/b/166142/1815098.html', ''],
	                     '寻梦': ['https://www.mgtv.com/b/166143/1815099.html', ''],
	                     '一米阳光': ['https://www.mgtv.com/b/166140/1815096.html', ''],
	                     '长大了我们都嫁给你': ['https://www.mgtv.com/b/166141/1815097.html', ''],
	                     '钟爱': ['https://www.mgtv.com/b/166138/1815094.html', ''],
	                     '警花路放': ['https://www.mgtv.com/b/166139/1815095.html', ''],
	                     '梦圆山城村': ['https://www.mgtv.com/b/166137/1815092.html', ''],
	                     '云知道': ['https://www.mgtv.com/b/166136/1815091.html', ''],
	                     '尽瘁': ['https://www.mgtv.com/b/166135/1815088.html', ''],
	                     '小梅花': ['https://www.mgtv.com/b/166134/1815087.html', ''],
	                     '幸福终点站': ['https://www.mgtv.com/b/166132/1815084.html', ''],
	                     '严复：天演先声': ['https://www.mgtv.com/b/166133/1815086.html', ''],
	                     '煮笛': ['https://www.mgtv.com/b/166130/1815081.html', ''],
	                     '开包子铺的爸爸': ['https://www.mgtv.com/b/166131/1815083.html', ''],
	                     '掌心痣': ['https://www.mgtv.com/b/166127/1815075.html', ''],
	                     '较量': ['https://www.mgtv.com/b/166128/1815079.html', ''],
	                     '霾没了': ['https://www.mgtv.com/b/166125/1815065.html', ''],
	                     '心翼': ['https://www.mgtv.com/b/166124/1815059.html', ''],
	                     '小水井': ['https://www.mgtv.com/b/166123/1815058.html', ''],
	                     '理发师': ['https://www.mgtv.com/b/166122/1815057.html', ''],
	                     '梦想进行时': ['https://www.mgtv.com/b/166121/1815056.html', ''],
	                     '胡友义的钢琴天堂': ['https://www.mgtv.com/b/166120/1815055.html', ''],
	                     '留守儿童的妈妈': ['https://www.mgtv.com/b/166118/1815053.html', ''],
	                     '索玛海子': ['https://www.mgtv.com/b/166116/1815048.html', ''],
	                     '孤岛离歌': ['https://www.mgtv.com/b/166117/1815052.html', ''],
	                     '黄君奕住厦鼓甘露': ['https://www.mgtv.com/b/166115/1815033.html', ''],
	                     '真实': ['https://www.mgtv.com/b/166114/1815032.html', ''],
	                     '给力天使': ['https://www.mgtv.com/b/166111/1815025.html', ''],
	                     '父亲的小黄鸭': ['https://www.mgtv.com/b/166112/1815026.html', ''],
	                     '梦巴士': ['https://www.mgtv.com/b/166110/1815023.html', ''],
	                     '我有你': ['https://www.mgtv.com/b/166108/1815017.html', ''],
	                     '向阳生长': ['https://www.mgtv.com/b/166107/1815015.html', ''],
	                     '微校': ['https://www.mgtv.com/b/166104/1815001.html', ''],
	                     '情有独钟': ['https://www.mgtv.com/b/166102/1814999.html', ''],
	                     '春泥': ['https://www.mgtv.com/b/166101/1814998.html', ''],
	                     '素心': ['https://www.mgtv.com/b/166100/1814992.html', ''],
	                     '阿尼帕和她的小丑丑': ['https://www.mgtv.com/b/166097/1814985.html', ''],
	                     '6号赛车': ['https://www.mgtv.com/b/166096/1814982.html', ''],
	                     '别让爱忙音': ['https://www.mgtv.com/b/166095/1814981.html', ''],
	                     '51把钥匙': ['https://www.mgtv.com/b/166094/1814979.html', ''],
	                     '儿子的信': ['https://www.mgtv.com/b/166093/1814976.html', ''],
	                     '父亲的草原': ['https://www.mgtv.com/b/166092/1814974.html', ''],
	                     '不该屏蔽的爱': ['https://www.mgtv.com/b/166091/1814963.html', ''],
	                     '迫在眉睫': ['https://www.mgtv.com/b/166039/1811994.html', ''],
	                     '那片海': ['https://www.mgtv.com/b/166032/1811933.html', ''],
	                     '爷爷的小戏文': ['https://www.mgtv.com/b/166033/1811934.html', ''],
	                     '对鸟': ['https://www.mgtv.com/b/166031/1811930.html', ''],
	                     '家长会': ['https://www.mgtv.com/b/166029/1811924.html', ''],
	                     '心灵造口师': ['https://www.mgtv.com/b/166030/1811925.html', ''],
	                     '锤钉兄弟': ['https://www.mgtv.com/b/166028/1811915.html', ''],
	                     '这些年一路有你': ['https://www.mgtv.com/b/166027/1811910.html', ''],
	                     '乡村教师': ['https://www.mgtv.com/b/166025/1811903.html', ''],
	                     '真相': ['https://www.mgtv.com/b/52609/1802532.html', ''],
	                     '只要努力就能改变': ['https://www.mgtv.com/b/159471/1802623.html', ''],
	                     '遇见你': ['https://www.mgtv.com/b/159465/1802530.html', ''],
	                     '新视觉：手艺新生': ['https://www.mgtv.com/b/159464/1802529.html', ''],
	                     '草根的喜剧': ['https://www.mgtv.com/b/159459/1802458.html', ''],
	                     '逆光': ['https://www.mgtv.com/b/159458/1802453.html', ''],
	                     '北京的哥自述感人心路': ['https://www.mgtv.com/b/159457/1802438.html', ''],
	                     '赋木天工': ['https://www.mgtv.com/b/159456/1802437.html', ''],
	                     '拾荒主席': ['https://www.mgtv.com/b/159455/1802436.html', ''],
	                     '微视界': ['https://www.mgtv.com/b/159451/1802428.html', ''],
	                     '我的爱人': ['https://www.mgtv.com/b/159450/1802425.html', ''],
	                     '阿达么么哒': ['https://www.mgtv.com/b/159449/1802414.html', ''],
	                     '寻找湖南抗战记忆': ['https://www.mgtv.com/b/158394/1766706.html', ''],
	                     '展璞计划': ['https://www.mgtv.com/b/105030/1077223.html', ''],
	                     '芒果小大使 2019': ['https://www.mgtv.com/b/330518/6009108.html', ''],
	                     '星空日记': ['https://www.mgtv.com/b/101106/1017537.html', ''],
	                     '青春季': ['https://www.mgtv.com/b/100992/1015429.html', ''],
	                     '爱的守望': ['https://www.mgtv.com/b/100988/1015371.html', ''],
	                     '我在中国': ['https://www.mgtv.com/b/100989/1015373.html', ''],
	                     '梦想之花': ['https://www.mgtv.com/b/100985/1015368.html', ''],
	                     '“漫漫看”系列片': ['https://www.mgtv.com/b/100987/1015370.html', ''],
	                     '用生命写就的告白': ['https://www.mgtv.com/b/100983/1015365.html', ''],
	                     '摘星的你': ['https://www.mgtv.com/b/100984/1015366.html', ''],
	                     '保安日记': ['https://www.mgtv.com/b/100981/1015361.html', ''],
	                     '天堂的小说': ['https://www.mgtv.com/b/100982/1015362.html', ''],
	                     '告别囧途': ['https://www.mgtv.com/b/100980/1015360.html', ''],
	                     '深蓝': ['https://www.mgtv.com/b/100978/1015357.html', ''],
	                     '我的成人礼': ['https://www.mgtv.com/b/100977/1015355.html', ''],
	                     '致父亲': ['https://www.mgtv.com/b/100975/1015353.html', ''],
	                     '大漠“胡杨”': ['https://www.mgtv.com/b/100976/1015354.html', ''],
	                     '鼓舞': ['https://www.mgtv.com/b/100974/1015352.html', ''],
	                     '我不让你走': ['https://www.mgtv.com/b/100970/1015347.html', ''],
	                     '奔跑的鸭蛋': ['https://www.mgtv.com/b/100973/1015351.html', ''],
	                     '回家的路': ['https://www.mgtv.com/b/100964/1015328.html', ''],
	                     '青草地': ['https://www.mgtv.com/b/100965/1015329.html', ''],
	                     '1分16秒': ['https://www.mgtv.com/b/100968/1015335.html', ''],
	                     '逐梦': ['https://www.mgtv.com/b/54888/1015319.html', ''],
	                     '有心有方向': ['https://www.mgtv.com/b/100962/1015325.html', ''],
	                     '希望树': ['https://www.mgtv.com/b/100956/1015318.html', ''],
	                     '在路上': ['https://www.mgtv.com/b/100954/1015316.html', ''],
	                     '城市梦想家': ['https://www.mgtv.com/b/100953/1015315.html', ''],
	                     '谢谢你带我去听海': ['https://www.mgtv.com/b/100952/1015314.html', ''],
	                     '田埂上的梦': ['https://www.mgtv.com/b/100951/1015313.html', ''],
	                     '我的记忆我的年': ['https://www.mgtv.com/b/311735/3816622.html', ''],
	                     '相爱四十年': ['https://www.mgtv.com/b/327210/4892324.html', ''],
	                     '此间的奋斗': ['https://www.mgtv.com/b/327349/4796507.html', ''],
	                     '时光的旋律': ['https://www.mgtv.com/b/327423/4806288.html', ''],
	                     '不老乡音': ['https://www.mgtv.com/b/327523/4809065.html', ''],
	                     '四十年四十村 纯享版': ['https://www.mgtv.com/b/327718/4834377.html', ''],
	                     '与法同行': ['https://www.mgtv.com/b/327376/4840046.html', ''],
	                     '中国出了个毛泽东·故园长歌': ['https://www.mgtv.com/b/327833/4856385.html', ''],
	                     '迷彩虎讲堂 2019': ['https://www.mgtv.com/b/327426/5070493.html', ''],
	                     '巴盐': ['https://www.mgtv.com/b/328075/4957973.html', ''],
	                     '川味 第二季': ['https://www.mgtv.com/b/328077/4963225.html', ''],
	                     '人民至上': ['https://www.mgtv.com/b/328227/5093482.html', ''],
	                     '光阴的故事-中柬情谊': ['https://www.mgtv.com/b/328375/5150304.html', ''],
	                     '潮起海之南': ['https://www.mgtv.com/b/328605/5798578.html', ''],
	                     '中国照相馆': ['https://www.mgtv.com/b/328453/5234249.html', ''],
	                     '致敬新时代': ['https://www.mgtv.com/b/327083/5260799.html', ''],
	                     '我们的非洲朋友': ['https://www.mgtv.com/b/330261/5878524.html', ''],
	                     '下一站 天亮': ['https://www.mgtv.com/b/330265/5869937.html', ''],
	                     '黄河': ['https://www.mgtv.com/b/330168/5830234.html', ''],
	                     '“锦绣中华·大美山川”微视频大赛作品展': ['https://www.mgtv.com/b/330054/5800423.html', ''],
	                     '盐池滩羊': ['https://www.mgtv.com/b/330173/5830314.html', ''],
	                     '六盘山': ['https://www.mgtv.com/b/330169/5830290.html', ''],
	                     '丝路印象': ['https://www.mgtv.com/b/330171/5830312.html', ''],
	                     '变迁': ['https://www.mgtv.com/b/330174/5830207.html', ''],
	                     '画家眼中的丝绸之路': ['https://www.mgtv.com/b/330167/5830212.html', ''],
	                     '穿越腾格里': ['https://www.mgtv.com/b/330170/5830210.html', ''],
	                     '家园': ['https://www.mgtv.com/b/330172/5830243.html', ''],
	                     '膳食志': ['https://www.mgtv.com/b/329840/5713409.html', ''],
	                     '历史方城式': ['https://www.mgtv.com/b/329260/5491763.html', ''],
	                     '不负青春不负村 第二季': ['https://www.mgtv.com/b/329304/5555255.html', ''],
	                     '我来自中国': ['https://www.mgtv.com/b/328272/5510222.html', ''],
	                     '周末热纪录': ['https://www.mgtv.com/b/110001/2933163.html', ''],
	                     '第三届优秀国产纪录片及创作人才扶持项目表彰活动': ['https://www.mgtv.com/b/157401/1731586.html', ''],
	                     '醉美湘镇': ['https://www.mgtv.com/b/328916/5346535.html', ''],
	                     '守望': ['https://www.mgtv.com/b/166113/1815028.html', ''],
	                     '无声的梦想': ['https://www.mgtv.com/b/166126/1815071.html', ''],
	                     '少年': ['https://www.mgtv.com/b/328942/5363459.html', ''],
	                     '奔跑吧小凡': ['https://www.mgtv.com/b/166146/1815142.html', ''],
	                     '创新中国 第二季': ['https://www.mgtv.com/b/328919/5345908.html', ''],
	                     '博物馆奇妙夜': ['https://www.mgtv.com/b/1137/230123.html', '预告'],
	                     '锦绣潇湘': ['https://www.mgtv.com/b/4408/365251.html', '预告'],
	                     '湖南最美小镇': ['https://www.mgtv.com/b/41557/480522.html', ''],
	                     '味道': ['https://www.mgtv.com/b/50095/1000555.html', ''],
	                     '中国梦 未来篇': ['https://www.mgtv.com/b/100949/1015311.html', ''],
	                     '采血护士': ['https://www.mgtv.com/b/100957/1015320.html', ''],
	                     '说文解梦': ['https://www.mgtv.com/b/100958/1015321.html', ''],
	                     '最美情书': ['https://www.mgtv.com/b/100963/1015327.html', ''],
	                     '回家 中国梦': ['https://www.mgtv.com/b/100966/1015330.html', ''],
	                     '鸡蛋启示录': ['https://www.mgtv.com/b/100967/1015333.html', ''],
	                     '我是中医': ['https://www.mgtv.com/b/100986/1015369.html', ''],
	                     '国家大剧院古典音乐频道': ['https://www.mgtv.com/b/100991/1015395.html', ''],
	                     '电影史话 潇湘电影频道': ['https://www.mgtv.com/b/157516/1733873.html', ''],
	                     '群众路线系列动漫': ['https://www.mgtv.com/b/159453/1802430.html', ''],
	                     '巅球—律动雪域': ['https://www.mgtv.com/b/159454/1802435.html', ''],
	                     '最美的风景叫文明': ['https://www.mgtv.com/b/159470/1802622.html', ''],
	                     '中国梦系列': ['https://www.mgtv.com/b/159473/1802633.html', ''],
	                     '阿U微动画之梦想系列：传递': ['https://www.mgtv.com/b/166026/1811908.html', ''],
	                     '最好吃的饭': ['https://www.mgtv.com/b/166109/1815018.html', ''],
	                     '汪星人': ['https://www.mgtv.com/b/168549/1862245.html', '预告'],
	                     '王凯靳东十年磨一剑': ['https://www.mgtv.com/b/168695/3611119.html', ''],
	                     '延时摄影': ['https://www.mgtv.com/b/168319/3619191.html', ''],
	                     '故宫新事': ['https://www.mgtv.com/b/317500/4060420.html', '预告']}
	dic_theme_convert_url = dic_title_build_by_url(dic_title_url_vip)
	list_all = divide_line(1500,all_need_claw)
	num = 9
	list_input = list_all[num]
	re_get_title_and_update_by_url(list_input)


