# 80s_spider

www.80s.tw 爬虫，用 [pyspider](https://github.com/binux/pyspider)，
只爬电影、电视剧、动漫、综艺，爬取后存储至本地 JSON 和 MongoDB

## 运行

`pyspider --config pyspider.json`


## JSON 示例

```
{
  "title": "丛林",
  "year": "2017",
  "site_desc": "白人的探险精神,让人敬佩",
  "special_list": "",
  "special_list_link": "",
  "other_names": "丛林炼狱(台)/Jungle",
  "actors": "丹尼尔·雷德克里夫/托马斯·克莱舒曼/亚历克斯·罗素/莉莉·沙利文",
  "actors_link": [
    "http://www.80s.tw/actor/1360",
    "http://www.80s.tw/actor/4706",
    "http://www.80s.tw/actor/24377"
  ],
  "header_img_link": "http://t.dyxz.la/upload/img/201711/poster_20171104_2444940_b.jpg",
  "screenshot_link": "http://t.dyxz.la/upload/img/201711/20171104_4845639.jpg",
  "total": 1,
  "current": 1,
  "type": "剧情/冒险",
  "type_link": [
    "http://www.80s.tw/movie/list/f----",
    "http://www.80s.tw/movie/list/h----"
  ],
  "region": "其他",
  "region_link": [
    "http://www.80s.tw/movie/list/--f--"
  ],
  "language": "英语",
  "language_link": [
    "http://www.80s.tw/movie/list/---2-"
  ],
  "directors": "克瑞格·麦克林恩",
  "directors_link": [
    "http://www.80s.tw/director/4706"
  ],
  "created_at": "2017-10-20",
  "updated_at": "2017-11-04",
  "item_length": "115分钟",
  "douban_rate": "6.7",
  "douban_comment_link": "https://movie.douban.com/subject/26726261/comments",
  "movie_content": "影片改编自冒险家贝纳·金斯伯格同名畅销冒险小说，讲述他及其两位伙伴深入亚马逊丛林寻找失落黄金，险象环生的三周真实求生之旅。",
  "bt": {
    "row_title": [
      "电视 丛林 1.5 G"
    ],
    "format_title": [
      "丛林"
    ],
    "format_size": [
      "1.5G"
    ],
    "download_link": [
      "thunder://QUFodHRwOi8vZGwxNTMuODBzLmltOjkyMC8xNzExL+S4m+aely/kuJvmnpcubXA0Wlo="
    ]
  }
}
```

# LICENCE
MIT
