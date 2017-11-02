#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-11-01 14:44:52
# Project: 80s_movie

import re
import json
from pyspider.libs.base_handler import *

START_PAGE = 'http://www.80s.tw/movie/list/-----p'
PAGE_NUM = 1
PAGE_TOTAL = 1
# PAGE_TOTAL = 408


class Handler(BaseHandler):
    crawl_config = {}

    def __init__(self):
        self.start_page = START_PAGE
        self.page_num = PAGE_NUM
        self.page_total = PAGE_TOTAL
        self.format = Format()

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
            self.crawl(each.attr.href, callback=self.detail_page)

    @config(priority=2)
    def detail_page(self, response):
        # title, year, site_desc, special_list, special_list_link, other_names, actors, actors_link = self.format.format_brief_info(
        #     response)

        self.format.construct_brief_json(self.format.format_brief_info(response))

        # print(title)
        # print(year)
        # print(site_desc)
        # print(special_list)
        # print(special_list_link)
        # print(other_names)
        # print(actors)
        # print(actors_link)


        # type, type_link, region, region_link, language, language_link, directors, directors_link, created_at, updated_at, item_length, douban_rate, douban_comment_link, movie_content = self.format.format_detail_info(
        #     response)

        self.format.construct_detail_json(self.format.format_detail_info(response))


        # print(type)
        # print(type_link)
        # print(region)
        # print(region_link)
        # print(language)
        # print(language_link)
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
        # row_title, format_title, format_size, download_link = self.format.get_download_info(
        #     response)

        self.format.construct_download_json(self.format.get_download_info(response))

        self.crawl(response.url + "/bd-1", callback=self.get_bd_info)
        self.crawl(response.url + "/hd-1", callback=self.get_hd_info)

        self.item_json['url'] = response.url
        self.item_json['title'] = response.doc('title').text()

        return {
            "url": response.url,
            "title": response.doc('title').text(),
        }

    @config(priority=2)
    def get_bd_info(self, response):
        if response.status_code == 200:
            row_title, format_title, format_size, download_link = self.format.get_download_info(
                response)


    @config(priority=2)
    def get_hd_info(self, response):
        if response.status_code == 200:
            row_title, format_title, format_size, download_link = self.format.get_download_info(
                response)


class Format:
    def __init__(self):
        self.item_json = {}

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
        print(format_title)
        print(format_size)
        print(download_link)

        return row_title, format_title, format_size, download_link

    def format_brief_info(self, res):
        info = res.doc('.info').text()
        # 年份
        year_re = re.search(r"\d{4}", info)
        year = year_re.group(0)
        # 名称
        title = res.doc('.font14w').text()

        # 80s 的描述，专题，又名，演员 字符串列表和对应的链接
        info_span = [i.text() for i in res.doc('.info > span').items()]
        # 第一个是80s的一句话描述，可为空，后面都是演员链接
        info_span_link = [
            i.attr.href for i in res.doc('.info > span > a').items()
        ]

        print(info_span)
        print(info_span_link)

        site_desc = info_span[0]
        if len(info_span) > 3:
            special_list = info_span[1].split('：')[1].strip()
            special_list_link = info_span_link[0]
            other_names = info_span[2].split('：')[1].strip()
            other_names = '/'.join(other_names.split(' , '))
            actors = info_span[3].split('：')[1].strip()
            actors = '/'.join(actors.split(' '))
            actors_link = info_span_link[1:]
        else:
            special_list = ''
            special_list_link = ''
            other_names = info_span[1].split('：')[1].strip()
            other_names = '/'.join(other_names.split(' , '))
            actors = info_span[2].split('：')[1].strip()
            actors = '/'.join(actors.split(' '))
            actors_link = info_span_link[1:]
        return title, year, site_desc, special_list, special_list_link, other_names, actors, actors_link

    def format_detail_info(self, res):
        # 类型、地区、语言、剧情介绍等信息的字符串列表和链接
        span_block = [i.text() for i in res.doc('.span_block').items()]
        span_block_link = [
            i.attr.href or '' for i in res.doc('.span_block > a').items()
        ]

        print(span_block)
        print(span_block_link)

        type_list = span_block[0].split('： ')[1].split(' ')
        type = '/'.join(type_list)
        type_link = span_block_link[:len(type_list)]

        region = '/'.join(span_block[1].split('： ')[1].split(' '))
        region_link = span_block_link[len(type_list):len(type_list) + 1]

        language = '/'.join(span_block[2].split('： ')[1].split(' '))
        language_link = span_block_link[len(type_list) + 1:len(type_list) + 2]

        directors = '/'.join(span_block[3].split('： ')[1].split(' '))
        directors_link = span_block_link[len(type_list) + 2:len(
            type_list) + 2 + len(span_block[3].split('： ')[1].split(' '))]

        created_at = span_block[4].split('： ')[1]
        item_length = span_block[5].split('： ')[1]
        updated_at = span_block[6].split('： ')[1]
        douban_rate = span_block[7].split('： ')[1]
        douban_comment_link = span_block_link[-1]
        movie_content = res.doc('#movie_content').text().split('： ')[1].strip()
        return type, type_link, region, region_link, language, language_link, directors, directors_link, created_at, updated_at, item_length, douban_rate, douban_comment_link, movie_content

    def construct_brief_json(self, *args):
        self.item_json['brief_info'] = {}
        self.item_json['brief_info']['title'] = args[0]
        self.item_json['brief_info']['year'] = args[1]
        self.item_json['brief_info']['site_desc'] = args[2]
        self.item_json['brief_info']['special_list'] = args[3]
        self.item_json['brief_info']['special_list_link'] = args[4]
        self.item_json['brief_info']['other_names'] = args[5]
        self.item_json['brief_info']['actors'] = args[6]
        self.item_json['brief_info']['actors_link'] = args[7]

    def construct_detail_json(self, *args):
        self.item_json['detail_info'] = {}
        self.item_json['detail_info']['type'] = args[0]
        self.item_json['detail_info']['type_link'] = args[1]
        self.item_json['detail_info']['region'] = args[2]
        self.item_json['detail_info']['region_link'] = args[3]
        self.item_json['detail_info']['language'] = args[4]
        self.item_json['detail_info']['language_link'] = args[5]
        self.item_json['detail_info']['directors'] = args[6]
        self.item_json['detail_info']['directors_link'] = args[7]
        self.item_json['detail_info']['created_at'] = args[8]
        self.item_json['detail_info']['updated_at'] = args[9]
        self.item_json['detail_info']['item_length'] = args[10]
        self.item_json['detail_info']['douban_rate'] = args[11]
        self.item_json['detail_info']['douban_comment_link'] = args[12]
        self.item_json['detail_info']['movie_content'] = args[13]

    def construct_download_json(self, *args):
        self.item_json['download_json'] = {}
        self.item_json['download_json']['row_title'] = args[0]
        self.item_json['download_json']['format_title'] = args[1]
        self.item_json['download_json']['format_size'] = args[2]
        self.item_json['download_json']['download_link'] = args[3]

    def write_to_json(self, data):
        file_name = data['url']
        with open(file_name, 'w') as outfile:
            json.dump(data, outfile)
