import urllib
import urllib2,cookielib
import datetime
import re 
import struct
import base64
import requests2 as requests
import traceback,sys,os,xbmc,xbmcaddon,xbmcgui
from t0mm0.common.net import Net
import simplejson as json
#import YDStreamExtractor
#import YDStreamUtils
import httplib2
import time
from bs4 import BeautifulSoup,SoupStrainer
import bs4
print bs4.__version__
addon = xbmcaddon.Addon('plugin.video.live.proyectoluzdigital')
addon_version = addon.getAddonInfo('version')
profile = xbmc.translatePath(addon.getAddonInfo('profile').decode('utf-8'))
LstDir = os.path.join(profile, 'xmldir')
communityfiles = os.path.join(profile, 'community files')
cacheDir = os.path.join(LstDir, 'cachedir')
page_cache = os.path.join(cacheDir, 'http_page_cache')
h = httplib2.Http(page_cache)
s = requests.Session()
#YDStreamExtractor.disableDASHVideo(True)
dialog = xbmcgui.Dialog()

headers=dict({'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 Firefox/32.0'})
print type(headers)
if not cacheDir.startswith(('smb://', 'nfs://', 'upnp://', 'ftp://')) and not os.path.isdir(cacheDir):
    os.mkdir(cacheDir)
if not os.path.isdir(page_cache):
    os.mkdir(page_cache)
if not os.path.isdir(page_cache):
    os.mkdir(communityfiles)

'''
<item><title>sky1 [cast247] </title>
<link>$doregex[play]</link>

<regex>
<name>play</name>
<expres>$pyFunction:myFunctions.cast247(page_data,'skysp1','www.kbps.tv')</expres>
<page></page>
<referer></referer>
</regex>
</item>'''
zoomtv_reg = r'''sg[:,'\s]+(.*?)[:,'\s]+ts[:,'\s]+(.*?)[:,'\s]+.*?flashplayer[:,'\s]+(.*?)[:,'\s]+streamer[:,'\s]+(.*?)[,'\s]+file[:,'\s]+(.*?)[:,'\s]+'''
castup = r'''SWFObject\([',:"\s]+(.*?)[',:"\s]+.*?file[',:"\s]+(.*?)[',:"\s]+.*?streamer[',"]+(.*?)[',"\s]+.*?token[',:"\s]+(.*?)[',:"\s]+'''
mips_lft_jan_pattern = '''(?<=SWFObject\()[,"'\s]+(.*?)[,"'\s]+.*?(?<=FlashVars)[,"'\s]+(.*?)[,"'\s]+'''
dcast_pa = '''(?<=flashplayer)[',:"\s]+(.*?)[',:"\s]+.*?(?=rtmpe?)(.*?)[\s"',]+'''
ilivee_regex = r'''getJSON\(\"(.*?)\",.*?flashplayer: \"(.*?)\".*?streamer: \"(.*?)\",.*file:\s*\"(.*?)\",'''
#stream9 = r'''getJSON\(\"(.*?)\",streamer: \"(.*?)\",.*file:\s*\"(.*?)\",'''
stream9= r'''getJSON\(\"(.*?)\",.*?\'streamer\': \"(.*?)\",.*?\'file\': \'(.*?)\'.*?src:\s*\'(.*?)\''''
hqstream_rtmp =r'''var.*\s(\d+);'''

