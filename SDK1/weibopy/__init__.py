
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

"""
weibo API library
"""
__version__ = '1.5'
__author__ = 'Joshua Roesslein'
__license__ = 'MIT'

from weibopy.models import Status, User, DirectMessage, Friendship, SavedSearch, SearchResult, ModelFactory, IDSModel
from weibopy.error import WeibopError
from weibopy.api import API
from weibopy.cache import Cache, MemoryCache, FileCache
from weibopy.auth import BasicAuthHandler, OAuthHandler
from weibopy.streaming import Stream, StreamListener
from weibopy.cursor import Cursor

# Global, unauthenticated instance of API
api = API()

def debug(enable=True, level=1):

    import httplib
    httplib.HTTPConnection.debuglevel = level

