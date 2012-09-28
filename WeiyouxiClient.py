import urllib
import urllib2
import json
import hashlib
import time

'''
Python SKD for Sina Weiyouxi.

usage:
try:
    w = WeiyouxiClient(source, secret, params)
except Exception, e:
    print e
else:
    user_info = w.get('user/show', {'uid': 1936344094})
    print user_info
    
    
source: your app key            |   unique identifier of an app
secret: your app secret         |   distinguish secret of an app
params: HTTP GET parameters
        When a user click a game in Weibo.com, an iframe will appear in this
        page. iframe src points to the GAME REAL URL.
        there are some GET params:
        
        wyx_user_id
        wyx_session_key
        wyx_create
        wyx_expire
        wyx_signature
        
        
        get this params from web framework, and fill up a param dict.
'''



class WeiyouxiClient(object):
    def __init__(self, source=None, secret=None, params={}):
        self.source = source    # app key
        self.secret = secret    # app secret
        self.params = params    # params includes wyx_user_id, wyx_session_key,
                                # wyx_create, wyx_signature keys.
        
        if not self.source or not self.secret:
            raise Exception, 'Need App Key and App Secret'
        
        if not self.params:
            raise Exception, 'params not defined'
        
        self.PREFIX_PARAM = 'wyx_'
        self.VERSION = '0.0.2'
        self.apiUrl = 'http://api.weibo.com/game/1'
        self.userAgent = 'Weiyouxi Agent Alpha 0.0.1'
        #self.connectTimeout = 30   ----   I don't know what this setting means
        self.timeout = 30
        self._httpCode = '<not set>'
        self._httpInfo = '<not set>'
        
        # user session
        self._session = {
            'sessionKey': None,
            'userId': None,
            'create': None,
            'expire': None,
        }
        
        
        self.sessionKey = self.params.get('%s%s' % (self.PREFIX_PARAM,
                                                    'session_key'),
                                          None)
        self.signature = self.params.get('%s%s' % (self.PREFIX_PARAM,
                                                   'signature'),
                                         None)
        
        # check signature and session key
        if self.sessionKey or self.signature:
            self.checkSignature()
            self.checkSessionKey()
        
    # Used when unable to get parameters from params
    # set and check signature
    def setAndCheckSignature(self, signature, getParams={}):
        self.signature = signature
        self.checkSignature(getParams)
        
    def checkSignature(self, getParams={}):
        if not self.signature:
            raise Exception, 'Require signature'
        
        temp = getParams.copy() if getParams else self.params.copy()
            
        temp.pop('%s%s' % (self.PREFIX_PARAM, 'signature'), None)
        new_params = {}
        for k, v in temp.items():
            if k.startswith(self.PREFIX_PARAM):
                new_params[k] = v
                
        baseString = self.buildBaseString(new_params)
        
        #print '<Client>', baseString
        #print hashlib.sha1(baseString + self.secret).hexdigest()
        
        if self.signature != hashlib.sha1(baseString + self.secret).hexdigest():
            raise Exception, 'Signature Error'
        
    def setAndCheckSessionKey(self, session_key):
        self.sessionKey = session_key
        self.checkSessionKey()
        
        
    def checkSessionKey(self):
        if not self.sessionKey:
            raise Exception, 'Require session key'
        
        self._session['sessionKey'] = self.sessionKey
        sessionArr = self._session['sessionKey'].split('_')
        if len(sessionArr) < 3:
            raise Exception, 'Session key error'
        
        expire = sessionArr[1]
        userId = sessionArr[2]
        
        self._session['userId'] = int(userId)
        self._session['create'] = self.params.get(self.PREFIX_PARAM + 'create',
                                                 None)
        self._session['expire'] = self.params.get(self.PREFIX_PARAM + 'expire',
                                                 expire)
            
            
    def getUserId(self):
        return self._session['userId']
        
    def getSession(self):
        return self._session
        
        
    # call api.
    # api :  string, api name
    # data : dict, params except source, session_key, timestamp, signature
    # return format: dict.
        
    def post(self, api, data={}):
        result = self.http('%s/%s' % (self.apiUrl, api),
                           self.buildQueryParamStr(data), 1)
        return json.loads(result)
    
    def get(self, api, data={}):
        result = self.http('%s/%s' % (self.apiUrl, api),
                           self.buildQueryParamStr(data), 0)
        return json.loads(result)
    
    def buildQueryParamStr(self, data):
        timestamp = str(time.time())
        new_params = {'source': self.source,
                      'timestamp': timestamp,}
        if self.sessionKey:
            new_params['session_key'] = self.sessionKey
        new_params.update(data)
        
        baseString = self.buildBaseString(new_params)
        signature = hashlib.sha1(baseString + self.secret).hexdigest()
        return '%s&signature=%s' % (baseString, signature)
        
        
    def buildBaseString(self, new_params):
        if not new_params:
            return ''
        
        couple_list = map(lambda a: '%s=%s' % (urllib.quote_plus(str(a[0])),
                                               urllib.quote_plus(str(a[1]))),
                          new_params.items())
        
        couple_list.sort()
        return '&'.join(couple_list)
        
    
    def http(self, url, dataStr='', isPost=False):
        #print '<http>', dataStr
        if(isPost):
            req = urllib2.Request(url, dataStr)
        else:
            req = urllib2.Request('%s?%s' % (url, dataStr))
            
        req.add_header('User-Agent', self.userAgent)
        response = urllib2.urlopen(req, timeout=self.timeout)
        
        self._httpCode = response.code
        return response.read()
        
        # self._httpInfo = ???
    
    def setUserAgent(self, agent=''):
        self.userAgent = agent
        
    def setConnectTimeout(timeout=30):
        # I don't know connectTimeout how to use.
        pass
        
    def setTimeout(timeout=30):
        self.timeout = timeout
        
    def getHttpCode(self):
        return self._httpCode
    
    def getHttpInfo(self):
        return self._httpInfo
        
        
    #define this perperties, It' more convenient for use in Python Program
    @property
    def httpCode(self):
        return self._httpCode
    
    @property
    def httpInfo(self):
        return self._httpInfo
    
    @property
    def userId(self):
        return self._session['userId']
        
    @property
    def session(self):
        return self._session