def hqstream(page_data): #should be category name : football hockey as seen on site
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 Firefox/32.0','Referer':page_data}
    resp, content = h.request(page_data, "GET",headers=headers)
    soup = BeautifulSoup(content)
    final_url =''
    season =[]
    count = 0
    print len(soup)
    l = soup('script', {'language':'javascript'})
    for tag in l:
        #print tag.text
        r= re.compile(hqstream_rtmp,re.I).findall(tag.text)
        v = re_me(tag.text,r'''var v_part.*\'(.*?)\'''')
        print v
        ip1=str(int(r[0])/int(r[4]))
        ip2=str(int(r[1])/int(r[4]))
        ip3=str(int(r[2])/int(r[4]))
        ip4=str(int(r[3])/int(r[4]))
        rtmp = 'rtmp://'+ip1+'.' + ip2 + '.' + ip3 + '.' + ip4 + v
        if 'hqstream' in page_data:
            final_url =  rtmp+ ' swfUrl=http://filo.hqstream.tv/jwp6/jwplayer.flash.swf live=1 timeout=15 swfVfy=1 pageUrl=http://hqstream.tv'
        elif 'leton' in page_data:
            final_url =  rtmp+ ' swfUrl=http://files.leton.tv/jwplayer.flash.swf live=1 timeout=15 swfVfy=1 pageUrl='+page_data
        elif 'liveall' in page_data:
            final_url =  rtmp+ ' swfUrl=http://wds.liveall.tv/jwplayer.flash.swf live=1 timeout=15 swfVfy=1 pageUrl='+page_data
            
        return final_url
def jJcast(page_data,ref=None): #unpcaker
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 \
            Firefox/32.0','Referer':str(ref)}
    resp, content = h.request(page_data, "GET",headers=headers)
    soup = BeautifulSoup(content)
    final_url =''
    count = 0
    soup = BeautifulSoup(content)
    l = soup('script',{'type':'text/javascript'})# its a tag
    print type(l)
    for tag in l:
        if tag.find(text=re.compile('eval')):
            import jsunpack
            unpacker = jsunpack.unpack(tag.text)
            print unpacker
            r=re.compile(r'''push\((.*?)\)''').findall(unpacker)
            ook= urllib.unquote(''.join(r).replace('\'','').replace('\\',''))
            print ook
            rt = ook.split('rtmp')
            print rt
            return 'rtmp'+rt[1]+' playpath=' + rt[0] + ' swfUrl=http://jjcast.com/jw5/5.10.swf live=1 timeout=10 swfVfy=1 pageUrl=' + page_data 
                
def mips(channel,g,domain=None):
    url = 'http://www.mips.tv/embedplayer/'+channel+'/'+str(g)+'/600/450'
    print url
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 \
            Firefox/32.0','Referer':str(domain)}
    resp, content = h.request(url, "GET",headers=headers)
    m= re.compile(mips_lft_pattern,re.DOTALL).findall(content)
    if m:
        print m
        final_url = final_url + ' swfUrl=http://www.mips.tv' + m[0][0]
        print final_url

        final_url = ' playpath=' +fid + m[0][1] + final_url + ' live=true timeout=15 swfVfy=1' + ' pageUrl=' + url
        print final_url
        load = 'http://www.mips.tv:1935/loadbalancer'
        resp, content = h.request(load, "GET",headers=headers)
        rtmp = 'rtmp://' + re_me(content,r'''redirect=(.*?)\s''') +'/live/'
        final_url = rtmp + final_url + ' conn=S:OK tcommand=kaskatijaEkonomista;TRUE'
        return final_url
    else:
        notification('MIPS Link has failed','Link failed',1000)
def dcast(channel,domain=None):
    url = 'http://www.dcast.tv/embed.php?u=%s&vw=600&vh=450' %channel
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 \
            Firefox/32.0','Referer':str(domain)}
    resp, content = h.request(url, "GET",headers=headers)
    m= re.compile(dcast_pa).findall(content)
    print m

    ppath = m[0][1] +  ' swfUrl=' +m[0][0] #+ final_url + ' live=true timeout=15 swfVfy=1' + ' pageUrl=' + url

    other = ' swfVfy=1 timeout=15 live=true'
    final_url =  ppath + ' pageUrl=' + url + other
    print final_url
    return final_url
def extract_jscript(page_data,ref=None):
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 Firefox/32.0'}
    if ref:
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 Firefox/32.0','Referer':ref}
    resp, content = h.request(page_data, "GET",headers=headers)
    soup = BeautifulSoup(content)
    final_url =''
    season =[]
    count = 0
    #l = soup('script', {'language':'javascript'})
    l = soup('script', {'language':'Javascript'})# its a tag
    print type(l)
    print l

    for tag in l:
      
        r= re.compile(r'''SRC%3D%22(.*?)%22%3E''',re.I).findall(tag.text)
        url = urllib.unquote(r[0])
        print url
        if 'hqstream' in url or 'leton' in url or 'liveall' in url:
            final_url = hqstream(url)
            return final_url   
        if 'jjcast' in url:
            url = url.replace('embed','player')
            print url
            final_url = jJcast(url,page_data)
            return final_url

            

