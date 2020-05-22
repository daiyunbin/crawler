# -*- coding: utf-8 -*-
# author: Scandium
# work_location: CSM Peking 
# project : vector_calculate
# time: 2019/12/21 21:09

import csv
import os
import json
import redis
import copy
import elasticsearch


def ld_to_csv(input_dic, csv_directory, csv_name):
    with open(r'{dic_rectory}\{name}.csv'.format(dic_rectory=csv_directory, name=csv_name), 'w', newline='',
              encoding='gb18030') as csv_w:
        file = csv.writer(csv_w)
        if type(input_dic).__name__ == 'dict':
            for key in input_dic.keys():
                list_write = []
                if type(input_dic[key]).__name__ == 'list':
                    for write_value in input_dic[key]:
                        list_write.append(write_value)
                else:
                    list_write = [key, input_dic[key]]
                    file.writerow(list_write)
        elif type(input_dic).__name__ == 'list':
            for key in input_dic:
                list_write = []
                for write_value in key:
                    list_write.append(write_value)
                file.writerow(list_write)

#rds_list = redis.StrictRedis(host='127.0.0.1', port=6379, db=3, decode_responses=True)
#rds_single = redis.StrictRedis(host='127.0.0.1', port=6379, db=4, decode_responses=True)

# RDS_list 写入csv
def title_info_to_csv(rds_list):
    list_key = rds_list.keys()
    list_all_data_write = []
    for title in list_key:
        rds_data = rds_list.hgetall(title)
        publisher = rds_data['publisher']
        geographical_area = rds_data['geographical_area']
        comment_count_sum = rds_data['comment_count_sum']
        detail = rds_data['detail']
        duration_sum = rds_data['duration_sum']
        theme_type = rds_data['theme_type ']
        play_count_sum = rds_data['play_count_sum']
        video_count_sum = rds_data['video_count_sum']
        like_num_sum = rds_data['like_num_sum']
        vip = dic_title_url_vip[title][1]
        url = dic_title_url_vip[title][0]
        input_list = [title, detail, video_count_sum, duration_sum, publisher, theme_type, geographical_area, vip,
                      play_count_sum, like_num_sum, comment_count_sum, dic_title_url_vip[title][0]]
        list_all_data_write.append(input_list)
    ld_to_csv(list_all_data_write, r'F:\\', 'mgtv_list')


# single-video写入csv
def single_video_info_to_csv(rds_single):
    list_key = rds_single.keys()
    list_single_data_write = []
    for title in list_key:
        rds_data = rds_single.hgetall(title)

        video_title = rds_data['video_title']

        comment_count = rds_data['comment_count']

        video_url = rds_data['video_url']

        play_count = rds_data['play_count']

        duration = rds_data['duration']

        like_num = rds_data['like_num']

        title = rds_data['title']

        input_list = [video_title, video_url, duration, play_count, like_num, comment_count, title]
        list_single_data_write.append(input_list)
    ld_to_csv(list_single_data_write, r'F:\\', 'mgtv_single')


# 统计收集rds种某个标签等于相应值的个数,返回列表
def single_no_duratgion(input_rds, input_tag, input_value):
    list_key = input_rds.keys()
    list_reclaw = []
    num_0 = 0
    for title in list_key:
        rds_data = input_rds.hgetall(title)
        tag_value = rds_data[input_tag]
        # except:
        # 	print(rds_data)
        # 	rds_single.delete(title)
        # 	duration_sum = 1
        if duration_sum == input_value:
            num_0 += 1
            list_reclaw.append(title)
    print(num_0)
    return list_reclaw


# 删除rds中的数据,如果数据没有带相应的标签值
def del_data_if_has_no_tag(rds_input, input_tag):
    list_key = rds_input.keys()
    del_num = 0
    for title in list_key:
        rds_data = rds_single.hgetall(title)
        try:
            tag = rds_data[input_tag]
            print(title, 'has the tag named:', tag)
        except:
            print(title)
            rds_list.delete(title)
            del_num += 1
    print('total_delete: ', del_num)


