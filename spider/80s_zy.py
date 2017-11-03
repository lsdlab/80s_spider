#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-11-01 14:44:52
# Project: 80s_dm

import re
import json
from pyspider.libs.base_handler import *

START_PAGE = 'http://www.80s.tw/zy/list/----4--p'
PAGE_NUM = 1
PAGE_TOTAL = 1
# PAGE_TOTAL = 17


class Handler(BaseHandler):
    crawl_config = {}

    def __init__(self):
        self.start_page = START_PAGE
        self.page_num = PAGE_NUM
        self.page_total = PAGE_TOTAL
        self.item_json = {}

    @every(minutes=24 * 60)
    def on_start(self):
        while self.page_num <= self.page_total:
            crawl_url = self.start_page + str(self.page_num)
            print(crawl_url)
            self.crawl(crawl_url, callback=self.index_page)
            self.page_num += 1

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('.h3 > a').items():
            print(each.attr.href)
            self.crawl(each.attr.href, callback=self.detail_page, fetch_type='js')

    @config(priority=2)
    def detail_page(self, response):
        # title, year, latest_update, update_period, other_names, actors, actors_link = self.format.format_brief_info(
        #     response)

        self.construct_brief_json(self.format_brief_info(response))

        #print(title)
        #print(year)
        #print(latest_update)
        #print(update_period)
        ##print(special_list)
        #print(special_list_link)
        #print(other_names)
        #print(actors)
        #print(actors_link)
        # print(header_img_link)
        # print(screenshot_link)

        # type, type_link, region, directors, directors_link, created_at, updated_at, item_length, douban_rate, douban_comment_link, movie_content = self.format.format_detail_info(
        #     response)

        self.construct_detail_json(self.format_detail_info(response))

        # print(type)
        # print(type_link)
        # print(region)
        # print(directors)
        # print(directors_link)
        # print(created_at)
        # print(updated_at)
        # print(item_length)
        # print(douban_rate)
        # print(douban_comment_link)
        # print(movie_content)

        # 第一个 tab bt 直接能解析，其他的 tab 需要爬单独的 html 再解析
        # http://www.80s.tw/movie/1173/bt-1 bd-1 hd-1
        # row_title, format_title, format_size, download_link = self.get_download_info(
            # response)
        mark_re = re.search(r"电视|平板|手机", response.doc('.dlselected > span').text())
        mark = 'other'
        if mark_re:
            if mark_re.group(0) == '电视':
                mark = 'bt'
            elif mark_re.group(0) == '平板':
                mark = 'bt'
            elif mark_re.group(0) == '手机':
                mark = 'hd'
        self.construct_download_json(self.get_download_info(response), mark=mark)
        self.write_default_download_info_to_json(self.item_json, response)

        self.item_json["url"] = response.url
        self.item_json["title"] = response.doc('title').text()
        self.write_brief_info_to_json(self.item_json)

        # 三种大小
        # self.crawl(response.url + "/bt-1", callback=self.get_bt_info)
        self.crawl(response.url + "/bd-1", callback=self.get_bd_info)
        self.crawl(response.url + "/hd-1", callback=self.get_hd_info)

    @config(priority=2)
    def get_bt_info(self, response):
        if response.status_code == 200:
            # row_title, format_title, format_size, download_link = self.get_download_info(
            #     response)
            self.construct_download_json(self.get_download_info(response), mark='bt')
            print('--------------')
            print(self.item_json)
            self.write_download_info_to_json(self.item_json, response)

    @config(priority=2)
    def get_bd_info(self, response):
        if response.status_code == 200:
            # row_title, format_title, format_size, download_link = self.get_download_info(
            #     response)
            self.construct_download_json(self.get_download_info(response), mark='bd')
            self.write_download_info_to_json(self.item_json, response)

    @config(priority=2)
    def get_hd_info(self, response):
        if response.status_code == 200:
            # row_title, format_title, format_size, download_link = self.get_download_info(
            #     response)
            self.construct_download_json(self.get_download_info(response), mark='hd')
            self.write_download_info_to_json(self.item_json, response)

    def get_download_info(self, res):
        # 电影原始名称 电视 赛车总动员 4.2 G 需要处理
        row_title = [i.text() for i in res.doc('.nm > span').items()]
        # 格式化后的名称列表
        format_title = [i.split(' ')[1] for i in row_title]

        # 格式化后的文件大小列表
        format_size = []
        for i in row_title:
            size_re = re.search(r"\d*\.\d*.?[G|GB|M|MB]", i)
            if size_re:
                size = ''.join(size_re.group(0).split(' '))
            else:
                size = ''
            format_size.append(size)
        #format_size = [i.split(' ')[2] for i in row_title]

        # 下载链接列表
        download_link = [
            i.children().attr.href for i in res.doc('.dlbutton1').items()
        ]

        print(row_title)
        print(len(row_title))
        print(format_title)
        print(len(format_title))
        print(format_size)
        print(len(format_size))
        print(download_link)
        print(len(download_link))

        return row_title, format_title, format_size, download_link

    def format_brief_info(self, res):
        title, year, latest_update, update_period, special_list, special_list_link, other_names, actors, actors_link, header_img_link, screenshot_link = '', '', '', '', '', '', '', '', '', '', ''
        info = res.doc('.info').text()
        # 年份
        year_re = re.search(r"\d{4}", info)
        year = year_re.group(0)
        # 名称
        title = res.doc('.font14w').text()
        # 题图
        header_img_link = res.doc('.img > img').attr.src
        print('header_img')
        print(header_img_link)
        # 截图
        screenshot_link = res.doc('.noborder > img').attr.src
        print('screenshot_link')
        print(screenshot_link)

        # 80s 的描述，专题，又名，演员 字符串列表和对应的链接
        info_span = [i.text() for i in res.doc('.info > span').items()]
        # 第一个是80s的一句话描述，可为空，后面都是演员链接
        info_span_link = [
            i.attr.href for i in res.doc('.info > span > a').items()
        ]
        i = '; '.join(info_span)

        print(info_span)
        print(info_span_link)

        # info_span 第一个可能为空，有的电视剧名称前面有个国语粤语标识，这五个信息排版混乱，用正则找
        for i in info_span:
            if re.search(r"最近更新", i):
                latest_update = "".join(i.split('： ')[1].split())
            elif re.search(r"更新周期", i):
                update_period = i.split('：')[1].strip()
            elif re.search(r"又名", i):
                # 又名可有可无
                other_names = i.split('：')[1].strip()
                other_names = '/'.join(other_names.split(' , '))
            elif re.search(r"专题", i):
                # 专题也是可有可无
                special_list = i.split('：')[1].strip()
                special_list_link = info_span_link[:1]
            elif re.search(r"演员", i):
                actors = i.split('：')[1].strip()
                actors = '/'.join(actors.split(' '))
                if special_list:
                    actors_link = info_span_link[1:]
                else:
                    actors_link = info_span_link[:]

        return title, year, latest_update, update_period, special_list, special_list_link, other_names, actors, actors_link, header_img_link, screenshot_link

    def format_detail_info(self, res):
        type, type_link, region, directors, directors_link, created_at, updated_at, item_length, douban_rate, douban_comment_link, movie_content = '', '', '', '', '', '', '', '', '', '', ''
        # 类型、地区、语言、剧情介绍等信息的字符串列表和链接
        span_block = [i.text() for i in res.doc('.span_block').items()]
        span_block_link = [
            i.attr.href or '' for i in res.doc('.span_block > a').items()
        ]

        print(span_block)
        print(span_block_link)

        for i in span_block:
            if re.search(r"类型", i):
                type_list = i.split('： ')[1].split(' ')
                type = '/'.join(type_list)
                if span_block_link:
                    type_link = span_block_link[:len(type_list)]
            elif re.search(r"导演", i):
                # 导演可有可无
                directors = '/'.join(i.split('： ')[1].split(' '))
                if span_block_link:
                    directors_link = span_block_link[len(type_list):len(type_list) + 1]
            elif re.search(r"地区", i):
                region = '/'.join(i.split('： ')[1].split(' '))
            elif re.search(r"上映日期", i):
                created_at = i.split('： ')[1]
            elif re.search(r"片长", i):
                item_length = i.split('： ')[1]
            elif re.search(r"更新日期", i):
                updated_at = i.split('： ')[1]
            elif re.search(r"豆瓣评分", i):
                douban_rate = i.split('： ')[1]
        if span_block_link:
            douban_comment_link = span_block_link[-1]
        movie_content = res.doc('#movie_content').text().split('： ')[1].strip()
        return type, type_link, region, directors, directors_link, created_at, updated_at, item_length, douban_rate, douban_comment_link, movie_content


    def construct_brief_json(self, *args):
        print('========')
        print(args)
        self.item_json["brief_info"] = {}
        self.item_json["brief_info"]["title"] = args[0][0]
        self.item_json["brief_info"]["year"] = args[0][1]
        self.item_json["brief_info"]["latest_update"] = args[0][2]
        self.item_json["brief_info"]["update_period"] = args[0][3]
        self.item_json["brief_info"]["special_list"] = args[0][4]
        self.item_json["brief_info"]["special_list_link"] = args[0][5]
        self.item_json["brief_info"]["other_names"] = args[0][6]
        self.item_json["brief_info"]["actors"] = args[0][7]
        self.item_json["brief_info"]["actors_link"] = args[0][8]
        self.item_json["brief_info"]["header_img_link"] = args[0][9]
        self.item_json["brief_info"]["screenshot_link"] = args[0][10]

        total_current_re = re.search(r"第(\d*)集/共(\d*)集", args[0][2])
        if total_current_re:
            self.item_json["brief_info"]["current"] = total_current_re.group(0)
            self.item_json["brief_info"]["total"] = total_current_re.group(1)

        current_re = re.search(r"第(\d*)集", args[0][2])
        if current_re:
            self.item_json["brief_info"]["current"] = current_re.group(0)

    def construct_detail_json(self, *args):
        self.item_json["detail_info"] = {}
        self.item_json["detail_info"]["type"] = args[0][0]
        self.item_json["detail_info"]["type_link"] = args[0][1]
        self.item_json["detail_info"]["region"] = args[0][2]
        self.item_json["detail_info"]["directors"] = args[0][3]
        self.item_json["detail_info"]["directors_link"] = args[0][4]
        self.item_json["detail_info"]["created_at"] = args[0][5]
        self.item_json["detail_info"]["updated_at"] = args[0][6]
        self.item_json["detail_info"]["item_length"] = args[0][7]
        self.item_json["detail_info"]["douban_rate"] = args[0][8]
        self.item_json["detail_info"]["douban_comment_link"] = args[0][9]
        self.item_json["detail_info"]["movie_content"] = args[0][10]

    def construct_download_json(self, *args, **kwargs):
        mark = kwargs['mark']
        self.item_json["download_info"] = {}
        self.item_json["download_info"][mark] = {}
        self.item_json["download_info"][mark]["row_title"] = args[0][0]
        self.item_json["download_info"][mark]["format_title"] = args[0][1]
        self.item_json["download_info"][mark]["format_size"] = args[0][2]
        self.item_json["download_info"][mark]["download_link"] = args[0][3]

    def write_brief_info_to_json(self, data):
        file_name = data['url'].split('/')[-2] + '_' + data['url'].split('/')[
            -1] + '.json'
        # print('==========')
        # print(file_name)
        with open("/Users/Chen/Desktop/pyspider_example/json/" + file_name,
                  'w') as f:
            json.dump(data, f)

    def write_default_download_info_to_json(self, data, res):
        print('data')
        print(data)
        print('res')
        print(res)
        file_name = res.url.split('/')[-2] + '_' + res.url.split('/')[
            -1] + '.json'
        print('==========')
        print(file_name)
        with open("/Users/Chen/Desktop/pyspider_example/json/" + file_name, 'w') as f:
            json.dump(data, f)

    def write_download_info_to_json(self, data, res):
        print('data')
        print(data)
        print('res')
        print(res)
        file_name = res.url.split('/')[-3] + '_' + res.url.split('/')[
            -2] + '.json'
        print('==========')
        print(file_name)
        with open("/Users/Chen/Desktop/pyspider_example/json/" + file_name, 'r') as f:
            basic_info = json.load(f)
            print('basic_info')
            print(basic_info)

            if res.url.split('/')[-1] == 'bt-1':
                mark = 'bt'
            elif res.url.split('/')[-1] == 'bd-1':
                mark = 'bd'
            elif res.url.split('/')[-1] == 'hd-1':
                mark = 'hd'
            basic_info['download_info'][mark] = data

        with open("/Users/Chen/Desktop/pyspider_example/json/" + file_name, 'w') as f:
            json.dump(basic_info, f)