def extract_embed_id(page_data,ref=None):
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 Firefox/32.0'}
    if ref:
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 Firefox/32.0','Referer':ref}
    resp, content = h.request(page_data, "GET",headers=headers)
    soup = BeautifulSoup(content)
    final_url =''
    season =[]
    count = 0
    links =  soup('script',{'type':'text/javascript'})
    for link in links:
        if 'channel' in link.text:
                #try:
            print link.text
            ch=re.compile(r'''channel=\'(.*?)\',\s+[eg]+=\'(.*?)\'''').findall(link.text)
            print 'dddddddch', ch
            fid = ch[0][0].encode('utf-8')
            g = str(ch[0][1])
            if not fid is None:
                k= link.next_sibling.get('src','SRC')
            if k.find('liveflash') !=-1 or k.find('janjua') !=-1 or k.find('mips') !=-1 or k.find('ucaster'):
                k = k.split('/')
                src = k[2]
                final_url =liveflashtv(fid,g,src,domain=page_data)
            elif k.find('freedocast'):
                final_url = freedocast(fid,g,src,domain=page_data)
                
            return final_url 

        if link.find(text=re.compile('f?id')):
                fid= re_me(link.text,'''f?id=['"](.*?)["']''')
                fid = fid.encode('utf-8')
                print fid
                if not fid is None:
                    k= link.next_sibling.get('src','SRC')
                if k.find('playfooty') !=-1:
                    notification ('playfooty link found','resolving....')
                    final_url =playfooty(fid,domain=page_data)
                    return final_url 
                elif k.find('pt987') !=-1:
                    notification ('xuscacamusca link found','resolving....')
                    final_url =xuscacamusca(fid,domain=page_data)
                    return final_url
                elif k.find('flashtv') !=-1:
                    notification ('flashtv link found','resolving....')
                    final_url =flashtvco(fid,domain=page_data)
                    return final_url
                elif k.find('dcast') !=-1:
                    notification ('dcast link found','resolving....')
                    final_url =dcast(fid,domain=page_data)
                    return final_url
                elif k.find('castup') !=-1:
                    notification ('[COLOR yellow] Castup[/COLOR]] : Playable link found','resolving....')
                    final_url =castup(fid,domain=page_data)
                    return final_url
                elif k.find('btcast') !=-1:
                    notification ('[COLOR yellow] UKcast[/COLOR]] : Playable link found','resolving....')
                    final_url =ukcast(fid,domain=page_data)
                    return final_url
                elif k.find('zoomtv') !=-1:
                    ohj = re_me(content,r'''var ohj = (\d+);''')
                    print ohj
                    #pid= re_me(link.text,'''pid=['"](.*?)["']''')
                    notification ('[COLOR yellow] ZOOMTV[/COLOR]] : Playable link found','resolving....')
                    final_url =zoomtv(fid,ohj,domain=page_data)
                    return final_url
def ukcast(fid,domain=None):
    url = 'http://www.ukcast.co/embed.php?u=%s&vw=600&vh=430' %fid
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 \
                            Firefox/32.0','Referer':domain}
    resp, content = h.request(url, "GET",headers=headers)
    soup = BeautifulSoup(content)
    final_url =''
    count = 0
    soup = BeautifulSoup(content)
    l = soup('script')# its a tag
    print type(l)
    for tag in l:
        print tag.text
        if tag.find(text=re.compile('rtmpe?')):
            rtmp = re_me(tag.text,r'''str.*?"(.*?)"''')
            print rtmp
            rtmp = rtmp.replace('cdn','strm')
            final_url = rtmp + ' playpath=' +fid + ' swfUrl=http://ukcast.co/player//player.swf swfVfy=true live=1 timeout=15 pageUrl=' +url
            return final_url
            
                           
          
