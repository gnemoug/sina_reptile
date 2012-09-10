#!/usr/bin/python
#-*-coding:utf8-*-

from pprint import pprint
from weibopy.auth import OAuthHandler
from weibopy.api import API
from weibopy.binder import bind_api
from weibopy.error import WeibopError
import time,os,pickle,sys
import logging.config 
from multiprocessing import Process
from pymongo import Connection


mongo_addr = 'localhost'
mongo_port = 27017
db_name = 'weibo'

class Sina_reptile():
    """
    爬取sina微博数据
    """

    def __init__(self,consumer_key,consumer_secret):
        self.consumer_key,self.consumer_secret = consumer_key,consumer_secret
        self.connection = Connection(mongo_addr,mongo_port)
        self.db = self.connection[db_name]
        self.collection_userprofile = self.db['userprofile']
        self.collection_statuses = self.db['statuses']

    def getAtt(self, key):
        try:
            return self.obj.__getattribute__(key)
        except Exception, e:
            print e
            return ''

    def getAttValue(self, obj, key):
        try:
            return obj.__getattribute__(key)
        except Exception, e:
            print e
            return ''

    def auth(self):
        """
        用于获取sina微博  access_token 和access_secret
        """
        if len(self.consumer_key) == 0:
            print "Please set consumer_key"
            return
        
        if len(self.consumer_key) == 0:
            print "Please set consumer_secret"
            return
        
        self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        auth_url = self.auth.get_authorization_url()
        print 'Please authorize: ' + auth_url
        verifier = raw_input('PIN: ').strip()
        self.auth.get_access_token(verifier)
        self.api = API(self.auth)

    def setToken(self, token, tokenSecret):
        """
        通过oauth协议以便能获取sina微博数据
        """
        self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.setToken(token, tokenSecret)
        self.api = API(self.auth)

    def get_userprofile(self,id):
        """
        获取用户基本信息
        """
        try:
            userprofile = {}
            userprofile['id'] = id
            user = self.api.get_user(id)
            self.obj = user
            
            userprofile['screen_name'] = self.getAtt("screen_name")
            userprofile['name'] = self.getAtt("name")
            userprofile['province'] = self.getAtt("province")
            userprofile['city'] = self.getAtt("city")
            userprofile['location'] = self.getAtt("location")
            userprofile['description'] = self.getAtt("description")
            userprofile['url'] = self.getAtt("url")
            userprofile['profile_image_url'] = self.getAtt("profile_image_url")
            userprofile['domain'] = self.getAtt("domain")
            userprofile['gender'] = self.getAtt("gender")
            userprofile['followers_count'] = self.getAtt("followers_count")
            userprofile['friends_count'] = self.getAtt("friends_count")
            userprofile['statuses_count'] = self.getAtt("statuses_count")
            userprofile['favourites_count'] = self.getAtt("favourites_count")
            userprofile['created_at'] = self.getAtt("created_at")
            userprofile['following'] = self.getAtt("following")
            userprofile['allow_all_act_msg'] = self.getAtt("allow_all_act_msg")
            userprofile['geo_enabled'] = self.getAtt("geo_enabled")
            userprofile['verified'] = self.getAtt("verified")

#            for i in userprofile:
#                print type(i),type(userprofile[i])
#                print i,userprofile[i]
#            

        except WeibopError, e:      #捕获到的WeibopError错误的详细原因会被放置在对象e中
            print "error occured when access userprofile use user_id:",id
            print "Error:",e
            log.error("Error occured when access userprofile use user_id:{0}\nError:{1}".format(id, e),exc_info=sys.exc_info())
            return None
            
        return userprofile

    def get_specific_weibo(self,id):
        """
        获取用户最近发表的50条微博
        """
        statusprofile = {}
        statusprofile['id'] = id
        try:
            #重新绑定get_status函数
            get_status = bind_api( path = '/statuses/show/{id}.json', 
                                 payload_type = 'status',
                                 allowed_param = ['id'])
        except:
            return "**绑定错误**"
        status = get_status(self.api,id)
        self.obj = status
        statusprofile['created_at'] = self.getAtt("created_at")
        statusprofile['text'] = self.getAtt("text")
        statusprofile['source'] = self.getAtt("source")
        statusprofile['favorited'] = self.getAtt("favorited")
        statusprofile['truncated'] = self.getAtt("ntruncatedame")
        statusprofile['in_reply_to_status_id'] = self.getAtt("in_reply_to_status_id")
        statusprofile['in_reply_to_user_id'] = self.getAtt("in_reply_to_user_id")
        statusprofile['in_reply_to_screen_name'] = self.getAtt("in_reply_to_screen_name")
        statusprofile['thumbnail_pic'] = self.getAtt("thumbnail_pic")
        statusprofile['bmiddle_pic'] = self.getAtt("bmiddle_pic")
        statusprofile['original_pic'] = self.getAtt("original_pic")
        statusprofile['geo'] = self.getAtt("geo")
        statusprofile['mid'] = self.getAtt("mid")
        statusprofile['retweeted_status'] = self.getAtt("retweeted_status")
        return statusprofile

    def get_latest_weibo(self,user_id,count):
        """
        获取用户最新发表的count条数据
        """
        statuses,statusprofile = [],{}
        try:            #error occur in the SDK
            timeline = self.api.user_timeline(count=count, user_id=user_id)
        except Exception as e:
            print "error occured when access status use user_id:",user_id
            print "Error:",e
            log.error("Error occured when access status use user_id:{0}\nError:{1}".format(user_id, e),exc_info=sys.exc_info())
            return None
        for line in timeline:
            self.obj = line
            statusprofile['usr_id'] = user_id
            statusprofile['id'] = self.getAtt("id")
            statusprofile['created_at'] = self.getAtt("created_at")
            statusprofile['text'] = self.getAtt("text")
            statusprofile['source'] = self.getAtt("source")
            statusprofile['favorited'] = self.getAtt("favorited")
            statusprofile['truncated'] = self.getAtt("ntruncatedame")
            statusprofile['in_reply_to_status_id'] = self.getAtt("in_reply_to_status_id")
            statusprofile['in_reply_to_user_id'] = self.getAtt("in_reply_to_user_id")
            statusprofile['in_reply_to_screen_name'] = self.getAtt("in_reply_to_screen_name")
            statusprofile['thumbnail_pic'] = self.getAtt("thumbnail_pic")
            statusprofile['bmiddle_pic'] = self.getAtt("bmiddle_pic")
            statusprofile['original_pic'] = self.getAtt("original_pic")
            statusprofile['geo'] = repr(pickle.dumps(self.getAtt("geo"),pickle.HIGHEST_PROTOCOL))
            statusprofile['mid'] = self.getAtt("mid")
            statusprofile['retweeted_status'] = repr(pickle.dumps(self.getAtt("retweeted_status"),pickle.HIGHEST_PROTOCOL))
            statuses.append(statusprofile)

