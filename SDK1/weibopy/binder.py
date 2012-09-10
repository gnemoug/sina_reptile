
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

import httplib
import urllib
import time
import re
from weibopy.error import WeibopError
from weibopy.utils import convert_to_utf8_str

re_path_template = re.compile('{\w+}')


def bind_api(**config):

    class APIMethod(object):
        
        path = config['path']
        payload_type = config.get('payload_type', None)
        payload_list = config.get('payload_list', False)
        allowed_param = config.get('allowed_param', [])
        method = config.get('method', 'GET')
        require_auth = config.get('require_auth', False)
        search_api = config.get('search_api', False)
                
        def __init__(self, api, args, kargs):
            # If authentication is required and no credentials
            # are provided, throw an error.
            if self.require_auth and not api.auth:
                raise WeibopError('Authentication required!')

            self.api = api
            self.post_data = kargs.pop('post_data', None)
            self.retry_count = kargs.pop('retry_count', api.retry_count)
            self.retry_delay = kargs.pop('retry_delay', api.retry_delay)
            self.retry_errors = kargs.pop('retry_errors', api.retry_errors)
            self.headers = kargs.pop('headers', {})
            self.build_parameters(args, kargs)
            # Pick correct URL root to use
            if self.search_api:
                self.api_root = api.search_root
            else:
                self.api_root = api.api_root
            
            # Perform any path variable substitution
            self.build_path()

            if api.secure:
                self.scheme = 'https://'
            else:
                self.scheme = 'http://'

            if self.search_api:
                self.host = api.search_host
            else:
                self.host = api.host

            # Manually set Host header to fix an issue in python 2.5
            # or older where Host is set including the 443 port.
            # This causes Twitter to issue 301 redirect.
            # See Issue http://github.com/joshthecoder/tweepy/issues/#issue/12
            self.headers['Host'] = self.host

        def build_parameters(self, args, kargs):
            self.parameters = {}
            for idx, arg in enumerate(args):
                try:
                    self.parameters[self.allowed_param[idx]] = convert_to_utf8_str(arg)
                except IndexError:
                    raise WeibopError('Too many parameters supplied!')

            for k, arg in kargs.items():
                if arg is None:
                    continue
                if k in self.parameters:
                    raise WeibopError('Multiple values for parameter %s supplied!' % k)

                self.parameters[k] = convert_to_utf8_str(arg)

        def build_path(self):
            for variable in re_path_template.findall(self.path):
                name = variable.strip('{}')

                if name == 'user' and self.api.auth:
                    value = self.api.auth.get_username()
                else:
                    try:
                        value = urllib.quote(self.parameters[name])
                    except KeyError:
                        raise WeibopError('No parameter value found for path variable: %s' % name)
                    del self.parameters[name]

                self.path = self.path.replace(variable, value)

        def execute(self):
            # Build the request URL
            url = self.api_root + self.path
            if self.api.source is not None:
                self.parameters.setdefault('source',self.api.source)
            
            if len(self.parameters):
                if self.method == 'GET' or self.method == 'DELETE':
                    url = '%s?%s' % (url, urllib.urlencode(self.parameters))  
                else:
                    self.headers.setdefault("User-Agent","python")
                    if self.post_data is None:
                        self.headers.setdefault("Accept","text/html")                        
                        self.headers.setdefault("Content-Type","application/x-www-form-urlencoded")
                        self.post_data = urllib.urlencode(self.parameters)           
            # Query the cache if one is available
            # and this request uses a GET method.
            if self.api.cache and self.method == 'GET':
                cache_result = self.api.cache.get(url)
                # if cache result found and not expired, return it
                if cache_result:
                    # must restore api reference
                    if isinstance(cache_result, list):
                        for result in cache_result:
                            result._api = self.api
                    else:
                        cache_result._api = self.api
                    return cache_result
                #urllib.urlencode(self.parameters)
            # Continue attempting request until successful
            # or maximum number of retries is reached.
            sTime = time.time()
            retries_performed = 0
            while retries_performed < self.retry_count + 1:
                # Open connection
                # FIXME: add timeout
                if self.api.secure:
                    conn = httplib.HTTPSConnection(self.host)
                else:
                    conn = httplib.HTTPConnection(self.host)
                # Apply authentication
                if self.api.auth:
                    self.api.auth.apply_auth(
                            self.scheme + self.host + url,
                            self.method, self.headers, self.parameters
                    )
                # Execute request
                try:
                    conn.request(self.method, url, headers=self.headers, body=self.post_data)
                    resp = conn.getresponse()
                except Exception, e:
                    raise WeibopError('Failed to send request: %s' % e + "url=" + str(url) +",self.headers="+ str(self.headers))

                # Exit request loop if non-retry error code
                if self.retry_errors:
                    if resp.status not in self.retry_errors: break
                else:
                    if resp.status == 200: break

                # Sleep before retrying request again
                time.sleep(self.retry_delay)
                retries_performed += 1

            # If an error was returned, throw an exception
            body = resp.read()
            self.api.last_response = resp
            if self.api.log is not None:
                requestUrl = "URL:http://"+ self.host + url
                eTime = '%.0f' % ((time.time() - sTime) * 1000)
                postData = ""
                if self.post_data is not None:
                    postData = ",post:"+ self.post_data[0:500]
                self.api.log.debug(requestUrl +",time:"+ str(eTime)+ postData+",result:"+ body )
            if resp.status != 200:
                try:
                    json = self.api.parser.parse_error(self, body)
                    error_code =  json['error_code']
                    error =  json['error']
                    error_msg = 'error_code:' + error_code +','+ error
                except Exception:
                    error_msg = "Weibo error response: status code = %s" % resp.status
                raise WeibopError(error_msg)
            
            # Parse the response payload
            result = self.api.parser.parse(self, body)
            conn.close()

            # Store result into cache if one is available.
            if self.api.cache and self.method == 'GET' and result:
                self.api.cache.store(url, result)
            return result

    def _call(api, *args, **kargs):

        method = APIMethod(api, args, kargs)
        return method.execute()


    # Set pagination mode
    if 'cursor' in APIMethod.allowed_param:
        _call.pagination_mode = 'cursor'
    elif 'page' in APIMethod.allowed_param:
        _call.pagination_mode = 'page'

    return _call