def zoomtv(fid,ohj,domain=None):
    print 'zoomtv'
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 \
                            Firefox/32.0','Referer':domain}
    pageUrl='http://www.zoomtv.me/embed.php?v=%s&vw=660&vh=450'
    url = 'http://www.zoomtv.me/embed.php?v=%s&vw=660&vh=450|cx=%s&lg=1&pid=2' %(fid,ohj)
    res,content = h.request(url,"POST",headers=headers)
    soup = BeautifulSoup(content)
    l = soup('script',{'type':'text/javascript'})# its a tag
    print type(l)
    for tag in l:
        if tag.find(text=re.compile('secure')):
            print tag.text
            r= re.compile(zoomtv_reg,re.DOTALL).findall(tag.text)
            print r
            final_url = r[0][3] + ' playpath='+r[0][4]
            print final_url
            final_url = final_url +' swfUrl='+r[0][2]+' conn=S:'+r[0][4]
            other =' conn=S:' + r[0][0] + ' conn=S:' + r[0][1] + ' conn=S:V&gt;JWhui^@2ESdu0?}&gt;AN live=1 timeout=15 token=Q!lrB@G1)ww(-dQ4J4 swfVfy=1 pageUrl=' +url
            print final_url
            return final_url +other
#http://www.castup.tv/embed_2.php?channel=23?hzsZF&vw=640&vh=440
        
def castup(channel,domain):      
    url = 'http://%s/embed_2.php?channel=%s&vw=640&vh=440'
    url = url %(domain,channel)
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 \
            Firefox/32.0','Referer':str(domain)}
    resp, content = h.request(url, "GET",headers=headers)    
    soup = BeautifulSoup(content)
    l = soup('script',{'type':'text/javascript'})# its a tag
    print type(l)
    for tag in l:
        if tag.find(text=re.compile('SWFObject')):
            print 'found'
            r = re.compile(castup,re.DOTALL).findall(tag.text)
            print r
            final_url = r[2] + ' playpath=' +r[1] +' token='+r[3]+ ' pageUrl='+url+' live=true swfVfy=1 timeout=15 swfUrl=http://www.castup.tv'+r[0]
            return final_url
  
#'rtmp://%s/stream/tvadjsaa?id=5286
#http://www.ucaster.eu/embedded/golrincondepensar/1/650/400

def liveflashtv(channel,g,src,domain=None): #same as janjua
    if 'ucaster' in src:
        url = 'http://'+src+'/embedded/'+channel+'/'+str(g)+'/600/450'
    else:
        url = 'http://'+src+'/embedplayer/'+channel+'/'+str(g)+'/600/450'
    print url
    final_url = ''
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 \
            Firefox/32.0','Referer':str(domain)}
    resp, content = h.request(url, "GET",headers=headers)
    m= re.compile(mips_lft_jan_pattern,re.DOTALL).findall(content)
    print m
    swf = ' swfUrl=http://'+src + m[0][0]
    id = m[0][1].split('&')
    ppath = ' playpath=' +channel +'?' + id[0] #+ final_url + ' live=true timeout=15 swfVfy=1' + ' pageUrl=' + url
    load = 'http://'+src+':1935/loadbalancer'
    print load
    resp, content = h.request(load, "GET",headers=headers)
    print content
    rtmp = 'rtmp://' + re_me(content,r'''.*redirect=([\.\d]+).*''') 
    if 'liveflash' in src:
        rtmp = rtmp  +'/stream/'
        other = ' swfVfy=1 timeout=15 live=true conn=S:OK tcommand=kaskatijaEkonomista;TRUE'
        final_url = rtmp + ppath + swf + ' pageUrl=' + url + other
        print final_url
    elif 'janjua' in src:
        rtmp = rtmp  +'/live/'
        other = ' swfVfy=1 timeout=15 live=true conn=S:OK tcommand=soLagaDaSeStoriAga;TRUE'
        final_url = rtmp + ppath + swf + ' pageUrl=' + url + other
        print final_url
    elif 'ucaster' in src:
        rtmp = rtmp  +'/live/'
        other = ' swfVfy=1 timeout=15 live=true conn=S:OK tcommand=vujkoMiLazarBarakovOdMonospitovo;TRUE'
        final_url = rtmp + ppath + swf + ' pageUrl=' + url + other
        print final_url
    return final_url



    return final_url
