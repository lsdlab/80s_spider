import re
import hashlib
from datetime import datetime
from model.resource import ResourceRecord
from model.resource import ResourceSource
from model.resource import ResourceDownloadItem
from model.resource import ResourceTagItem
from fake_useragent import UserAgent
from mongoengine import connect

databases = [
    dict(host="127.0.0.1", port=27017, name='movie'),
]

for database in databases:
    connect(
        alias=database['name'],
        db=database['name'],
        host=database['host'],
        port=database['port'])


# 处理上半部分信息
def format_brief_info(res, rtype):
    title, year, latest_update, current, total, update_period, special_list, other_names, actors, header_img_link, screenshot_link = '', '', '', '', '', '', '', '', '', '', ''
    info = res.doc('.info').text()
    # 名称
    title = res.doc('.font14w').text()
    # 年份
    year_re = re.search(r"(\d{4})", info)
    if year_re:
        year = year_re.group(0)
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
    info_span_link = [i.attr.href for i in res.doc('.info > span > a').items()]

    print(info_span)
    print(info_span_link)

    if rtype == 'movie' or rtype == 'zy':
        current = 1
        total = 1

    # info_span 第一个可能为空，有的电视剧名称前面有个国语粤语标识，这五个信息排版混乱，用正则找
    for i in info_span:
        if re.search(r"最近更新", i):
            if "：" in i:
                raw_latest_update = i.split('：')
                if raw_latest_update[1]:
                    latest_update = raw_latest_update[1].strip()
                    # 处理 total current
                    total, current = 0, 0
                    total_current_re = re.search(r"/", latest_update)
                    current_re = re.search(r"第(\d+)集", latest_update)
                    total_re = re.search(r"共(\d+)集", latest_update)
                    # 有总数有当前集数
                    if total_current_re:
                        current_re = re.search(r"第(\d+)集",
                                               latest_update.split('/')[0])
                        total_re = re.search(r"共(\d+)集",
                                             latest_update.split('/')[1])
                        if current_re:
                            current = current_re.group(0)[1:-1]
                        if total_re:
                            total = total_re.group(0)[1:-1]
                    # 只有当前集数
                    elif current_re:
                        current = current_re.group(0)[1:-1]
                    # 只有总技术
                    elif total_re:
                        total = total_re.group(0)[1:-1]
        elif re.search(r"更新周期", i):
            if "：" in i:
                raw_update_period = i.split('：')
                if raw_update_period[1]:
                    update_period = raw_update_period[1].strip()
        elif re.search(r"又名", i):
            # 又名可有可无
            if "：" in i:
                raw_other_names = i.split('：')
                if raw_other_names[1]:
                    other_names = raw_other_names[1].strip()
                    # 如果能详细处理
                    if ' , ' in other_names:
                        other_names = '|'.join(other_names.split(' , '))
        elif re.search(r"专题", i):
            # 专题也是可有可无
            if "：" in i:
                raw_special_list = i.split('：')
                if raw_special_list[1]:
                    special_list = raw_special_list[1].strip()
        elif re.search(r"演员", i):
            if "：" in i:
                raw_actors = i.split('：')
                if raw_actors[1]:
                    actors = raw_actors[1].strip()
                    # 如果能详细处理
                    if ' ' in actors:
                        actors = '|'.join(actors.split(' '))

    return title, year, latest_update, current, total, update_period, special_list, other_names, actors, header_img_link, screenshot_link


