# -*- coding: utf-8 -*-
import xbmcvfs
import os,xbmc,xbmcaddon,re,sys,xbmcgui,json
from bs4 import BeautifulSoup
import urllib2,urllib,requests,time,xbmcplugin,re,datetime
import cPickle as pickle
ALL_TAGS = ['link','f4m','sportsdevil','dm','vimeo','yt-dl','Lstreamer','utube','imdb','p2p','f4m''vaughn','ilive','veetle','ftv']

addon = xbmcaddon.Addon('plugin.video.live.proyectoluzdigital')
profile = xbmc.translatePath(addon.getAddonInfo('profile').decode('utf-8'))
communityfiles = os.path.join(profile, 'LivewebTV')
cacheDir = os.path.join(profile, 'cachedir')
cookie_file = os.path.join(profile, 'cookies')
headers=dict({'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 Firefox/32.0'})

def match1(text, *patterns):
    """Scans through a string for substrings matched some patterns (first-subgroups only).

    Args:
        text: A string to be scanned.
        patterns: Arbitrary number of regex patterns.

    Returns:
        When only one pattern is given, returns a string (None if no match found).
        When more than one pattern are given, returns a list of strings ([] if no match found).
    """

    if len(patterns) == 1:
        pattern = patterns[0]
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        ret = []
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                ret.append(match.group(1))
        return ret



def get_soup(url,content=None,ref=None,post=None):
    if not url == '' :
        if ref:
            print 'we got ref',ref
            headers.update({'Referer': '%s'%ref})
        else:
            headers.update({'Referer': '%s'%url})
        req = urllib2.Request(url,None,headers)
        resp = urllib2.urlopen(req)
        content = resp.read()
        resp.close()
    try:
        soup = BeautifulSoup(content,'html.parser')
        print 'using html.parser'
    except:
        soup = BeautifulSoup(content)


    print len(soup)

    return soup

def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))


def notification(header="", message="", sleep=3000):
    """ Will display a notification dialog with the specified header and message,
    in addition you can set the length of time it displays in milliseconds and a icon image.
    """
    xbmc.executebuiltin("XBMC.Notification(%s,%s,%i)" % ( header, message, sleep ))
def makeRequest(url,referer=None,post=None,body={}):

    if referer:
        headers.update=({'Referer':referer})
    if post:
        r = requests.post(url,data=body,headers=headers,verify=False)
        return r.text
    else:
        req = urllib2.Request(url,None,headers)
        response = urllib2.urlopen(req)
        data = response.read()
        response.close()
        return data
def cache(url, duration=0,post=None,other_head='',body={},ref=None,getcookie=None,need_cookie=None,save_cookie=None,build_soup=None,debug=False,repeat=1):
    UAhead=dict({'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 Firefox/32.0'})
    headers=dict({'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 Firefox/32.0'})
    print url

    if addon.getSetting('nocache') == 'true':
        duration = 0
    new = 'true'
    if ref:
        headers.update({'Referer': '%s'%ref})
    #else:
    #    headers.update({'Referer': '%s'%url})
    if len(body) > 1:
        f_name_posturl = url + json.dumps(body)
        cacheFile = os.path.join(cacheDir, (''.join(c for c in unicode(f_name_posturl, 'utf-8') if c not in '/\\:?"*|<>')).strip())
    else:
        cacheFile = os.path.join(cacheDir, (''.join(c for c in unicode(url.encode('utf-8'), 'utf-8') if c not in '/\\:?"*|<>')).strip())
    if need_cookie:
        cookie_jar = os.path.join(cookie_file, '%s' %need_cookie) #need cookie is cookie file name that had
                                                                # had saved befor
        with open( cookie_jar, "rb") as f:
            cookiess = pickle.load(f)
    for i in range(repeat): # if range is 1 loop through once
            if os.path.exists(cacheFile) and duration!=0 and (time.time()-os.path.getmtime(cacheFile) < 60*60*24*duration)and os.path.getsize(cacheFile) > 5:
                fh = xbmcvfs.File(cacheFile, 'r')
                content = fh.read()
                fh.close()
                new = 'false'
                return content,new
            elif post and need_cookie:

                r = requests.post(url,data=body,cookies=cookiess,headers=headers,verify=False)
            elif post:

                r = requests.post(url,data=body,headers=headers,verify=False)
            elif need_cookie:
                r = requests.get(url,cookies=cookiess,headers=headers,verify=False)

            else:
                #print headers
                r = requests.get(url,headers=headers,verify=False)

            #if not r.raise_for_status() :
            try:
                content = r.text
            except Exception:
                print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++'
                print 'debug for the url:%s' %url
                print 'status_code:',r.status_code
                print 'Response Headers server sent::',r.headers
                print 'Header sent to server:',r.request.headers
                print 'The cookies are:',r.headers['set-cookie']
                print '========================================================='
                return None
    if duration != 0:
        fh = xbmcvfs.File(cacheFile, 'w')
        fh.write(str(removeNonAscii(content))) #problem to save ilive : add str
        fh.close()
    if save_cookie:
        #print r
        Cookie =  r.cookies.get_dict()      #str(r.headers['set-cookie'])
        if len(Cookie) < 1:
            print 'Saving cookie failed, see debug below'
            debug = True
        print 'saving cookies for ',Cookie
            #notification('Login Succes','Succesfully loged_in to doridro.Com as %s ::.'%Doridro_USER,2000)
            #return r.cookies
        cookie_jar = os.path.join(cookie_file, '%s' %save_cookie)
        with open( cookie_jar, "wb" ) as ff:
            pickle.dump( Cookie, ff )
            ff.close()
        new = Cookie
    if debug:
        print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++'
        print 'debug for the url:%s' %url
        print 'status_code:',r.status_code
        print 'Response Headers server sent::',r.headers
        print 'Header sent to server:',r.request.headers
        print 'The cookies are:',r.headers['set-cookie']
        print '========================================================='
    if build_soup:
        content = get_soup('',content)
    if getcookie:
        new = r.headers['set-cookie']
    return content,new
def clean(text):
    command={'\r':'','\n':'','\t':'','&nbsp;':'','&#231;':'�','&#201;':'�','&#233;':'�','&#250;':'�','&#227;':'�','&#237;':'�','&#243;':'�','&#193;':'�','&#205;':'�','&#244;':'�','&#224;':'�','&#225;':'�','&#234;':'�','&#211;':'�','&#226;':'�'}
    regex = re.compile("|".join(map(re.escape, command.keys())))
    return regex.sub(lambda mo: command[mo.group(0)], text)

def getEpocTime(milli=None):
    import time
    if milli:
        return str(int(time.time()*1000))
    else:
        return str(int(time.time()))

def timeStamped(fname, fmt='{fname}[COLOR yellow]%d-%m-%Y-@-%H-%M[/COLOR]'):
    return datetime.datetime.now().strftime(fmt).format(fname=fname)