def flashtvco(fid,domain): #ok
    url = 'http://www.flashtv.co/embed.php?live=%s' %fid
    print url
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 \
            Firefox/32.0','Referer':str(domain)}
    resp, content = h.request(url, "GET",headers=headers)
    soup = BeautifulSoup(content)
    print soup
    final_url =''
    for link in soup.find_all('script',{'type':'text/javascript'}):
        print link
        if 'swf' in link.text:
            m= re.compile('''(?<=SWFObject\()[,"'\s]+(.*?)[,"'\s]+.*?(?<=file)[,"'\s]+(.*?)[,"'\s]+.*?(?=rtmpe?:)(.*?)[,"'\s]+''', re.DOTALL).findall(link.text)
            print m
            if  len(m) !=0:
                if m[0][0]:
                    final_url = final_url + ' swfUrl=http://www.flashtv.co/' + m[0][0]
                    print final_url
                if  m[0][1]:
                    final_url = ' playpath=' + m[0][1] + final_url
                if  m[0][2]:
                    final_url = m[0][2] +final_url + ' live=true token=%ZZri(nKa@#Z timeout=15 swfVfy=1' + ' pageUrl=' + url
    return final_url
def janjuatv(channel,g,domain=None):
    url = 'http://www.janjua.tv/embedplayer/'+channel+'/'+str(g)+'/600/450'
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 \
            Firefox/32.0','Referer':str(domain)}
    resp, content = h.request(url, "GET",headers=headers)
    soup = BeautifulSoup(content)
    final_url =''    
    for link in soup.find_all('script',{'type':'text/javascript'}):
        if any('rtmp' in s for s in link.contents): #true or false    

                  
            if  len(m) !=0:
                if m[0][0]:
                    final_url = ' swfUrl=' + m[0][0]
                if  m[0][1]:
                    final_url = m[0][1] + final_url
                if  m[0][2]:
                    final_url = final_url + ' playpath=' + m[0][2]
            print final_url
def playfooty(fid,domain=None):    
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 \
            Firefox/32.0','Referer':'http://desistreams.tv'}
    final_url =''
    url ='http://www.playfooty.tv/play/embed.php?u=%s&vw=600&vh=430&domain=http://desistreams.tv'%fid
    resp, content = h.request(url, "GET",headers=headers)
    soup = BeautifulSoup(content)
    for link in soup.find_all('script',{'type':'text/javascript'}):
        m= re.compile('''(?<=SWFObject\(")(.*?)".*(?=rtmpe?:)(.*?)".*(?<=file)[,"'\s]+(.*?)"''', re.DOTALL).findall(link.text)
        print m
        if  len(m) !=0:
            if m[0][0]:
                final_url = final_url + ' swfUrl=' + m[0][0]
                print final_url
            if  m[0][1]:
                final_url = m[0][1] + final_url
            if  m[0][2]:
                final_url = final_url + ' live=true timeout=15 swfVfy=1 playpath=' + m[0][2] + ' pageUrl=' + url
    return final_url     

def cast247(page_data,channel,domain,private=None): # keep same session across the requests including cookie
    s = requests.Session()
    url='http://www.cast247.tv/embed.php?channel=%s&width=600&height=450&domain=%s' %(channel,domain)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36','Referer' : '%s' %url}
    
    if private: #domain protected
        print 'private'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36','Referer' : '%s' %domain}
    r = s.get(url, headers = headers,allow_redirects=False)
    print r.headers
    data = r.text
    match = re.compile(r'flashplayer: "(.*?)",\s*file: "(.*?)",.*?streamer: "(.*?)"',re.DOTALL).findall(data)
    print match
    sURL = re_me(data,'\?k=(.*?)"')
    play = match[0][2] + '/' + match[0][1] + ' swfUrl=http://www.cast247.tv/' + match[0][0] + ' pageUrl=' +url + ' live=true swfvfy=1 timeout=15'
    oRequest = 'http://www.cast247.tv/t.php?k=' + sURL
    print oRequest
    rr = s.get(oRequest, headers = headers)
    return play
