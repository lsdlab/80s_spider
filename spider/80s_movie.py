#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-11-03 10:56:36
# Project: 80s_movie

import re
from pyspider.libs.base_handler import *
from spider.utils import *


FIRST_PAGE = 'http://www.80s.tw/movie/list'
START_PAGE = 'http://www.80s.tw/movie/list/-----p'
PAGE_NUM = 1
PAGE_TOTAL = 408
WRITE_MONGODB = True


class Handler(BaseHandler):
    crawl_config = {}

    def __init__(self):
        self.first_page = FIRST_PAGE
        self.start_page = START_PAGE
        self.page_num = PAGE_NUM
        self.page_total = PAGE_TOTAL

    # 每三天重爬
    @every(minutes=24 * 60 * 5)
    def on_start(self):
        self.crawl(
            self.first_page,
            headers=generate_random_headers(),
            callback=self.get_page_num)

    # age 一天内认为页面没有改变，不会再重新爬取，每天自动重爬
    # 获取页数
    @config(age=24 * 60 * 60, auto_recrawl=True, priority=1)
    def get_page_num(self, response):
        pager_list = [i.attr.href for i in response.doc('.pager > a').items()]
        page_total_url = pager_list[-1:][0]
        page_total_re = re.search(r"p(\d+)", page_total_url)
        if page_total_re:
            page_total = page_total_re.group(0)[1:]
        else:
            page_total = self.page_total
        print('总页数 ========== ' + str(page_total))
        while self.page_num <= int(page_total):
            crawl_url = self.start_page + str(self.page_num)
            print(crawl_url)
            self.crawl(
                crawl_url,
                headers=generate_random_headers(),
                callback=self.index_page)
            self.page_num += 1

    # age 一天内认为页面没有改变，不会再重新爬取，每天自动重爬
    # 列表页
    @config(age=24 * 60 * 60, auto_recrawl=True, priority=1)
    def index_page(self, response):
        for each in response.doc('.h3 > a').items():
            if each.attr.href.split('/')[-2:-1] == ['movie']:
                print(each.attr.href)
                self.crawl(
                    each.attr.href,
                    fetch_type='js',
                    headers=generate_random_headers(),
                    callback=self.detail_page)

    # age 一天内认为页面没有改变，不会再重新爬取
    # 详情页
    @config(age=24 * 60 * 60, auto_recrawl=True, priority=2)
    def detail_page(self, response):
        resource_item = {}
        final_json = {}
        resource_item["url"] = response.url
        resource_item["title"] = response.doc('title').text()
        # 构建两块信息
        brief_info = format_brief_info(response, 'movie')
        resource_brief = construct_brief_json(brief_info)
        detail_info = format_detail_info(response)
        resource_detail = construct_detail_json(detail_info)
        resource_item = {**resource_brief, **resource_detail}

        if WRITE_MONGODB:
            # 两块信息先构建好
            final_json = construct_final_json(resource_item, response.url)

        # 第一个 tab bt 直接能解析，其他的 tab 需要爬单独的 html 再解析
        # http://www.80s.tw/movie/1173/bt-1 bd-1 hd-1
        mark = get_mark(response.doc('.dlselected > span').text())
        final_json["url_has_downlaod"] = []
        final_json["url_has_downlaod"].append(mark)

        if mark:
            # 构建第一个下载页面的 JSON 信息
            first_tab_download_info = get_download_info(response, 'movie')
            download_json = construct_download_json(
                first_tab_download_info, mark=mark)
            if WRITE_MONGODB:
                download_json_final = construct_final_download_json(
                    download_json, mark)
                final_json = {**final_json, **download_json_final}
                write_to_mongodb(final_json, mark)

            # 另外两种大小，可有可无
            tab_text = response.doc('.cpage').text()
            bd_re = re.search(r"平板", tab_text)
            hd_re = re.search(r"手机", tab_text)
            pt_re = re.search(r"小MP4", tab_text)
            if bd_re and mark != 'bd':
                self.crawl(
                    response.url + "/bd-1",
                    headers=generate_random_headers(),
                    callback=self.get_bd_info,
                    save={'resource_item': resource_item})
            elif hd_re and mark != 'hd':
                self.crawl(
                    response.url + "/hd-1",
                    headers=generate_random_headers(),
                    callback=self.get_hd_info,
                    save={'resource_item': resource_item})
            elif pt_re and mark != 'pt':
                self.crawl(
                    response.url + "/mp4-1",
                    headers=generate_random_headers(),
                    callback=self.get_pt_info,
                    save={'resource_item': resource_item})

            return {
                "url": response.url,
                "title": response.doc('.font14w').text(),
            }
        else:
            print('========== 处理错误，没有得到下载信息 ==========')

    # age 一天内认为页面没有改变，不会再重新爬取
    # 爬取 bd
    @config(age=24 * 60 * 60, auto_recrawl=True, priority=3)
    def get_bd_info(self, response):
        self.crawl_download_info(response, 'bd',
                                 response.save['resource_item'])

    # age 一天内认为页面没有改变，不会再重新爬取
    # 爬取 hd
    @config(age=24 * 60 * 60, auto_recrawl=True, priority=3)
    def get_hd_info(self, response):
        self.crawl_download_info(response, 'hd',
                                 response.save['resource_item'])

    @config(age=24 * 60 * 60, auto_recrawl=True, priority=3)
    def get_pt_info(self, response):
        self.crawl_download_info(response, 'pt',
                                 response.save['resource_item'])

    def crawl_download_info(self, response, mark, resource_item):
        tab_download_info = get_download_info(response, 'movie')
        download_json = construct_download_json(
            tab_download_info, mark=mark)
        if WRITE_MONGODB:
            download_json_final = construct_final_download_json(
                download_json, mark)
            url_source = response.url
            update_download_info_to_mongodb(download_json_final, mark,
                                            url_source)
