import urllib,base64
import os,xbmc,xbmcaddon,xbmcgui,re,xbmcplugin,sys
#from resources.lib import commonmyFunctions as cmyFun
import commonmyFunctions as cmyFun
from bs4 import BeautifulSoup
addon = xbmcaddon.Addon('plugin.video.live.proyectoluzdigital')
profile = xbmc.translatePath(addon.getAddonInfo('profile').decode('utf-8'))
#LstDir = os.path.join(profile, 'xmldir')
communityfiles = os.path.join(profile, 'LivewebTV')
cacheDir = os.path.join(profile, 'cachedir')
headers=dict({'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:32.0) Gecko/20100101 Firefox/32.0'})

if not cacheDir.startswith(('smb://', 'nfs://', 'upnp://', 'ftp://')) and not os.path.isdir(cacheDir):
    os.mkdir(cacheDir)
if not os.path.isdir(communityfiles):
    os.mkdir(communityfiles)
ref = 'http://verdirectotv.com'
channel_url = 'http://tv.verdirectotv.org/channel.php?file=%s&width=650&height=400&autostart=true'
jquery = '%s?callback=jQuery170025813597286718948_%s&v_cod1=%s&v_cod2=%s&_=%s'
final_rtmp = '%s app=tvdirecto/?token=%s playpath=%s flashver=WIN%5C2017,0,0,134 \
        swfUrl=http://www.businessapp1.pw/jwplayer5/addplayer/jwplayer.flash.swf pageUrl=%s live=1 timeout=15 swfVfy=1'
def verdirect(chnum):
    ch_url = channel_url %chnum
    con,new= cmyFun.cache(ch_url, 0,ref=ref)
    s_url = cmyFun.match1(con,'iframe\s*src="([^"]+)')
    con,new= cmyFun.cache(s_url, 0.5,ref=ref)


    soup = BeautifulSoup(con,'html.parser')
    hidden = urllib.quote_plus(soup('input',{'type':'hidden'})[1].get('value'))
    hidden2 = urllib.quote_plus(soup('input',{'type':'hidden'})[2].get('value'))
    hidden3 = base64.b64decode(soup('input',{'type':'hidden'})[3].get('value'))
    jquery_url = jquery %(hidden3,cmyFun.getEpocTime(milli='1'),hidden,hidden2,cmyFun.getEpocTime(milli='1'))
    con,new= cmyFun.cache(jquery_url, 0.5,ref=s_url)
    res = cmyFun.match1(con,'result1":"([^"]+)','result2":"([^"]+)')
    if res and 'redirect' in res[1]:
        token = res[1].replace('\\','').split('redirect/?')
        rtmp = 'rtmp://146.185.16.34:1735/' #token[0]
    else:
        token = res[1].replace('\\','').split('vod/?')
        rtmp = 'rtmp://146.185.16.76:1735/' #token[0]
    app = 'tvdirecto?'+token[1]
    return rtmp+ app +' playpath='+ res[0] +' flashver=WIN%5C2017,0,0,134 swfUrl=http://www.businessapp1.pw/jwplayer5/addplayer/jwplayer.flash.swf swfVfy=1 pageUrl='+s_url+' live=1 timeout=15'