def iillive(x,t):
    import math
    w=int(0)
    s=0
    r=''
    p=0
    t_l = len(t)
    print 'xxxxxxxxxxxxxxxxxxxxxx',len(x)
    #ppp = x[170*(t_l+1):]
    ppp =x
    print 'pppppppppppppppppppp',len(ppp)
    j=math.ceil(len(ppp)/1024) #(len(ppp)/1024)
    print j
    l= len(ppp)
    print l
    
    ii = min(l, 1024)
    for k1 in range(int(j), 0, -1):
        #print 'k1',k1
        for k2 in range(int(ii),0,-1):
            #print 'k2',k2
            
            #if p> 11400: #76*150
            #if p> (170*(t_l+1)): #76*170
            tt= t[(ord(ppp[p])) - 48]
            p+=1
            #print 'tt',tt
            #print 's',s
            pp= int(tt) << s
            w = w|pp
            #print w
            #print s
            if s:
                r+= chr(165^w &255)
                #print 'r',r
                w >>= 8
                #print 'w',w
                s -= 2
                #print 's',s
            else:
                #print 'else s'
                s = 6

            if p > (185*(t_l+1)): #76*200
                print 'breaking'
                break
    #print r
    return r    
#<item><title>Sky_Sports_4-live-stream-channel</title><thumbnail>http://snapshots.ilive.to/snapshots/kuwz0bh6zyqaz2y_snapshot.jpg</thumbnail>
#<link>$doregex[reg1]</link>
#<regex><name>reg1</name>
#<expres>$pyFunction:myFunctions.ilive('http://www.ilive.to/view/69326/')</expres>
#<page></page>
#<referer></referer>
#</regex>
#</item>  
def get_soup(url,ref=None,parse_type=None):
    if ref:
        headers.update({'Referer': '%s'%ref})
    resp, content = h.request(url, "GET",headers=headers)
    if parse_type:
        soup = BeautifulSoup(content,'html.parser')
        print 'using html.parser'
    else:
        soup = BeautifulSoup(content)

    
    print len(soup)    
    
    return soup
    
def direct2watch(page_data,channel):
    
    url= 'http://www.direct2watch.com/embedplayer.php?width=653&height=400&channel=%s&autoplay=true' %channel
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'}
    #get_embed = s.get(page_data, headers=headers)
    #data = get_embed.text
    #embed_code = re_me(data,'9stream\.com\/embed.*?\/(.*?)&')
    s.headers.update({'Referer': '%s'%page_data})
    r = s.get(url, headers = headers,allow_redirects=False)
    s.headers.update({'Cookie': r.headers['set-cookie']})
    data = r.text
    c= re_me(data,r'''>c="(.*?)"''')
    
    d=''
    for i in range(len(c)):
        if i%3 == 0:
            d+=('%')
        else:
            d+=(c[i])
    
    uu= urllib2.unquote(d)
    print 'uu',uu
    ttk= re_me(uu,r'''Array\((.*?)\)''')
    tk = ttk.split(',')
    print 'tk',len(tk)
    
        
    x= re_me(data,r'''x\("(.*?)"\)''')
    print len(x)
    tag = iillive(x,tk)  
    match = re.compile(r'''getJSON\(\"(.*?)\",.*?\'streamer\': \"(.*?)\",.*?\'file\': \'(.*?)\'.*?src:\s*\'(.*?)\'''',re.DOTALL).findall(tag)
    print match
    #    match = re.compile(r'getJSON\(\"(.*?)\",.*?streamer\': \"(.*?)direct2watch(.*?)\",.*?\'file\': \'(.*?)\'.*?\'flash\', src:\s*\'(.*?)\'', re.DOTALL).findall(data)
    for token_url,rtmp,playpath,swf in match:
        rtmp = rtmp.replace("\\", "")
        app = rtmp.split("1935/")
        rtmp = app[0]+'1935/'+app[1].replace('.','')
        s.headers.update({'Referer': url})
        r = s.get(token_url, headers = headers,allow_redirects=False)
        playpath = playpath.replace('.flv','')
        token = re_me(r.text,'token":"(.*?)"')
        print token
        play= rtmp + ' app='+ app[1].replace('.','') +' playpath=' + playpath + ' token=' + token + ' pageUrl=' +url + ' swfUrl=' + swf
        return play    