# 处理下半部份信息
def format_detail_info(res):
    type, region, language, directors, created_at, updated_at, item_length, douban_rate, douban_comment_link, movie_content = '', '', '', '', '', '', '', '', '', ''
    # 类型、地区、语言、剧情介绍等信息的字符串列表和链接
    span_block, span_block_link = [], []
    span_block = [i.text() for i in res.doc('.span_block').items()]
    span_block_link = [
        i.attr.href or '' for i in res.doc('.span_block > a').items()
    ]

    print(span_block)
    print(span_block_link)

    if span_block:
        for i in span_block:
            if re.search(r"类型", i):
                if "：" in i:
                    raw_type = i.split('：')
                    if raw_type[1]:
                        type = raw_type[1].strip()
                        # 如果能详细处理
                        if " " in type:
                            type = '|'.join(type.split(' '))
            elif re.search(r"导演", i):
                # 导演可有可无
                if "：" in i:
                    raw_directors = i.split('：')
                    if raw_directors[1]:
                        directors = raw_directors[1].strip()
                        # 如果能详细处理
                        if " " in directors:
                            directors = '|'.join(directors.split(' '))
            elif re.search(r"地区", i):
                if len(i) > 10:
                    region = re.sub('[\s+]', ' ', i)
                    if "：" in region:
                        raw_region = region.split('：')
                        if raw_region[1]:
                            region = raw_region[1].strip()
                            # 如果能详细处理
                            region = "|".join(region.split())
                else:
                    if "：" in i:
                        raw_region = i.split('：')
                        if raw_region[1]:
                            region = raw_region[1].strip()
                            # 如果能详细处理
                            if " " in region:
                                region = '|'.join(region.split(' '))
            elif re.search(r"语言", i):
                if "：" in i:
                    raw_language = i.split('：')
                    if raw_language[1]:
                        language = raw_language[1].strip()
                        # 如果能详细处理
                        if " " in language:
                            language = '|'.join(language.split(' '))
            elif re.search(r"上映日期", i):
                if "：" in i:
                    raw_created_at = i.split('：')
                    if raw_created_at[1]:
                        created_at = raw_created_at[1].strip()
            elif re.search(r"片长", i):
                if "：" in i:
                    raw_item_length = i.split('：')
                    if raw_item_length[1]:
                        item_length = raw_item_length[1].strip()
            elif re.search(r"更新日期", i):
                if "：" in i:
                    raw_created_at = i.split('：')
                    if raw_created_at[1]:
                        updated_at = raw_created_at[1].strip()
            elif re.search(r"豆瓣评分", i):
                if "：" in i:
                    raw_douban_rate = i.split('：')
                    if raw_douban_rate[1]:
                        douban_rate = raw_douban_rate[1].strip()
                        if douban_rate == '暂无':
                            douban_rate = '0'

    if span_block_link:
        douban_comment_link = span_block_link[-1]
    if len(res.doc('#movie_content').text()) == 5:
        movie_content = ''
    else:
        movie_content = res.doc('#movie_content').text().split('： ')[1].strip()
    return type, region, language, directors, created_at, updated_at, item_length, douban_rate, douban_comment_link, movie_content


def construct_brief_json(*args, **kwargs):
    brief_info = {}
    brief_info["title"] = args[0][0]
    brief_info["year"] = args[0][1]
    brief_info["latest_update"] = args[0][2]
    brief_info["current"] = args[0][3]
    brief_info["total"] = args[0][4]
    brief_info["update_period"] = args[0][5]
    brief_info["special_list"] = args[0][6]
    brief_info["other_names"] = args[0][7]
    brief_info["actors"] = args[0][8]
    brief_info["header_img_link"] = args[0][9]
    brief_info["screenshot_link"] = args[0][10]
    return brief_info


def construct_detail_json(*args, **kwargs):
    detail_info = {}
    detail_info["type"] = args[0][0]
    detail_info["region"] = args[0][1]
    detail_info["language"] = args[0][2]
    detail_info["directors"] = args[0][3]
    detail_info["created_at"] = args[0][4]
    detail_info["updated_at"] = args[0][5]
    detail_info["item_length"] = args[0][6]
    detail_info["douban_rate"] = args[0][7]
    detail_info["douban_comment_link"] = args[0][8]
    detail_info["movie_content"] = args[0][9]
    return detail_info


