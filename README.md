# 80s_spider

www.80s.tw 爬虫，用 [pyspider](https://github.com/binux/pyspider)，
只爬电影、电视剧、动漫、综艺，爬取后存储至本地 JSON 和 MongoDB

JSON 示例

```
{
  "brief_info": {
    "title": "赛车总动员",
    "year": "2006",
    "site_desc": "皮克斯的佳作，不容错过！",
    "special_list": "赛车总动员",
    "special_list_link": "http://www.80s.tw/tag/68",
    "other_names": "反斗车王(港)/汽车总动员/飞车正传/小汽车的故事",
    "actors": "欧文·威尔逊/王牌接线员拉里/保罗·纽曼/邦尼·亨特",
    "actors_link": [
      "http://www.80s.tw/actor/1807",
      "http://www.80s.tw/actor/5325",
      "http://www.80s.tw/actor/5975",
      "http://www.80s.tw/actor/5976"
    ]
  },
  "detail_info": {
    "type": "喜剧/动画/冒险/家庭/运动",
    "type_link": [
      "http://www.80s.tw/movie/list/2----",
      "http://www.80s.tw/movie/list/c----",
      "http://www.80s.tw/movie/list/h----",
      "http://www.80s.tw/movie/list/j----",
      "http://www.80s.tw/movie/list/o----"
    ],
    "region": "美国",
    "region_link": [
      "http://www.80s.tw/movie/list/--4--"
    ],
    "language": "英语",
    "language_link": [
      "http://www.80s.tw/movie/list/---2-"
    ],
    "directors": "约翰·拉塞特/乔·兰福特",
    "directors_link": [
      "http://www.80s.tw/director/320",
      "http://www.80s.tw/director/863"
    ],
    "created_at": "2006-06-09",
    "updated_at": "2017-10-31",
    "item_length": "117分钟",
    "douban_rate": "7.7']",
    "douban_comment_link": "https://movie.douban.com/subject/1428878/comments",
    "movie_content": "《赛车总动员》是由皮克斯动画工厂制作，并由迪士尼于2006年发行的电脑动画电影。该片由约翰·拉塞特执导，并且由欧文·威尔逊、保罗·纽曼、邦妮·亨特等人配音演出，这是迪士尼和皮克斯的第七部动画长片，也是在迪士尼买下皮克斯之前，两家公司旧有合约下的最后一部电影。\n故事的主角是一部时髦拉风的赛车，梦想在Route 66道路上展开的赛车大赛中脱颖而出，成为车坛新偶像。但不料他在参赛途中却意外迷路，闯入一个陌生的城镇，展开一段超乎想像的意外旅程。\n汽车世界中，一年一度的活塞杯再次拉开序幕。红色跑车“闪电”麦坤和“冠军”、“路霸”是冠军最有力的竞争者。作为新人，麦坤具有极高的天赋，同时也是一个目空一切的家伙。经过紧张激烈的对抗，这三辆车同时冲过终点线。由于无法判定最终优胜者，组委会决定一个月后在加州洛杉矶召开一次只有这三辆车参加的殊死战，只有最后的胜者才能捧得活塞杯。 信心满满麦坤和搭档拖车麦大叔早早启程。但是长时间的疲劳驾驶，令麦大叔不慎将麦坤丢在半路。麦坤东闯西撞，无意间来到了被众车遗忘的油车水镇。因躲避警长的追捕，麦坤毁坏了小镇的马路。在法官哈迪逊韩大夫和律师保时捷莎莉的裁决下，他被迫留在这里修路。短短几天相处，麦坤和小镇的居民渐渐融洽起来，同时他也爱上了美丽的莎莉。只不过，路终有修完的时候，未完的比赛仍在等待着他……"
  },
  "download_info": {
    "bt": {
      "row_title": [
        "电视 赛车总动员 1.5 G",
        "外链 赛车总动员.蓝光720P [6.7G]"
      ],
      "format_title": [
        "赛车总动员",
        "赛车总动员.蓝光720P"
      ],
      "format_size": [
        "1.5G",
        "6.7G"
      ],
      "download_link": [
        "thunder://QUFodHRwOi8vZGwxNTAuODBzLmltOjkyMC8xNzEwL+i1m+i9puaAu+WKqOWRmC/otZvovabmgLvliqjlkZgubXA0Wlo=",
        "magnet:?xt=urn:btih:f852d6d8be97a50864c68f52db852d63475317db&dn=Cars.2006.Blu-Ray.720p.MultiAudio.AC3.x264-beAst&tr="
      ]
    },
    "hd": {
      "download_info": {
        "hd": {
          "row_title": [
            "手机 赛车总动员 514.0 M"
          ],
          "format_title": [
            "赛车总动员"
          ],
          "format_size": [
            "514.0M"
          ],
          "download_link": [
            "thunder://QUFodHRwOi8vZGwyMy44MHMuaW06OTIwLzE2MDEv6LWb6L2m5oC75Yqo5ZGYL+i1m+i9puaAu+WKqOWRmF9oZC5tcDRaWg=="
          ]
        }
      }
    }
  },
  "url": "http://www.80s.tw/movie/1173",
  "title": "赛车总动员 (2006)高清mp4迅雷下载-80s手机电影"
}
```

# LICENCE
MIT