def ilive(page_data,domain=None):
    s = requests.Session()
    #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'}
    #headers = {'cache-control':'no-cache','User-Agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'}
    url= page_data #'http://www.ilive.to/view/%s/' %id
    #resp, content = h.request(url, "GET",headers=headers)
    #r = s.get(url, headers = headers,allow_redirects=False)
    #content = r.text    
    #headers.update({'Cookie': r.headers['set-cookie']})
    #soup = BeautifulSoup(content)
    r = s.get(url, headers = headers,allow_redirects=False)
    content = r.text
    headers.update({'Cookie': r.headers['set-cookie']})
    c= re_me(content,r'''>c="(.*?)"''')
    
    d=''
    for i in range(len(c)):
        if i%3 == 0:
            d+=('%')
        else:
            d+=(c[i])
    
    uu= urllib2.unquote(d)
    print 'uu',uu
    ttk= re_me(uu,r'''Array\((.*?)\)''')
    tk = ttk.split(',')
    print 'tk',len(tk)
    
        
    x= re_me(content,r'''x\("(.*?)"\)''')
    print len(x)
    tag = iillive(x,tk)
    soup = BeautifulSoup(tag)
    print len(soup)
    l = soup('script', {'type':'text/javascript'})
    print len(l)
    for realdata in l:
        if realdata.find(text=re.compile('token')):
    #print 'found'
            match = re.compile(ilivee_regex,re.DOTALL).findall(realdata.text)    
    #match = re.compile(ilivee, re.DOTALL).findall(tag)
    print match
            
    #    match = re.compile(r'getJSON\(\"(.*?)\",.*?streamer\': \"(.*?)direct2watch(.*?)\",.*?\'file\': \'(.*?)\'.*?\'flash\', src:\s*\'(.*?)\'', re.DOTALL).findall(data)
    for token_url,swf,rtmp,playpath in match:
        headers.update({'Referer': '%s'%url}) #you must have this
        #r = s.get(token_url)
        #R_token = r.text
        token_url = 'http://www.ilive.to/server2.php?id='+getEpocTime()+'&_='+getEpocTime(milli='1')
        print token_url
        #headers.update({'Referer': '%s'%url,'cache-control':'no-cache'})
        r = requests.get(token_url,headers=headers)
        token = re_me(r.text,'token":"(.*?)"')
        playpath = playpath.split('.')
        
        rtmp = rtmp.replace("\\", "")  #.replace('rtmp','rtsp')
        app = rtmp.split("1935/")
        #print app[1]
        play= rtmp + ' app='+ app[1] +' playpath=' + playpath[0] + ' token=' + token + ' pageUrl=' +url + ' live=1 swfVfy=true timeout=30 swfUrl=' + swf
        return play
def getEpocTime(milli=None):
    import time
    if milli:
        return str(int(time.time()*1000))
    else:
        return str(int(time.time()))
    
'''<item><title>9stream hustler ALI1</title>
<link>$doregex[reg1]</link>
<regex><name>reg1</name>                 '9stream code' , 'referer'
<expres>$pyFunction:myFunctions.stream9('100','http://cinestrenostv.tv')</expres>
<page></page>
</regex>
</item>

This also work. Make sure the referer is correct if dont play.
<item><title>9stream</title>
<link>$doregex[reg1]</link>
<regex><name>reg1</name>
<expres>$pyFunction:myFunctions.stream9('http://verdirectotv.com/tv/deportes/plusliga.html')</expres>
<page></page>
<referer></referer>
</regex>
</item>'''
def re_me(data, re_patten):
    match = ''
    m = re.search(re_patten, data,re.I)
    if m != None:
        match = m.group(1)
    else:
        match = ''
    return match        
