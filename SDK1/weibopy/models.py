
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

from weibopy.utils import parse_datetime, parse_html_value, parse_a_href, \
        parse_search_datetime, unescape_html

class ResultSet(list):
    """A list like object that holds results from a Twitter API query."""


class Model(object):

    def __init__(self, api=None):
        self._api = api

    def __getstate__(self):
        # pickle
        pickle = dict(self.__dict__)
        del pickle['_api']  # do not pickle the API reference
        return pickle

    @classmethod
    def parse(cls, api, json):
        """Parse a JSON object into a model instance."""
        raise NotImplementedError

    @classmethod
    def parse_list(cls, api, json_list):
        """Parse a list of JSON objects into a result set of model instances."""
        results = ResultSet()
        for obj in json_list:
            results.append(cls.parse(api, obj))
        return results


class Status(Model):

    @classmethod
    def parse(cls, api, json):
#        print json
        status = cls(api)
        for k, v in json.items():
            if k == 'user':
                user = User.parse(api, v)
                setattr(status, 'author', user)
                setattr(status, 'user', user)  # DEPRECIATED
            elif k == 'screen_name':
                setattr(status, k, v)
            elif k == 'created_at':
                setattr(status, k, parse_datetime(v))
            elif k == 'source':
                if '<' in v:
                    setattr(status, k, parse_html_value(v))
                    setattr(status, 'source_url', parse_a_href(v))
                else:
                    setattr(status, k, v)
            elif k == 'retweeted_status':
                setattr(status, k, Status.parse(api, v))
            elif k == 'geo':
                setattr(status, k, Geo.parse(api, v))
            else:
                setattr(status, k, v)
        return status

    def destroy(self):
        return self._api.destroy_status(self.id)

    def retweet(self):
        return self._api.retweet(self.id)

    def retweets(self):
        return self._api.retweets(self.id)

    def favorite(self):
        return self._api.create_favorite(self.id)
class Geo(Model):

    @classmethod
    def parse(cls, api, json):
        geo = cls(api)
        if json is not None:
            for k, v in json.items():
                setattr(geo, k, v)
        return geo
    
class Comments(Model):

    @classmethod
    def parse(cls, api, json):
        comments = cls(api)
        for k, v in json.items():
            if k == 'user':
                user = User.parse(api, v)
                setattr(comments, 'author', user)
                setattr(comments, 'user', user)
            elif k == 'status':
                status = Status.parse(api, v)
                setattr(comments, 'user', status)
            elif k == 'created_at':
                setattr(comments, k, parse_datetime(v))
            elif k == 'reply_comment':
                setattr(comments, k, User.parse(api, v))
            else:
                setattr(comments, k, v)
        return comments

    def destroy(self):
        return self._api.destroy_status(self.id)

    def retweet(self):
        return self._api.retweet(self.id)

    def retweets(self):
        return self._api.retweets(self.id)

    def favorite(self):
        return self._api.create_favorite(self.id)

class User(Model):

    @classmethod
    def parse(cls, api, json):
        user = cls(api)
        for k, v in json.items():
            if k == 'created_at':
                setattr(user, k, parse_datetime(v))
            elif k == 'status':
                setattr(user, k, Status.parse(api, v))
            elif k == 'screen_name':
                setattr(user, k, v)
            elif k == 'following':
                # twitter sets this to null if it is false
                if v is True:
                    setattr(user, k, True)
                else:
                    setattr(user, k, False)
            else:
                setattr(user, k, v)
        return user

    @classmethod
    def parse_list(cls, api, json_list):
        if isinstance(json_list, list):
            item_list = json_list
        else:
            item_list = json_list['users']

        results = ResultSet()
        for obj in item_list:
            results.append(cls.parse(api, obj))
        return results

    def timeline(self, **kargs):
        return self._api.user_timeline(user_id=self.id, **kargs)

    def friends(self, **kargs):
        return self._api.friends(user_id=self.id, **kargs)

    def followers(self, **kargs):
        return self._api.followers(user_id=self.id, **kargs)

    def follow(self):
        self._api.create_friendship(user_id=self.id)
        self.following = True

    def unfollow(self):
        self._api.destroy_friendship(user_id=self.id)
        self.following = False

    def lists_memberships(self, *args, **kargs):
        return self._api.lists_memberships(user=self.screen_name, *args, **kargs)

    def lists_subscriptions(self, *args, **kargs):
        return self._api.lists_subscriptions(user=self.screen_name, *args, **kargs)

    def lists(self, *args, **kargs):
        return self._api.lists(user=self.screen_name, *args, **kargs)

    def followers_ids(self, *args, **kargs):
        return self._api.followers_ids(user_id=self.id, *args, **kargs)




