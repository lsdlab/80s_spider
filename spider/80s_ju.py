#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-11-01 14:44:52
# Project: 80s_ju

import re
import json
import hashlib
import uuid
from datetime import datetime
from pyspider.libs.base_handler import *
from model.resource.resource import ResourceRecord
from model.resource.resource import ResourceSource
from model.resource.resource import ResourceDownloadItem
from model.resource.resource import ResourceTagItem
from lib.tool.mongo_extend import MongoExtend
from stest.base_test import BaseTest

FIRST_PAGE = 'http://www.80s.tw/ju/list'
START_PAGE = 'http://www.80s.tw/ju/list/----0--p'
PAGE_NUM = 1
PAGE_TOTAL = 130
# PAGE_TOTAL = 5
WRITE_JSON = False
WRITE_MONGODB = True
UPDATE_TO_PRODUCTION = False
GLOBAL_HEADERS = {
    'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
    'Host':
    'www.80s.tw'
}


class Handler(BaseHandler):
    crawl_config = {'headers': GLOBAL_HEADERS}

    def __init__(self):
        self.first_page = FIRST_PAGE
        self.start_page = START_PAGE
        self.page_num = PAGE_NUM
        self.page_total = PAGE_TOTAL
        self.item_json = {}
        self.final_json = {}

    # 每三天重爬
    @every(minutes=24 * 60 * 3)
    def on_start(self):
        self.crawl(self.first_page, callback=self.get_page_num)

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
            self.crawl(crawl_url, callback=self.index_page)
            self.page_num += 1

    # age 一天内认为页面没有改变，不会再重新爬取，每天自动重爬
    # 列表页
    @config(age=24 * 60 * 60, auto_recrawl=True, priority=1)
    def index_page(self, response):
        for each in response.doc('.h3 > a').items():
            print(each.attr.href)
            self.crawl(
                each.attr.href, fetch_type='js', callback=self.detail_page)

    # age 一天内认为页面没有改变，不会再重新爬取
    # 详情页
    @config(age=24 * 60 * 60, auto_recrawl=True, priority=2)
    def detail_page(self, response):
        self.item_json["url"] = response.url
        self.item_json["title"] = response.doc('title').text()
        # 构建两块信息
        self.construct_brief_json(self.format_brief_info(response))
        self.construct_detail_json(self.format_detail_info(response))

        if WRITE_JSON:
            # 先不写，到取得第一部分下载信息的时候一起写进去
            # self.write_brief_info_to_json(self.item_json)
            pass
        if WRITE_MONGODB:
            self.construct_final_json(self.item_json, response)

        # 第一个 tab bt 直接能解析，其他的 tab 需要爬单独的 html 再解析
        # http://www.80s.tw/movie/1173/bt-1 bd-1 hd-1
        mark_re = re.search(r"电视|平板|手机|小MP4",
                            response.doc('.dlselected > span').text())
        mark = ''
        self.final_json["url_has_downlaod"] = []
        if mark_re:
            if mark_re.group(0) == '电视':
                mark = 'bt'
            elif mark_re.group(0) == '平板':
                mark = 'bd'
            elif mark_re.group(0) == '手机':
                mark = 'hd'
            elif mark_re.group(0) == '小MP4':
                mark = 'pt'
        self.final_json["url_has_downlaod"].append(mark)

        if mark:
            # 构建第一个下载页面的 JSON 信息
            self.construct_download_json(
                self.get_download_info(response), mark=mark)

            if WRITE_JSON:
                self.write_info_to_json(self.item_json, response)
            if WRITE_MONGODB:
                self.construct_final_download_json(self.item_json, mark)
                self.write_to_mongodb(self.final_json, mark)

            # 另外两种大小，可有可无
            tab_text = response.doc('.cpage').text()
            bd_re = re.search(r"平板", tab_text)
            hd_re = re.search(r"手机", tab_text)
            pt_re = re.search(r"小MP4", tab_text)
            if bd_re and mark != 'bd':
                self.crawl(response.url + "/bd-1", callback=self.get_bd_info)
            elif hd_re and mark != 'hd':
                self.crawl(response.url + "/hd-1", callback=self.get_hd_info)
            elif pt_re and mark != 'pt':
                self.crawl(response.url + "/mp4-1", callback=self.get_pt_info)

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
        self.crawl_download_info(response, 'bd')

    # age 一天内认为页面没有改变，不会再重新爬取
    # 爬取 hd
    @config(age=24 * 60 * 60, auto_recrawl=True, priority=3)
    def get_hd_info(self, response):
        self.crawl_download_info(response, 'hd')

    @config(age=24 * 60 * 60, auto_recrawl=True, priority=3)
    def get_pt_info(self, response):
        self.crawl_download_info(response, 'pt')

    def crawl_download_info(self, response, mark):
        if response.status_code == 200:
            self.construct_download_json(
                self.get_download_info(response), mark=mark)
            if WRITE_JSON:
                self.write_download_info_to_json(self.item_json, response)
            if WRITE_MONGODB:
                self.final_json = self.construct_final_download_json(
                    self.item_json, mark)
                url_source = response.url
                self.update_download_info_to_mongodb(self.final_json, mark,
                                                     url_source)

    def get_download_info(self, res):
        # 电影原始名称 电视 赛车总动员 4.2 G 需要处理
        row_title = [i.text() for i in res.doc('.nm > span').items()]
        # 格式化后的名称列表
        # format_title = [
        #     i.split(' ')[1] + '-' + i.split(' ')[3] for i in row_title
        # ]
        # 格式化后的剧集名称列表，有国语粤语之分，size, download_link 一起放在 for 里面处理
        cantonese_title = []
        national_title = []
        cantonese_size = []
        national_size = []
        cantonese_download_link = []
        national_download_link = []
        download_button_list = [
            i.children().attr.href for i in res.doc('.dlbutton1').items()
        ]
        for k, i in enumerate(row_title):
            size_re = re.search(r"\d*\.\d*.?[G|GB|M|MB]", i)
            if size_re:
                size = ''.join(size_re.group(0).split(' '))
            else:
                size = ''
            cantonese_re = re.search(r"粤语", i)
            # 标题变成 1 2 3 纯数字 电视剧和动漫变成数字，电影和综艺不变
            episode_number_re = re.search(r"第(\d+)集", i)
            episode_range_number_re = re.search(r"第(\d+-\d+)集", i)
            if episode_number_re:
                episode_number = episode_number_re.group(0)[1:-1]
            elif episode_range_number_re:
                episode_number = episode_range_number_re.group(0)[1:-1]
            else:
                episode_number = i.split(' ')[1] + '-' + i.split(' ')[3]
            # 带集数描述的title
            # title =  i.split(' ')[1] + '-' + i.split(' ')[3]
            # 没有迅雷按钮 判断标题上的链接是否是 '#'，是 '#' 再罝未 ''
            if len(download_button_list) != len(row_title):
                download_link = ''
            else:
                download_link = download_button_list[k]
            if cantonese_re:
                cantonese_title.append(episode_number)
                cantonese_size.append(size)
                cantonese_download_link.append(download_link)
            else:
                national_title.append(episode_number)
                national_size.append(size)
                national_download_link.append(download_link)
        return row_title, national_title, cantonese_title, national_size, cantonese_size, national_download_link, cantonese_download_link

    def format_brief_info(self, res):
        title, year, latest_update, update_period, special_list, special_list_link, other_names, actors, actors_link, header_img_link, screenshot_link = '', '', '', '', '', '', '', '', '', '', ''
        info = res.doc('.info').text()
        # 年份
        year_re = re.search(r"(\d{4})", info)
        if year_re:
            year = year_re.group(0)
        # 名称
        title = res.doc('.font14w').text()
        # 题图
        header_img_link = res.doc('.img > img').attr.src or ''
        print('header_img')
        print(header_img_link)
        # 截图
        screenshot_link = res.doc('.noborder > img').attr.src or ''
        print('screenshot_link')
        print(screenshot_link)

        # 80s 的描述，专题，又名，演员 字符串列表和对应的链接
        info_span = [i.text() for i in res.doc('.info > span').items()]
        # 第一个是80s的一句话描述，可为空，后面都是演员链接
        info_span_link = [
            i.attr.href for i in res.doc('.info > span > a').items()
        ]

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
                other_names = '|'.join(other_names.split(' , '))
            elif re.search(r"专题", i):
                # 专题也是可有可无
                special_list = i.split('：')[1].strip()
                special_list_link = info_span_link[:1]
            elif re.search(r"演员", i):
                actors = i.split('：')[1].strip()
                actors = '|'.join(actors.split(' '))
                if special_list:
                    actors_link = info_span_link[1:]
                else:
                    actors_link = info_span_link[:]
        return title, year, latest_update, update_period, special_list, special_list_link, other_names, actors, actors_link, header_img_link, screenshot_link

    def format_detail_info(self, res):
        type, region, directors, created_at, updated_at, item_length, douban_rate, douban_comment_link, movie_content = '', '', '', '', '', '', '', '', ''
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
                type = '|'.join(type_list)
            elif re.search(r"导演", i):
                # 导演可有可无
                directors = '|'.join(i.split('： ')[1].split(' '))
            elif re.search(r"地区", i):
                region = '|'.join(i.split('： ')[1].split(' '))
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
        if len(res.doc('#movie_content').text()) == 5:
            movie_content = ''
        else:
            movie_content = res.doc('#movie_content').text().split('： ')[
                1].strip()
        return type, region, directors, created_at, updated_at, item_length, douban_rate, douban_comment_link, movie_content

    def construct_brief_json(self, *args):
        self.item_json["title"] = args[0][0]
        self.item_json["year"] = args[0][1]
        self.item_json["latest_update"] = args[0][2]
        self.item_json["update_period"] = args[0][3]
        self.item_json["special_list"] = args[0][4]
        self.item_json["special_list_link"] = args[0][5]
        self.item_json["other_names"] = args[0][6]
        self.item_json["actors"] = args[0][7]
        self.item_json["actors_link"] = args[0][8]
        self.item_json["header_img_link"] = args[0][9]
        self.item_json["screenshot_link"] = args[0][10]

        total_current_re = re.search(r"/", args[0][2])
        current_re = re.search(r"第(\d+)集", args[0][2])
        total_re = re.search(r"共(\d+)集", args[0][2])
        if total_current_re:
            current_re = re.search(r"第(\d+)集", args[0][2].split('/')[0])
            total_re = re.search(r"共(\d+)集", args[0][2].split('/')[1])
            if current_re:
                self.item_json["current"] = current_re.group(0)[1:-1]
            if total_re:
                self.item_json["total"] = total_re.group(0)[1:-1]
        elif current_re:
            if current_re:
                self.item_json["current"] = current_re.group(0)[1:-1]
            self.item_json["total"] = 0
        elif total_re:
            if total_re:
                self.item_json["current"] = 0
            self.item_json["total"] = total_re.group(0)[1:-1]

    def construct_detail_json(self, *args):
        self.item_json["type"] = args[0][0]
        self.item_json["region"] = args[0][1]
        self.item_json["directors"] = args[0][2]
        self.item_json["created_at"] = args[0][3]
        self.item_json["updated_at"] = args[0][4]
        self.item_json["item_length"] = args[0][5]
        self.item_json["douban_rate"] = args[0][6]
        self.item_json["douban_comment_link"] = args[0][7]
        self.item_json["movie_content"] = args[0][8]

    def construct_download_json(self, *args, **kwargs):
        mark = kwargs['mark']
        self.item_json[mark] = {}
        self.item_json[mark]["row_title"] = args[0][0]
        self.item_json[mark]["national_title"] = args[0][1]
        self.item_json[mark]["cantonese_title"] = args[0][2]
        self.item_json[mark]["national_size"] = args[0][3]
        self.item_json[mark]["cantonese_size"] = args[0][4]
        self.item_json[mark]["national_download_link"] = args[0][5]
        self.item_json[mark]["cantonese_download_link"] = args[0][6]

    # def write_brief_info_to_json(self, data):
    #     file_name = data['url'].split('/')[-2] + '_' + data['url'].split('/')[
    #         -1] + '.json'
    #     # print('==========')
    #     # print(file_name)
    #     with open("/Users/Chen/Desktop/80s_spider/json/" + file_name,
    #               'w') as f:
    #         json.dump(data, f)

    def write_info_to_json(self, data, res):
        # print('data')
        # print(data)
        # print('res')
        # print(res)
        file_name = res.url.split('/')[-2] + '_' + res.url.split('/')[
            -1] + '.json'
        print('==========')
        print(file_name)
        with open("/Users/Chen/Desktop/80s_spider/json/" + file_name,
                  'w') as f:
            json.dump(data, f)

    def write_download_info_to_json(self, data, res):
        print('data')
        print(data)
        print('res')
        print(res)
        file_name = res.url.split('/')[-3] + '_' + res.url.split('/')[
            -2] + '.json'
        # print('==========')
        # print(file_name)
        with open("/Users/Chen/Desktop/80s_spider/json/" + file_name,
                  'r') as f:
            basic_info = json.load(f)
            print('basic_info')
            print(basic_info)

            if res.url.split('/')[-1] == 'bt-1':
                mark = 'bt'
            elif res.url.split('/')[-1] == 'bd-1':
                mark = 'bd'
            elif res.url.split('/')[-1] == 'hd-1':
                mark = 'hd'
            basic_info[mark] = data

        with open("/Users/Chen/Desktop/80s_spider/json/" + file_name,
                  'w') as f:
            json.dump(basic_info, f)

    def construct_final_json(self, item_json, res):
        m = hashlib.md5()
        md5_string = ResourceSource._80s + '/' + res.url.split('/')[-1]
        m.update(md5_string.encode('utf-8'))
        self.final_json["rtype"] = "电视剧"
        self.final_json["hash"] = m.hexdigest()
        self.final_json["url_source"] = res.url
        self.final_json["title"] = item_json["title"]
        self.final_json["sub_title"] = item_json["latest_update"]
        self.final_json["year"] = item_json["year"]
        self.final_json["last_update_desc"] = item_json["latest_update"]
        self.final_json["update_cycle"] = item_json["update_period"]
        self.final_json["url_image_thumb"] = item_json["header_img_link"]
        self.final_json["url_image"] = item_json["header_img_link"]
        self.final_json["show_release_time"] = item_json["created_at"]
        self.final_json["show_update_time"] = item_json["updated_at"]
        if item_json["douban_rate"] == '暂无':
            self.final_json["score"] == '0'
        else:
            self.final_json["score"] = item_json["douban_rate"]
        self.final_json["actors"] = item_json["actors"]
        self.final_json["directors"] = item_json["directors"]
        self.final_json["areas"] = item_json["region"]
        self.final_json["tags"] = item_json["type"]
        self.final_json["langs"] = ''
        self.final_json["time_length"] = item_json["item_length"]
        self.final_json["total"] = item_json["total"]
        self.final_json["current"] = item_json["current"]
        self.final_json["source"] = ResourceSource._80s
        self.final_json["summery"] = item_json["movie_content"]
        if item_json["screenshot_link"] == '':
            self.final_json["url_image_list"] = ['']
        else:
            self.final_json["url_image_list"] = [item_json["screenshot_link"]]
        self.final_json["url_bt_download"] = []
        self.final_json["url_bd_download"] = []
        self.final_json["url_hd_download"] = []
        self.final_json["url_pt_download"] = []
        self.final_json["create_time"] = datetime.now()
        self.final_json["update_time"] = self.final_json["create_time"]

    def construct_final_download_json(self, item_json, mark):
        download_item_key = "url" + "_" + mark + "_download"
        self.final_json[download_item_key] = []
        if 'national_title' in item_json[mark].keys() and item_json[mark][
                'cantonese_title'] == []:
            title = '正片'
        elif 'national_title' in item_json[mark].keys() and item_json[mark][
                'cantonese_title'] != []:
            title = '国语'
        if 'national_title' in item_json[mark].keys() and item_json[mark][
                'national_title']:
            resource_tag_item = {}
            resource_tag_item['item_list'] = []
            resource_tag_item['title'] = title
            for k, v in enumerate(item_json[mark]['national_title']):
                download_item = {}
                download_item['title'] = v
                download_item['size'] = item_json[mark]['national_size'][k]
                download_item['url'] = item_json[mark][
                    'national_download_link'][k]
                resource_tag_item['item_list'].append(download_item)
            self.final_json[download_item_key].append(resource_tag_item)
        if 'cantonese_title' in item_json[mark].keys() and item_json[mark][
                'cantonese_title']:
            resource_tag_item = {}
            resource_tag_item['item_list'] = []
            resource_tag_item['title'] = '粤语'
            for k, v in enumerate(item_json[mark]['cantonese_title']):
                download_item = {}
                download_item['title'] = v
                download_item['size'] = item_json[mark]['cantonese_size'][k]
                download_item['url'] = item_json[mark][
                    'cantonese_download_link'][k]
                resource_tag_item['item_list'].append(download_item)
            self.final_json[download_item_key].append(resource_tag_item)
        return self.final_json

    def write_to_mongodb(self, final_json, mark):
        print('========== final_json 只带有第一个下载信息 ==========')
        print(final_json)
        exist_record = ResourceRecord.objects(
            url_source=final_json["url_source"]).first()
        # 不存在，写入新的，存在就更新
        if not exist_record:
            new_resource_record = ResourceRecord(**final_json)
            new_resource_record.save()
            print('========== 存储至 MongoDB ' + final_json['url_source'] +
                  '==========')
            # 存储至线上 MongoDB
            self.update_to_production(new_resource_record)
        else:
            self.update_detail_download_info_to_mongodb(exist_record, mark,
                                                        final_json)
            exist_record['sub_title'] = final_json['sub_title']
            exist_record['last_update_desc'] = final_json['last_update_desc']
            exist_record.save()
            print('========== 资源已存在，更新基本信息(副标题和最新更新描述)和第一页的剧集更新（如果有更新的话） ' +
                  final_json['url_source'] + ' ==========')
            # 更新至线上 MongoDB
            self.update_to_production(exist_record)

    # 更新新的剧集下载信息进去
    def update_download_info_to_mongodb(self, final_json, mark, url):
        print('final_json')
        print(final_json)
        print('mark  ' + mark)
        url_source = url[:-5]
        print('url  ' + url)
        exist_record = ResourceRecord.objects(url_source=url_source).first()
        if exist_record:
            url_has_downlaod = list(exist_record['url_has_downlaod'])
            if mark not in url_has_downlaod:
                exist_record['url_has_downlaod'].append(mark)
            exist_record['update_time'] = datetime.now()
            exist_record.save()
            self.update_detail_download_info_to_mongodb(exist_record, mark,
                                                        final_json)
            # 更新至线上 MongoDB
            self.update_to_production(exist_record)

    def update_detail_download_info_to_mongodb(self, exist_record, mark,
                                               final_json):
        # 资源模型 剧集改为了嵌套，有国语粤语之分，更新处理逻辑改变
        download_item_key = 'url' + '_' + mark + '_download'

        print('---------------------')
        print(final_json[download_item_key])

        for i in final_json[download_item_key]:
            # 查询现有剧集，有新的才更新
            if list(exist_record[download_item_key]):
                resource_tag_item = exist_record[download_item_key].filter(
                    title=i['title']).first()
                if resource_tag_item:
                    episode_length = resource_tag_item['item_list'].count()
                    # print('episode_length ' + i['title'] + ' 现有剧集数 ========== ' +
                          # str(episode_length))
                    for j in i['item_list']:
                        if episode_length != 0:
                            exist_episode = resource_tag_item['item_list'].filter(
                                title=j['title'])
                            if exist_episode:
                                print('========== ' + j['title'] + ' ========== ' +
                                      '这一集已存在')
                            else:
                                item_list_item = ResourceDownloadItem(
                                    title=j['title'], url=j['url'], size=j['size'])
                                resource_tag_item['item_list'].append(
                                    item_list_item)
                                exist_record[download_item_key].append(
                                    resource_tag_item)
                                exist_record.save()
                                print('========== ' + j['title'] + ' ========== ' +
                                      '新剧集')
                        else:
                            item_list_item = ResourceDownloadItem(
                                title=j['title'], url=j['url'], size=j['size'])
                            resource_tag_item['item_list'].append(item_list_item)
                            exist_record[download_item_key].append(
                                resource_tag_item)
                            exist_record.save()
                            print('========== ' + j['title'] + ' ========== ' +
                                  '新剧集')
                else:
                    resource_tag_item = ResourceTagItem(title=i['title'])
                    for j in i['item_list']:
                        resource_download_item = ResourceDownloadItem(
                            title=j['title'], size=j['size'], url=j['url'])
                        resource_tag_item['item_list'].append(
                            resource_download_item)
                    exist_record[download_item_key].append(resource_tag_item)
                    exist_record.save()
            else:
                resource_tag_item = ResourceTagItem(title=i['title'])
                for j in i['item_list']:
                    resource_download_item = ResourceDownloadItem(
                        title=j['title'], size=j['size'], url=j['url'])
                    resource_tag_item['item_list'].append(
                        resource_download_item)
                exist_record[download_item_key].append(resource_tag_item)
                exist_record.save()

    def update_to_production(self, resource):
        print('========== 开始上传至生产 ==========')
        if UPDATE_TO_PRODUCTION:
            resource_json = MongoExtend.mongo_to_json(resource)
            module = 'resource'
            params = dict(
                method='update_resource',
                resource_json=resource_json,
                device_token='',
                source_from_description="pyspider",
                app_uuid=str(uuid.uuid1()))
            base_test = BaseTest()
            base_test.debug = False
            ret = base_test.do_post(module,
                                    base_test.buildup_arguments(params))
            data = base_test.process_response(ret.text)
            print(data)
            if data.code == 200:
                print('========== 上传到生产成功 ==========')
            else:
                print('========== 上传到生产失败 ==========')
        else:
            print('========== 不上传至生产 ==========')
        print('========== 上传至生产结束 ==========')
