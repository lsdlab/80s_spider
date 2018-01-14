class BaseEnum(object):

    # meta属性，这个字典里存储通用方法可以返回的数据或配置相关的属性
    __meta__ = {'title_kv': {}, 'small_title': {}}

    @classmethod
    def title_with_value(cls, value):
        title_kv = cls.__meta__['title_kv']
        return title_kv.get(value, None)

    @classmethod
    def title_list(cls):
        title_kv = cls.__meta__['title_kv']
        return list(title_kv.values())

    @classmethod
    def title_kv(cls):
        title_kv = cls.__meta__['title_kv']
        return title_kv

    @classmethod
    def get_small_title(cls, order_type):
        small_title = cls.__meta__['small_title']
        return small_title.get(order_type, None)

    @classmethod
    def find_enum_with_title(cls, title):
        for k, v in cls.__meta__.items():
            if v == title:
                return k
        return None
