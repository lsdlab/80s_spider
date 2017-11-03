#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-11-01 14:44:52
# Project: 80s_dm

import re
from pyspider.libs.base_handler import *

START_PAGE = 'http://www.80s.tw/dm/list/----14--p'
PAGE_NUM = 1
PAGE_TOTAL = 1
# PAGE_TOTAL = 61


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
        title, year, latest_update, special_list, special_list_link, update_period, other_names, actors, actors_link = self.format.format_brief_info(
            response)

        print('=======')
        print(title)
        print(year)
        print(latest_update)
        print(special_list)
        print(special_list_link)
        print(update_period)
        print(other_names)
        print(actors)
        print(actors_link)

        type, region, directors, directors_link, created_at, updated_at, item_length, douban_rate, douban_comment_link, movie_content = self.format.format_detail_info(
            response)

        print('=======')
        print(type)
        print(region)
        print(directors)
        print(directors_link)
        print(created_at)
        print(updated_at)
        print(item_length)
        print(douban_rate)
        print(douban_comment_link)
        print(movie_content)

        # 第一个 tab bt 直接能解析，其他的 tab 需要爬单独的 html 再解析
        # http://www.80s.tw/movie/1173/bt-1 bd-1 hd-1
        row_title, format_title, format_size, download_link = self.format.get_download_info(
            response)

        self.crawl(response.url + "/bd-1", callback=self.get_bd_info)
        self.crawl(response.url + "/hd-1", callback=self.get_hd_info)

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
        pass

    def get_download_info(self, res):
        # 电影原始名称 电视 赛车总动员 4.2 G 需要处理
        row_title = [i.text() for i in res.doc('.nm > span').items()]
        # 格式化后的名称列表
        format_title = [i.split(' ')[1]+ '-' +i.split(' ')[3] for i in row_title]

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

        print('=======')
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

        # 最近更新
        latest_update = "".join(info_span[0].split('： ')[1].split())
        if len(info_span) > 4:
            special_list = info_span[1].split('：')[1].strip()
            special_list_link = info_span_link[0]
            update_period = info_span[2].split('：')[1].strip()
            other_names = info_span[3].split('：')[1].strip()
            other_names = '/'.join(other_names.split(' , '))
            actors = info_span[4].split('：')[1].strip()
            actors = '/'.join(actors.split(' '))
            actors_link = info_span_link[1:]
        else:
            special_list = ''
            special_list_link = ''
            update_period = info_span[1].split('：')[1].strip()
            other_names = info_span[2].split('：')[1].strip()
            other_names = '/'.join(other_names.split(' , '))
            actors = info_span[3].split('：')[1].strip()
            actors = '/'.join(actors.split(' '))
            actors_link = info_span_link[0:]
        return title, year, latest_update, special_list, special_list_link, update_period, other_names, actors, actors_link

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

        region = "/".join(span_block[1].split('： ')[1].split())

        directors = '/'.join(span_block[2].split('： ')[1].split(' '))
        directors_link = span_block_link[0]

        created_at = span_block[3].split('： ')[1]
        item_length = span_block[4].split('： ')[1]
        updated_at = span_block[5].split('： ')[1]
        douban_rate = span_block[6].split('： ')[1]
        douban_comment_link = span_block_link[1]
        movie_content = res.doc('#movie_content').text().split('： ')[1].strip()
        return type, region, directors, directors_link, created_at, updated_at, item_length, douban_rate, douban_comment_link, movie_content
