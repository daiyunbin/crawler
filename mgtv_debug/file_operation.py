# -*- coding: utf-8 -*-
# author: Scandium
# work_location: CSM Peking 
# project : clawer_scandium
# time: 2019/12/27 11:56

import os, re, csv, json, traceback

def ld_to_csv(input_dic,csv_directory,csv_name):
	with open( r'{dic_rectory}\{name}.csv'.format(dic_rectory=csv_directory ,name=csv_name),'w',newline='', encoding='gb18030') as csv_w:
		file =  csv.writer(csv_w)
		if type(input_dic).__name__ == 'dict':
			for key in input_dic.keys():
				list_write = []
				if type(input_dic[key]).__name__ =='list':
					for write_value in input_dic[key]:
						list_write.append(write_value)
				else:
					list_write = [key,input_dic[key]]
					file.writerow(list_write)
		elif type(input_dic).__name__ == 'list':
			for key in input_dic:
				list_write = []
				for write_value in key:
					list_write.append(write_value)
				file.writerow(list_write)

def file_to_list(file_name,header = False):
	if header:
		start_num = 1
	else:
		start_num = 0
	if file_name.endswith('csv'):
		try:
			with open(file_name, "r", encoding='gb18030') as csv_file:
				# print('gb_csv')
				list_out = []
				csv_r = csv.reader((line.replace('\0', '') for line in csv_file))
				for row in csv_r:
					list_out.append(row)
				return list_out[start_num:]
		except:
			with open(file_name, "r", encoding='utf-8') as csv_file:
				list_out = []
				csv_r = csv.reader((line.replace('\0', '') for line in csv_file))
				for row in csv_r:
					list_out.append(row)
				return list_out[start_num:]
	else:
		try:
			list_out = []
			with open(file_name, "r", encoding='gb18030') as file1:
				for row in file1.readlines():
					list_out.append(row)
			return list_out[start_num:]
		except:
			try:
				list_out = []
				with open(file_name, "r", encoding='utf-8') as file1:
					for row in file1.readlines():
						list_out.append(row)
				return list_out[start_num:]
			except:
				print('Can not open', file_name)
				return []

def screen_data_from_dir(input_dir, out_dir, input_value_list, input_key = ''):
	input_value_list = input_value_list.copy()
	list_file = []
	for root, dirs, files in os.walk(input_dir):
		for name in files:
			list_file.append(os.path.join(root, name))
	if str(input_key).isdigit():
		file_class_index = input_key
	else:
		head_line = file_to_list(list_file[0])[0]
		file_class_index = head_line.index(input_key)
	list_out_file = []

	for file_name in list_file:
		if str(input_key).isdigit():
			file_list = file_to_list(file_name)
		else:
			file_list = file_to_list(file_name,header=True)
		list_out_file += list(filter(lambda x: x[file_class_index] in input_value_list, file_list))

	out_file_name  = 'screen_{input_key}.csv'.format(input_key = input_key)
	ld_to_csv(list_out_file, out_dir, out_file_name)

def screen_data_from_file_maxnum(input_dir_file, input_value_list, out_path, index_input, maxnum = 'all'):
	input_value_list =  input_value_list.copy()
	list_out_return = []
	file_list = file_to_list(input_dir_file)
	dic_value_count = {}
	for value in input_value_list:
		dic_value_count[value]  = 0
	for data_line in file_list:
		if data_line[index_input] in input_value_list:
			print(data_line)
			list_out_return.append(data_line)
			dic_value_count[data_line[index_input]] += 1
			if maxnum != 'all':
				if dic_value_count[value] >= int(maxnum):
					input_value_list.remove(data_line[index_input])
	out_file_name  = 'screen_{input_key}_{maxnum}.csv'.format(input_key = index_input,maxnum= str(maxnum))
	print(list_out_return )
	ld_to_csv(list_out_return,out_path,out_file_name)



	out_file_name = '{input_value_list}_{input_key}_{maxnum}.csv'.format(input_value_list=('&').join(input_value_list),
																		 input_key=index_input, maxnum=str(maxnum))