def stream9(page_data,domain=None):
    s = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'}
    get_embed = s.get(page_data, headers=headers)
    data = get_embed.text
    embed_code = re_me(data,'9stream\.com\/embed.*?\/(.*?)&')
    s.headers.update({'Referer': '%s'%page_data})
    url= 'http://www.9stream.com/embedplayer.php?width=653&height=400&channel=%s&autoplay=true' %embed_code
    r = s.get(url, headers = headers,allow_redirects=False)
    data = r.text
    c= re_me(data,r'''>c="(.*?)"''')
    
    d=''
    for i in range(len(c)):
        if i%3 == 0:
            d+=('%')
        else:
            d+=(c[i])
    
    uu= urllib2.unquote(d)
    print 'uu',uu
    ttk= re_me(uu,r'''Array\((.*?)\)''')
    tk = ttk.split(',')
    print 'tk',len(tk)
    
        
    x= re_me(data,r'''x\("(.*?)"\)''')
    print len(x)
    tag = iillive(x,tk)    
    match = re.compile(stream9, re.DOTALL).findall(tag)
    print match
    #    match = re.compile(r'getJSON\(\"(.*?)\",.*?streamer\': \"(.*?)direct2watch(.*?)\",.*?\'file\': \'(.*?)\'.*?\'flash\', src:\s*\'(.*?)\'', re.DOTALL).findall(data)
    for token_url,rtmp,playpath,swf in match:
        s.headers.update({'Referer': '%s'%url})
        r = s.get(token_url)
        R_token = r.text
        token = re_me(R_token,'token":"(.*?)"')
        playpath = playpath.split('.')
        
        rtmp = rtmp.replace("\\", "")
        app = rtmp.split("1935/")
        #print app[1]
        play= rtmp + ' app='+ app[1] +' playpath=' + playpath[0] + ' token=' + token + ' pageUrl=' +url + ' live=true swfVfy=1 timeout=15 swfUrl=' + swf
        return play    
'''<item><title>Premier leauge dinozap hdcaststream function </title>
<link>$doregex[play]</link>

<regex>
<name>play</name>
<expres>$pyFunction:myFunctions.skytuxtv(page_data,112)</expres>
<page></page>
<referer></referer>
</regex>
</item>'''
def hdcastream(page_data,file): #site dinozap
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:29.0) Gecko/20100101 Firefox/29.0'}
    url='http://www.hdcastream.com/channel.php?file=%s&width=700&height=400&autostart=true' %file
    req = Location_only(url,headers)
    #req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; rv:29.0) Gecko/20100101 Firefox/29.0')
    #req.add_header('Referer', 'http://ibrod.tv/cw-tv-oline.html')
    ress = requests.get(req, headers = headers,allow_redirects=False)
    src=ress.text
    #response.close()
    
    iframe = re_me(src,'src=\"(.*?)\"')
    print ('iframe is %s' %iframe)
    #get location from header to get domain
    r = requests.head(iframe, headers = headers,allow_redirects=False)
    try:
        ref = r.headers['Location']
        print ('ref is %s' %ref)
        k = ref.split('domainprotect=')
        referer = k[1]
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:29.0) Gecko/20100101 Firefox/29.0','Referer' : '%s' %referer}
        print referer
    except Exception:
        pass
    
    response= requests.get(iframe,headers=headers,allow_redirects=False)
    data=response.text
    ssx4 = base64.b64decode(re_me(data,'ssx4" value=\"(.*?)\"'))
    print ( 'ssx4 is %s' %ssx4)
    ssx1 = base64.b64decode(re_me(data,'ssx1" value=\"(.*?)\"'))
    nssx4 = ssx4.replace("redirect/", "vod")
    print ( 'nssx4 is %s' %nssx4)
    playurl = nssx4 + ' playpath=' + ssx1 + ' pageUrl=' + iframe + ' token=wowk flashver=WIN%2011,9,900,117 swfUrl=http://www.thebestplayeronline.com/jwplayer5/addplayer/jwplayer.flash.swf'
    return playurl

