#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-11-21 10:21:37
# Project: 80s_daily

import re
from pyspider.libs.base_handler import *
from spider.utils import *
WRITE_MONGODB = True

UPDATE = {
    "movie": "http://www.80s.tw/top/last_update_list/1",
    "ju": "http://www.80s.tw/top/last_update_list/tv",
    "dm": "http://www.80s.tw/top/last_update_list/14",
    "zy": "http://www.80s.tw/top/last_update_list/4"
}


class Handler(BaseHandler):
    crawl_config = {}

    # 一天
    @every(minutes=24 * 60)
    def on_start(self):
        for rtype, url in UPDATE.items():
            self.crawl(
                url,
                headers=generate_random_headers(),
                callback=self.list_page,
                save={'rtype': rtype})

    @config(age=10 * 24 * 60 * 60, priority=1, retries=1)
    def list_page(self, response):
        # 只取十个就够了
        newest_ten_url = [
            i.attr.href for i in response.doc('.tpul1line a').items()
        ][:10]
        for i in newest_ten_url:
            if i.split('/')[-2:-1] == [response.save['rtype']]:
                print(i)
                self.crawl(
                    i,
                    fetch_type='js',
                    load_images=True,
                    headers=generate_random_headers(),
                    callback=self.detail_page,
                    save={'rtype': response.save['rtype']})

    # age 一天内认为页面没有改变，不会再重新爬取
    # 详情页
    @config(age=24 * 60 * 60, auto_recrawl=True, priority=2, retries=1)
    def detail_page(self, response):
        resource_item = {}
        final_json = {}
        resource_item["url"] = response.url
        resource_item["title"] = response.doc('title').text()
        # 构建两块信息
        brief_info = format_brief_info(response, response.save['rtype'])
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
            if WRITE_MONGODB:
                download_json_final = get_download_info(
                    response, response.save['rtype'], mark)
                final_json = {**final_json, **download_json_final}
                write_to_mongodb(final_json, mark)

            # 另外两种大小，可有可无
            tab_text = response.doc('.cpage').text()
            bt_re = re.search(r"电视", tab_text)
            bd_re = re.search(r"平板", tab_text)
            hd_re = re.search(r"手机", tab_text)
            pt_re = re.search(r"小MP4", tab_text)
            if bt_re and mark != 'bt':
                self.crawl(
                    response.url + "/bt-1",
                    headers=generate_random_headers(),
                    callback=self.get_bt_info,
                    save={
                        'resource_item': resource_item,
                        'rtype': response.save['rtype']
                    })
            if bd_re and mark != 'bd':
                self.crawl(
                    response.url + "/bd-1",
                    headers=generate_random_headers(),
                    callback=self.get_bd_info,
                    save={
                        'resource_item': resource_item,
                        'rtype': response.save['rtype']
                    })
            elif hd_re and mark != 'hd':
                self.crawl(
                    response.url + "/hd-1",
                    headers=generate_random_headers(),
                    callback=self.get_hd_info,
                    save={
                        'resource_item': resource_item,
                        'rtype': response.save['rtype']
                    })
            elif pt_re and mark != 'pt':
                self.crawl(
                    response.url + "/mp4-1",
                    headers=generate_random_headers(),
                    callback=self.get_pt_info,
                    save={
                        'resource_item': resource_item,
                        'rtype': response.save['rtype']
                    })
            return {
                "url": response.url,
                "title": response.doc('.font14w').text(),
            }
        else:
            print('========== 处理错误，没有得到下载信息 ==========')

    # age 一天内认为页面没有改变，不会再重新爬取
    # 爬取 bt
    @config(age=24 * 60 * 60, auto_recrawl=True, priority=3, retries=1)
    def get_bt_info(self, response):
        self.crawl_download_info(response, 'bt',
                                 response.save['resource_item'])

    # age 一天内认为页面没有改变，不会再重新爬取
    # 爬取 bd
    @config(age=24 * 60 * 60, auto_recrawl=True, priority=3, retries=1)
    def get_bd_info(self, response):
        self.crawl_download_info(response, 'bd',
                                 response.save['resource_item'])

    # age 一天内认为页面没有改变，不会再重新爬取
    # 爬取 hd
    @config(age=24 * 60 * 60, auto_recrawl=True, priority=3, retries=1)
    def get_hd_info(self, response):
        self.crawl_download_info(response, 'hd',
                                 response.save['resource_item'])

    @config(age=24 * 60 * 60, auto_recrawl=True, priority=3, retries=1)
    def get_pt_info(self, response):
        self.crawl_download_info(response, 'pt',
                                 response.save['resource_item'])

    def crawl_download_info(self, response, mark, resource_item):
        if WRITE_MONGODB:
            download_json_final = get_download_info(
                response, response.save['rtype'], mark)
            url_source = response.url
            update_download_info_to_mongodb(download_json_final, mark,
                                            url_source)
