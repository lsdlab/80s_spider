# 80s_spider

www.80s.tw 爬虫，用 [pyspider](https://github.com/binux/pyspider)，
只爬电影、电视剧、动漫、综艺，爬取后存储至 MongoDB


## model

model 见 `model/resource.py`，数据清洗和保存更新操作都放在 `utils.py` 中。


## 运行

```
pyspider --config config.json
```


# LICENCE
MIT
