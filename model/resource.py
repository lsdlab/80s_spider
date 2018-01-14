
from mongoengine import *
from model import BaseEnum


class ResourceSource(BaseEnum):
    _80s = "www.80s.tw"


class ResourceDownloadItem(EmbeddedDocument):
    title = StringField(required=True, default="")
    url = StringField(required=True, default="")
    url_backup = StringField(required=True, default="")
    size = StringField(required=True, default="")


class ResourceTagItem(EmbeddedDocument):
    title = StringField(required=True, default="")
    item_list = EmbeddedDocumentListField(
        "ResourceDownloadItem", required=False, default=[])


class ResourceRecord(Document):
    # 类型
    rtype = StringField(required=True)
    # 唯一标识，是否有这个必要呢？
    hash = StringField(required=True)
    # 抓取数据的来源网址
    url_source = StringField(required=True)
    # 标题
    title = StringField(required=True, default="")
    # 副标题
    sub_title = StringField(required=True, default="")
    # 简介
    summery = StringField(required=True, default="")
    # 最新更新描述
    last_update_desc = StringField(required=True, default="")
    # 更新周期
    update_cycle = StringField(required=True, default="")
    # 缩略图
    url_image_thumb = StringField(required=True, default="")
    # 原图
    url_image = StringField(required=True, default="")
    # 展示图
    url_image_list = ListField(
        StringField(required=False, default=""), required=True, default=[])
    # 发布时间
    show_release_time = StringField(required=True, default="")
    # 更新时间
    show_update_time = StringField(required=True, default="")
    # 年份
    year = StringField(required=True, default="")
    # 评分
    score = StringField(required=True, default="")
    # 演员
    actors = StringField(required=True, default="")
    # 导演
    directors = StringField(required=True, default="")
    # 区域
    areas = StringField(required=True, default="")
    # 标签
    tags = StringField(required=True, default="")
    # 语言
    langs = StringField(required=True, default="")
    # 时长
    time_length = StringField(required=True, default="")
    # 一共多少集
    total = IntField(required=True, default=0)
    # 当前第几集
    current = IntField(required=True, default=0)
    # 下载地址
    # 不同清晰度的片源列表，如["hd", "bd", "bt"]代表有三种片源，取的时候也是对应去取就好了
    url_has_downlaod = ListField(
        StringField(required=False, default=""), required=True, default=[])
    url_bt_download = EmbeddedDocumentListField(
        "ResourceTagItem", required=False, default=[])
    url_bd_download = EmbeddedDocumentListField(
        "ResourceTagItem", required=False, default=[])
    url_hd_download = EmbeddedDocumentListField(
        "ResourceTagItem", required=False, default=[])
    url_pt_download = EmbeddedDocumentListField(
        "ResourceTagItem", required=False, default=[])

    # 资源来源, 如80s
    source = StringField(required=True, default=ResourceSource._80s)

    # 创建时间
    create_time = DateTimeField(required=True)
    # 更新时间
    update_time = DateTimeField(required=False)

    meta = {'db_alias': 'movie'}