# 视频播放量转换
def trans_play_count(play_count_str):
    """suitable for the format 22万, 22万次播放, 22.2万, 2,222万, 2,222.2万, 2,222, 222"""
    play_count_str = play_count_str.replace('次播放', '')
    play_count_str = play_count_str.replace('播放', '')
    try:
        if '万' in play_count_str:
            play_count_str = play_count_str.split('万')[0]
            if ',' in play_count_str:
                play_count_str = play_count_str.replace(',', '')
            play_count = int(float(play_count_str) * 1e4)
            return play_count
        elif "w" in play_count_str:
            play_count_str = play_count_str.split('w')[0]
            if ',' in play_count_str:
                play_count_str = play_count_str.replace(',', '')
            play_count = int(float(play_count_str) * 1e4)
            return play_count
        else:
            try:
                play_count = int(play_count_str)
            except:
                play_count = int(play_count_str.replace(',', ''))
            return play_count
    except:
        return None


# 视频时长转换
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


# 视频列表数据写入rds
def parse_data(rds_list, data_dic, project_name):
    res = rds_list.hgetall(project_name)
    if res:
        if not res.get("project_tags"):
            res["project_tags"] = ""
        if data_dic.get("style_tags"):
            if data_dic.get("style_tags") not in res["style_tags"]:
                data_dic["style_tags"] = res["style_tags"] + "," + data_dic.get("style_tags")
        if data_dic.get("project_tags"):
            if data_dic.get("project_tags") not in res["project_tags"]:
                data_dic["project_tags"] = res["project_tags"] + "," + data_dic.get("project_tags")
        if data_dic.get("provider"):
            if data_dic.get("provider") not in res["provider"]:
                data_dic["provider"] = res["provider"] + "," + data_dic.get("provider")
        res.update(data_dic)
        rds_list.hmset(project_name, res)
    else:
        data = copy.deepcopy({
            # "title":web_text_select(title),
            "geographical_area": '',
            "detail": '',
            "publisher": '',
            "theme_type ": ''
        })
        data.update(data_dic)
        rds_list.hmset(project_name, data)


# 视频单集数据写入rds
def parse_single_data(rds_single, data_dic, project_name):
    res = rds_single.hgetall(project_name)
    if res:
        if not res.get("project_tags"):
            res["project_tags"] = ""
        if data_dic.get("style_tags"):
            if data_dic.get("style_tags") not in res["style_tags"]:
                data_dic["style_tags"] = res["style_tags"] + "," + data_dic.get("style_tags")
        if data_dic.get("project_tags"):
            if data_dic.get("project_tags") not in res["project_tags"]:
                data_dic["project_tags"] = res["project_tags"] + "," + data_dic.get("project_tags")
        if data_dic.get("provider"):
            if data_dic.get("provider") not in res["provider"]:
                data_dic["provider"] = res["provider"] + "," + data_dic.get("provider")
        res.update(data_dic)
        rds_single.hmset(project_name, res)
    else:
        data = copy.deepcopy(
            {'video_title': '', 'comment_count': 0, 'video_url': '', 'play_count': '', 'duration': '', 'like_num': ''})
        data.update(data_dic)
        rds_single.hmset(project_name, data)


# rds_single.hgetall('周末热纪录20150524期：少年少年（中）')
# dic_out = {
# 	#"title":web_text_select(title),
# 	"geographical_area": '',
# 	"detail": '',
# 	"publisher": '',
# 	"theme_type ": ''
# 	}
#
# single_video_dic = {
# 			"platform": "bilibili",
# 			"vid": "",
# 			"title": "",
# 			"video_title": "",
# 			"url": "",
# 			"video_url":"",
# 			"describe": "",
# 			"video_count": "",
# 			"duration": "",
# 			"year": "",
# 			"provider": "",
# 			"language": "",
# 			"area": "",
# 			"if_pay": "",
# 			"play_count": "",
# 			"play_heat": "",
# 			"rate": "",
# 			"favorite_count": "",
# 			"comment_count": "",
# 			"barrage_count": "",
# 		}

if __name__ == '__main__':
    pass

# 此行之下皆为测试