def construct_final_json(resource_item, url_source):
    final_json = {}
    m = hashlib.md5()
    md5_string = ResourceSource._80s + '/' + url_source.split('/')[-1]
    m.update(md5_string.encode('utf-8'))

    if url_source.split('/')[-2] == 'movie':
        rtype = '电影'
    elif url_source.split('/')[-2] == 'ju':
        rtype = '电视剧'
    elif url_source.split('/')[-2] == 'dm':
        rtype = '动漫'
    elif url_source.split('/')[-2] == 'zy':
        rtype = '综艺'
    else:
        rtype = '未知'
    final_json["rtype"] = rtype
    final_json["hash"] = m.hexdigest()
    final_json["url_source"] = url_source
    final_json["title"] = resource_item["title"]
    final_json["sub_title"] = resource_item["latest_update"]
    final_json["year"] = resource_item["year"]
    final_json["last_update_desc"] = resource_item["latest_update"]
    final_json["update_cycle"] = resource_item["update_period"]
    final_json["url_image_thumb"] = resource_item["header_img_link"]
    final_json["url_image"] = resource_item["header_img_link"]
    final_json["show_release_time"] = resource_item["created_at"]
    final_json["show_update_time"] = resource_item["updated_at"]
    final_json["score"] = resource_item["douban_rate"]
    final_json["actors"] = resource_item["actors"]
    final_json["directors"] = resource_item["directors"]
    final_json["areas"] = resource_item["region"]
    final_json["tags"] = resource_item["type"]
    final_json["langs"] = ''
    final_json["time_length"] = resource_item["item_length"]
    final_json["total"] = resource_item["total"]
    final_json["current"] = resource_item["current"]
    final_json["source"] = ResourceSource._80s
    final_json["summery"] = resource_item["movie_content"]
    if resource_item["screenshot_link"] == '':
        final_json["url_image_list"] = ['']
    else:
        final_json["url_image_list"] = [resource_item["screenshot_link"]]
    final_json["create_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    final_json["update_time"] = final_json["create_time"]

    return final_json


def get_download_info(res, rtype, mark):
    # 多语言处理
    # 电影原始名称 电视 赛车总动员 4.2 G 需要处理
    row_title = [i.text() for i in res.doc('.nm > span').items()]
    center_title = [i.text() for i in res.doc('.nm a').items()]
    center_download_link = [i.attr.href for i in res.doc('.nm a').items()]
    # 格式化后的名称列表
    # 格式化后的剧集名称列表，有国语粤语之分，size, download_link 一起放在 for 里面处理
    resource_tag_item = {}
    download_list = []
    for k, i in enumerate(row_title):
        size_re = re.search(r"\d*\.\d*.?[G|GB|M|MB]", i)
        episode_language_re = re.search(r"国语|粤语|日语|泰语|英语|韩语|德语|法语", i)
        if episode_language_re:
            episode_language = episode_language_re.group(0)
        else:
            episode_language = '正片'
        resource_tag_item = {}
        resource_tag_item["title"] = episode_language
        resource_tag_item["item_list"] = []

        if rtype == 'dm' or rtype == 'ju':
            episode_number_re = re.search(r"第(\d+.*-*_*\d*)集", i)
            if episode_number_re:
                title = episode_number_re.group(0)[1:-1]
            else:
                title = center_title[k]
        elif rtype == 'movie' or rtype == 'zy':
            title = center_title[k]
        else:
            title = ""

        if size_re:
            size_re_group = size_re.group(0)
            if ' ' in size_re_group:
                size = ''.join(size_re_group.split(' '))
            else:
                size = size_re_group
        else:
            size = ''

        link = center_download_link[k]

        item_list_item = {}
        item_list_item['title'] = title
        item_list_item['size'] = size
        item_list_item['url'] = link
        resource_tag_item["item_list"].append(item_list_item)
        download_list.append(resource_tag_item)

    download_list_final = []
    language = [i['title'] for i in download_list]
    language = list(set(language))
    for i in language:
        resource_tag_item = {}
        resource_tag_item['title'] = i
        resource_tag_item['item_list'] = []
        download_list_final.append(resource_tag_item)

    for j in download_list:
        for i in download_list_final:
            if j['title'] == i['title']:
                item = {}
                item['title'] = j['item_list'][0]['title']
                item['size'] = j['item_list'][0]['size']
                item['url'] = j['item_list'][0]['url']
                i['item_list'].append(item)

    # print('download_list_final')
    # print(download_list_final)
    # return download_list_final

    download_item_key = "url" + "_" + mark + "_download"
    download_json_final = {}
    download_json_final[download_item_key] = download_list_final
    print('download_json_final--------------')
    print(download_json_final)
    return download_json_final


def write_to_mongodb(final_json, mark):
    print('========== final_json 只带有第一个下载信息 ==========')
    print(final_json)
    exist_record = ResourceRecord.objects(
        url_source=final_json["url_source"]).first()
    if not exist_record:
        # 新建
        record = create_or_update_record(exist_record, final_json)
    else:
        # 只保存有可能更新的信息和第一页下载信息
        exist_record = update_detail_download_info_to_mongodb(exist_record,
                                                              mark, final_json)
        exist_record['sub_title'] = final_json['sub_title']
        exist_record['last_update_desc'] = final_json['last_update_desc']
        exist_record['current'] = final_json['current']
        exist_record['total'] = final_json['total']
        exist_record['update_time'] = datetime.now()
        exist_record.save()
        print(
            '========== 资源已存在，更新基本信息(副标题和最新更新描述 current 和 total)和第一页的剧集更新（如果有更新的话） '
            + final_json['url_source'] + ' ==========')

# 更新新的剧集下载信息进去
def update_download_info_to_mongodb(final_json, mark, url):
    print('final_json 只带有下载信息的 final_json')
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
        exist_record = update_detail_download_info_to_mongodb(exist_record,
                                                              mark, final_json)


# 更新下载信息
def update_detail_download_info_to_mongodb(exist_record, mark, final_json):
    download_item_key = 'url' + '_' + mark + '_download'
    print('---------------------')
    print(final_json[download_item_key])

    _list = []
    for item1 in final_json[download_item_key]:
        tt_items = item1['item_list']
        it1 = ResourceTagItem()
        it1.title = item1['title']
        _list2 = []
        for item2 in tt_items:
            _item = ResourceDownloadItem()
            for _k1, _v1 in item2.items():
                _item.__setitem__(_k1, _v1)
            _list2.append(_item)
        it1.item_list = _list2
        _list.append(it1)
    exist_record.__setitem__(download_item_key, _list)
    exist_record.save()
    return exist_record


# 生成随机 user-agent headers
def generate_random_headers():
    ua = UserAgent()
    headers = {"User-Agent": ua.random, "Host": "www.80s.tw"}
    return headers


def get_mark(mark_text):
    mark_re = re.search(r"电视|平板|手机|小MP4", mark_text)
    mark = ''
    if mark_re:
        if mark_re.group(0) == '电视':
            mark = 'bt'
        elif mark_re.group(0) == '平板':
            mark = 'bd'
        elif mark_re.group(0) == '手机':
            mark = 'hd'
        elif mark_re.group(0) == '小MP4':
            mark = 'pt'
    return mark


def create_or_update_record(record, resource):
    if not record:
        record = ResourceRecord()
        record.hash = resource['hash']
        record.url_source = resource['url_source']

    if not isinstance(record, ResourceRecord):
        return None
    if not isinstance(resource, dict):
        return None

    for key, value in resource.items():
        if key in [
                '_id', 'blocked', 'deleted', 'count_browser', 'count_download',
                'feedback', 'hash', 'url_source'
        ]:
            continue
        if key in [
                'url_bt_download', 'url_bd_download', 'url_hd_download',
                'url_pt_download'
        ]:
            _list = []
            for item1 in value:
                tt_items = item1['item_list']
                it1 = ResourceTagItem()
                it1.title = item1['title']
                _list2 = []
                for item2 in tt_items:
                    _item = ResourceDownloadItem()
                    for _k1, _v1 in item2.items():
                        _item.__setitem__(_k1, _v1)
                    _list2.append(_item)
                it1.item_list = _list2
                _list.append(it1)
            record.__setitem__(key, _list)
            continue
        if key in ['create_time', 'update_time']:
            dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            record.__setitem__(key, dt)
            continue
        record.__setitem__(key, value)
    record.save()
    return record