#            print '*************',type(statusprofile['retweeted_status']),statusprofile['retweeted_status'],'********'
#        for j in statuses:
#            for i in j:
#                print type(i),type(j[i])
#                print i,j[i]

        return statuses

    def friends_ids(self,id):
        """
        获取用户关注列表id
        """
        next_cursor,cursor = 1,0
        ids = []
        while(0!=next_cursor):
            fids = self.api.friends_ids(user_id=id,cursor=cursor)
            self.obj = fids
            ids.extend(self.getAtt("ids"))
            cursor = next_cursor = self.getAtt("next_cursor")
            previous_cursor = self.getAtt("previous_cursor")
        return ids

    def manage_access(self):
        """
        管理应用访问API速度,适时进行沉睡
        """
        info = self.api.rate_limit_status()
        self.obj = info
        sleep_time = round( (float)(self.getAtt("reset_time_in_seconds"))/self.getAtt("remaining_hits"),2 ) if self.getAtt("remaining_hits") else self.getAtt("reset_time_in_seconds")
        print self.getAtt("remaining_hits"),self.getAtt("reset_time_in_seconds"),self.getAtt("hourly_limit"),self.getAtt("reset_time")
        print "sleep time:",sleep_time,'pid:',os.getpid()
        time.sleep(sleep_time + 1.5)

    def save_data(self,userprofile,statuses):
        self.collection_statuses.insert(statuses)
        self.collection_userprofile.insert(userprofile)

def reptile(sina_reptile,userid):
    ids_num,ids,new_ids,return_ids = 1,[userid],[userid],[]
    while(ids_num <= 10000000):
        next_ids = []
        for id in new_ids:
            try:
                sina_reptile.manage_access()
                return_ids = sina_reptile.friends_ids(id)
                ids.extend(return_ids)
                userprofile = sina_reptile.get_userprofile(id)
                statuses = sina_reptile.get_latest_weibo(count=50, user_id=id)
                if statuses is None or userprofile is None:
                    continue
                sina_reptile.save_data(userprofile,statuses)
            except Exception as e:
                log.error("Error occured in reptile,id:{0}\nError:{1}".format(id, e),exc_info=sys.exc_info())
                time.sleep(60)
                continue
            ids_num+=1
            print ids_num
            if(ids_num >= 10000000):break
            next_ids.extend(return_ids)
        next_ids,new_ids = new_ids,next_ids

def run_crawler(consumer_key,consumer_secret,key,secret,userid):
    try:
        sina_reptile = Sina_reptile(consumer_key,consumer_secret)
        sina_reptile.setToken(key, secret)
        reptile(sina_reptile,userid)
        sina_reptile.connection.close()
    except Exception as e:
        print e
        log.error("Error occured in run_crawler,pid:{1}\nError:{2}".format(os.getpid(), e),exc_info=sys.exc_info())

if __name__ == "__main__":
    logging.config.fileConfig("logging.conf")
    log = logging.getLogger('logger_sina_reptile')
    with open('test.txt') as f:
        for i in f.readlines():
            j = i.strip().split(' ')
            p = Process(target=run_crawler, args=(j[0],j[1],j[2],j[3],j[4]))
            p.start()

#    sina_reptile = Sina_reptile('3105114937','985e8f106a5db148d1a96abfabcd9043')
##    sina_reptile.auth()
#    sina_reptile.setToken("e42c9ac01abbb0ccf498689f70ecce56", "dee15395b02e87eedc56e380807528a8")
##    sina_reptile.get_userprofile("1735950160")
##    sina_reptile.get_specific_weibo("3408234545293850")
##    sina_reptile.get_latest_weibo(count=50, user_id="1735950160")
##    sina_reptile.friends_ids("1404376560")
#    reptile(sina_reptile)
#    sina_reptile.manage_access()
