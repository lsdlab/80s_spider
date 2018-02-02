# 80s_spider

www.80s.tw 爬虫，用 [pyspider](https://github.com/binux/pyspider)，
只爬电影、电视剧、动漫、综艺，爬取后存储至 MongoDB


## model

model 见 `model/resource.py`，数据清洗和保存更新操作都放在 `utils.py` 中。


## 运行

```
pyspider --config config.json
```


![](http://breakwire.oss-cn-shanghai.aliyuncs.com/Screen%20Shot%202018-01-15%20at%2002.30.24.png)

先爬一遍整站的话成功率在 94% 左右，电影、电视剧、综艺基本都爬下来了，动漫的失败率最高，应该是数据解析处理没有完全考虑到位。


# LICENCE
MIT