class DirectMessage(Model):
    @classmethod
    def parse(cls, api, json):
        dm = cls(api)
        for k, v in json.items():
            if k == 'sender' or k == 'recipient':
                setattr(dm, k, User.parse(api, v))
            elif k == 'created_at':
                setattr(dm, k, parse_datetime(v))
            else:
                setattr(dm, k, v)
        return dm

class Friendship(Model):

    @classmethod
    def parse(cls, api, json):
       
        source = cls(api)
        for k, v in json['source'].items():
            setattr(source, k, v)

        # parse target
        target = cls(api)
        for k, v in json['target'].items():
            setattr(target, k, v)

        return source, target


class SavedSearch(Model):

    @classmethod
    def parse(cls, api, json):
        ss = cls(api)
        for k, v in json.items():
            if k == 'created_at':
                setattr(ss, k, parse_datetime(v))
            else:
                setattr(ss, k, v)
        return ss

    def destroy(self):
        return self._api.destroy_saved_search(self.id)


class SearchResult(Model):

    @classmethod
    def parse(cls, api, json):
        result = cls()
        for k, v in json.items():
            if k == 'created_at':
                setattr(result, k, parse_search_datetime(v))
            elif k == 'source':
                setattr(result, k, parse_html_value(unescape_html(v)))
            else:
                setattr(result, k, v)
        return result

    @classmethod
    def parse_list(cls, api, json_list, result_set=None):
        results = ResultSet()
        results.max_id = json_list.get('max_id')
        results.since_id = json_list.get('since_id')
        results.refresh_url = json_list.get('refresh_url')
        results.next_page = json_list.get('next_page')
        results.results_per_page = json_list.get('results_per_page')
        results.page = json_list.get('page')
        results.completed_in = json_list.get('completed_in')
        results.query = json_list.get('query')

        for obj in json_list['results']:
            results.append(cls.parse(api, obj))
        return results

class List(Model):

    @classmethod
    def parse(cls, api, json):
        lst = List(api)
        for k,v in json.items():
            if k == 'user':
                setattr(lst, k, User.parse(api, v))
            else:
                setattr(lst, k, v)
        return lst

    @classmethod
    def parse_list(cls, api, json_list, result_set=None):
        results = ResultSet()
        for obj in json_list['lists']:
            results.append(cls.parse(api, obj))
        return results

    def update(self, **kargs):
        return self._api.update_list(self.slug, **kargs)

    def destroy(self):
        return self._api.destroy_list(self.slug)

    def timeline(self, **kargs):
        return self._api.list_timeline(self.user.screen_name, self.slug, **kargs)

    def add_member(self, id):
        return self._api.add_list_member(self.slug, id)

    def remove_member(self, id):
        return self._api.remove_list_member(self.slug, id)

    def members(self, **kargs):
        return self._api.list_members(self.user.screen_name, self.slug, **kargs)

    def is_member(self, id):
        return self._api.is_list_member(self.user.screen_name, self.slug, id)

    def subscribe(self):
        return self._api.subscribe_list(self.user.screen_name, self.slug)

    def unsubscribe(self):
        return self._api.unsubscribe_list(self.user.screen_name, self.slug)

    def subscribers(self, **kargs):
        return self._api.list_subscribers(self.user.screen_name, self.slug, **kargs)

    def is_subscribed(self, id):
        return self._api.is_subscribed_list(self.user.screen_name, self.slug, id)

class JSONModel(Model):

    @classmethod
    def parse(cls, api, json):
        lst = JSONModel(api)
        for k,v in json.items():
            setattr(lst, k, v)
        return lst

class IDSModel(Model):
    @classmethod
    def parse(cls, api, json):
        ids = IDSModel(api)
        for k, v in json.items():            
            setattr(ids, k, v)
        return ids
    
class Counts(Model):
    @classmethod
    def parse(cls, api, json):
        ids = Counts(api)
        for k, v in json.items():            
            setattr(ids, k, v)
        return ids
class Trends(Model):
    @classmethod
    def parse(cls, api, json):
        ids = Trends(api)
        for k,v in json.items():
            setattr(ids, k , v)
        return ids
class Tags(Model):
    @classmethod
    def parse(cls, api, json):
        ts = Tags(api)
        for k,v in json.items():
            setattr(ts, k , v)
            #setattr(ts,"id",k)
        return ts   
                         
    
class ModelFactory(object):
    """
    Used by parsers for creating instances
    of models. You may subclass this factory
    to add your own extended models.
    """

    status = Status
    comments = Comments
    user = User
    direct_message = DirectMessage
    friendship = Friendship
    saved_search = SavedSearch
    search_result = SearchResult
    list = List
    json = JSONModel
    ids_list = IDSModel
    counts = Counts
    trends = Trends
    tags = Tags
