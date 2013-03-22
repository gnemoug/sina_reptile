目标：
爬取新浪微博的1000w用户，爬虫运行时间一周
数据存入mongodb，数据库自行设计，需要满足能存储如下用户基本信息 

 "users": [
        {
            "id": 1404376560,
            "screen_name": "zaku",
            "name": "zaku",
            "province": "11",
            "city": "5",
            "location": "北京 朝阳区",
            "description": "人生五十年，乃如梦如幻；有生斯有死，壮士复何憾。",
            "url": "http://blog.sina.com.cn/zaku",
            "profile_image_url": "http://tp1.sinaimg.cn/1404376560/50/0/1",
            "domain": "zaku",
            "gender": "m",
            "followers_count": 1204,
            "friends_count": 447,
            "statuses_count": 2908,
            "favourites_count": 0,
            "created_at": "Fri Aug 28 00:00:00 +0800 2009",
            "following": false,
            "allow_all_act_msg": false,
            "remark": "",
            "geo_enabled": true,
            "verified": false,
            "status": {
                "created_at": "Tue May 24 18:04:53 +0800 2011",
                "id": 11142488790,
                "text": "我的相机到了。",
                "source": "<a href="http://weibo.com" rel="nofollow">新浪微博</a>",
                "favorited": false,
                "truncated": false,
                "in_reply_to_status_id": "",
                "in_reply_to_user_id": "",
                "in_reply_to_screen_name": "",
                "geo": null,
                "mid": "5610221544300749636",
                "annotations": [],
                "reposts_count": 5,
                "comments_count": 8
            },
            "allow_all_comment": true,
            "avatar_large": "http://tp1.sinaimg.cn/1404376560/180/0/1",
            "verified_reason": "",
            "follow_me": false,
            "online_status": 0,
            "bi_followers_count": 215
        },
        ...
    ],
    "next_cursor": 5,
    "previous_cursor": 0,
    "total_number": 668
}

同时还能存储用户的微博信息，如下所示

{
    "statuses": [
        {
            "created_at": "Tue May 31 17:46:55 +0800 2011",
            "id": 11488058246,
            "text": "求关注。"，
            "source": "<a href="http://weibo.com" rel="nofollow">新浪微博</a>",
            "favorited": false,
            "truncated": false,
            "in_reply_to_status_id": "",
            "in_reply_to_user_id": "",
            "in_reply_to_screen_name": "",
            "geo": null,
            "mid": "5612814510546515491",
            "reposts_count": 8,
            "comments_count": 9,
            "annotations": [],
            
        },
        ...
    ],
    "previous_cursor": 0,
    "next_cursor": 11488013766,
    "total_number": 81655
}

一切以用户为单位，需要存储1000w用户的基本信息+用户发过的50条最近微博