def dic_order_by_value(input_dic):
	list_tuple = sorted(input_dic.items(), key=lambda input_dic: input_dic[1], reverse=True)
	return dict(list_tuple)


if __name__ == '__main__':
	list_value = ["健康","旅游","经济","文娱","社会","数码","汽车","体育"]
	list_es_value = ["健康","游戏","财经","汽车","体育"]
	screen_data_from_dir('F:\PyCharm_project\short_Video_title_classify\es_test_data_10','F:\PyCharm_project\short_Video_title_classify', list_es_value, input_key=2, maxnum = 100)
	screen_data_from_file_maxnum('F:\PyCharm_project\short_Video_title_classify\es_test_data_10\daily-url-2019-10-31_month_8.csv', list_es_value,'F:\PyCharm_project\short_Video_title_classify', 2, maxnum=50)
	pass
	value_list = list_es_value.copy()

# 此行之下皆为测试
def screen_data_from_dir(input_dir, out_dir, input_value_list, input_key = '',maxnum = 'all'):
	list_file = []
	value_list = input_value_list.copy()
	dic_value_count = {}
	for value in input_value_list:
		dic_value_count[value] = 0

	for root, dirs, files in os.walk(input_dir):
		for name in files:
			list_file.append(os.path.join(root, name))
	if str(input_key).isdigit():
		file_class_index = input_key
	else:
		head_line = file_to_list(list_file[0])[0]
		file_class_index = head_line.index(input_key)
	list_out_file = []

	for file_name in list_file:
		if value_list:
			if str(input_key).isdigit():
				file_list = file_to_list(file_name)
			else:
				file_list = file_to_list(file_name,header=True)

			for data_line in file_list:
				if data_line[file_class_index] in value_list:
					print(data_line)
					list_out_file.append(data_line)
					dic_value_count[data_line[file_class_index]] += 1
					if maxnum != 'all':
						if dic_value_count[data_line[file_class_index]] >= int(maxnum):
							value_list.remove(data_line[file_class_index])
		#list_out_file += list(filter(lambda x: x[file_class_index] in input_value_list, file_list))
	out_file_name  = 'screen_{input_key}_{maxnum}'.format(input_key = input_key,maxnum = maxnum)
	ld_to_csv(list_out_file, out_dir, out_file_name)

list_value = ["娱乐",'搞笑','体育','美食','科技','母婴','宠物','旅行','旅游','财经','finance','军事','观军事','法制','网上法院','汽车','游戏']
list_thu_value =['体育', '财经', '房产', '家居','教育', '科技', '时尚', '时政', '游戏', '娱乐']
screen_data_from_dir('F:\PyCharm_project\short_Video_title_classify\es_test_data_10','F:\PyCharm_project\short_Video_title_classify', list_thu_value , input_key=2, maxnum=1000)

#随机数据集筛选

def screen_data_from_dir(input_dir, out_dir, input_value_list, input_key = '',maxnum = 'all'):
	list_file = []
	value_list = input_value_list.copy()

	dic_value_count = {}
	for value in input_value_list:
		dic_value_count[value] = 0

	for root, dirs, files in os.walk(input_dir):
		for name in files:
			list_file.append(os.path.join(root, name))
	if str(input_key).isdigit():
		file_class_index = input_key
	else:
		head_line = file_to_list(list_file[0])[0]
		file_class_index = head_line.index(input_key)
	list_out_file = []

	for file_name in list_file:
		if value_list:
			if str(input_key).isdigit():
				file_list = file_to_list(file_name)
			else:
				file_list = file_to_list(file_name,header=True)

			for data_line in file_list:
				if data_line[file_class_index] in value_list:
					print(data_line)
					list_out_file.append(data_line)
					dic_value_count[data_line[file_class_index]] += 1
					if maxnum != 'all':
						if dic_value_count[data_line[file_class_index]] >= int(maxnum):
							value_list.remove(data_line[file_class_index])
		#list_out_file += list(filter(lambda x: x[file_class_index] in input_value_list, file_list))
	out_file_name  = 'screen_{input_key}_{maxnum}'.format(input_key = input_key,maxnum = maxnum)
	ld_to_csv(list_out_file, out_dir, out_file_name)