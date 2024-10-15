# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import six, sys
from six.moves import urllib_error, urllib_request, urllib_parse, http_cookiejar


import threading
import re
import time
import json
import xbmc
from datetime import date, datetime
from collections import OrderedDict

BASEURL='http://sport.tvp.pl'
proxy={}
TIMEOUT = 10
BRAMKA='http://www.bramka.proxy.net.pl/index.php?q='
BRAMKA3='https://darmowe-proxy.pl'
COOKIEFILE = ''
if sys.version_info >= (3,0,0):
    to_unicode = str

else:
    to_unicode = unicode



def getPhotoLink(uid):
    retVal=''
    h1=uid[0]
    h2=uid[1]
    h3=uid[2]
    ext=uid[-4:]
    hash=uid[:-4]
    width='640'
    heigth='360'
    retVal += "http://s.tvp.pl/images/";
    retVal += h1;
    retVal += "/";
    retVal += h2;
    retVal += "/";
    retVal += h3;
    retVal += "/";
    retVal += "uid_" + hash + "_width_" + width + "_height_" + heigth + "_gs_0" + ext;
    return retVal

UA='Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0'
cs=''
def getUrl(url,proxy={},timeout=TIMEOUT,cookies=True):
    global cs
    cookie=[]
    if proxy:
        urllib_request.install_opener(urllib_request.build_opener(urllib_request.ProxyHandler(proxy)))
    elif cookies:
        cookie = http_cookiejar.LWPCookieJar()
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cookie))
        urllib_request.install_opener(opener)
    req = urllib_request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36')
    try:
        response = urllib_request.urlopen(req,timeout=timeout)
        linkSRC = response.read()
        response.close()
    except:
        linkSRC=''
    cs = ''.join(['%s=%s;'%(c.name, c.value) for c in cookie])
    return linkSRC
    
    
def ListMenu():
    return [{'title':'Transmisje','href':'dzien','image':'x','plot':'TVPSport - transmisje', 'mode':'listschedule:tvpsport'},{'title':'Retransmisje','href':'1','image':'x','plot':'TVPSport - retransmisje', 'mode':'listretransmisje'}]

    
    
    
def suma(czas):
    y, m, d = czas.split('-')
    return int(y)*365 + int(m)*30 + int(d)    
def sekundy(czas):
    g, m = czas.split(':')
    return int(g) * 3600 + int(m) * 60

weekdays = [
    'Poniedziałek',
    'Wtorek',
    'Środa',
    'Czwartek',
    'Piątek',
    'Sobota',
    'Niedziela',
]
def ListSchedule(url):

    out=[]
    urlk = 'http://www.api.v3.tvp.pl/shared/listing_blackburst.php?dump=json&nocount=1&type=video&parent_id=3116100&copy=true&direct=true&order=release_date_long,1&count=-1&filter={%22paymethod%22:0}'
    content=getUrl(urlk)
    streams=json.loads(content)

    sections = {}
    dates = []
    out = []
    items = streams.get('items', [])
    for item in items:
        if (item.get('release_date_long', 0) + item.get('duration', 0) * 1000) < int(time.time() * 1000.0):
            continue
    
        release_dt = item.get('release_date_dt')
        if sections.get(release_dt, None):
            sections[release_dt].append(item)
        else:
            sections[release_dt] = []
            sections[release_dt].append(item)
    
        dates.append(release_dt)
    
    dates = list(OrderedDict.fromkeys(dates))
    
    for datestr in dates:
    
        components = datestr.split('-') if sys.version_info >= (3,0,0) else datestr.encode('utf-8', 'ignore').split('-')

        d = date(int(components[0]), int(components[1]), int(components[2]))

        title = weekdays[d.weekday()] + ', ' + components[2] + '-' + components[1] + '-' + components[0]

        now = datetime.now()
        if d.day == now.day and d.month == now.month and d.year == now.year:
            title = 'Dzisiaj'

        out.append({'title':'[COLOR khaki][I][B]--========== '+title+' ==========--[/B][/COLOR][/I]','href':title,'empty':'true'})    
    
        for item in sections[datestr]:
            movie_id = item.get('asset_id', '')
            release_hour = item.get('release_date_hour', '')
            name = release_hour + ' - ' + item.get('title', '')
            
            try:
                imag= item.get('image',[])[0].get("file_name",'')
                img= getPhotoLink(imag)
            except:
                img=''
    
            images = item.get('image', [])
            image_dict = next(iter(images), None)
            description = item.get('lead', [])
    
            img = ''
            if image_dict:
                img = getPhotoLink(image_dict.get('file_name', None))
    
            if item.get('play_mode', 0) == 2 and item.get('is_live', False):
                name = name if sys.version_info >= (3,0,0) else to_unicode(name)#.encode('utf-8', 'ignore')
                name = '[B][COLOR lightgreen]LIVE [/COLOR][/B] ' + name
                
                out.append({'title':name,'href':movie_id,'image':img,'plot':name,'mode':'playvid:tvpsport'})
            else:
                out.append({'title':name,'href':name,'empty':'true','image':img})   
            
    return out
def Retransmisje(strony):

    urlk='http://www.api.v3.tvp.pl/shared/listing_blackburst.php?dump=json&type=video&parent_id=48603943&order=modify_date_long&count=1&page='+str(strony)
    out=[]
    content=getUrl(urlk)
    content=json.loads(content)

    transmisje = content.get('items', [])

    pocz = int(strony)#-1 

    transmisjelista= transmisje[0 :25]
    
    nturl = False

    nturl = '%s'%(str( pocz+25)) 
    
    for tran in transmisjelista:
    
        name = tran.get('title', None)
        plot = tran.get('lead', None)
        images = tran.get('image', [])
        image_dict = next(iter(images), None)
        img = ''
        if image_dict:
            img = getPhotoLink(image_dict.get('file_name', None))
        movie_id = tran.get('asset_id', '')
        out.append({'title':name,'href':movie_id,'image':img,'plot':name,'mode':'playvid:tvpsport'})
    
    return out,nturl

def getProxyList():
    content=getUrl('http://www.idcloak.com/proxylist/free-proxy-list-poland.html')
    speed = re.compile('<div style="width:\\d+%" title="(\\d+)%"></div>').findall(content)
    trs = re.compile('<td>(http[s]*)</td><td>(\\d+)</td><td>(.*?)</td>',re.DOTALL).findall(content)
    proxies=[{x[0]: '%s:%s'%(x[2],x[1])} for x in trs]
    return proxies
def getTVPstream(url):
    if url=='':
        return vid_link
    if url.startswith('http://sport.tvp.pl'):
        content = getUrl(url)
    else:
        content = getUrl(BASEURL+url)
    src = re.compile('data-src="(.*?)"', re.DOTALL).findall(content)
    if src:
        vid_link=BASEURL+src[0]
    return vid_link
def GetVid(ex_link):
    
    if ex_link:
        url = 'https://sport.tvp.pl/sess/tvplayer.php?object_id=%s&force_original_for_tracking=1&nextprev=1&autoplay=true&copy_id=%s'%(ex_link,ex_link) if ex_link else ''
        stream_url = decodeUrl(url)
        proxy=False
        if not stream_url or 'material_niedostepny' in stream_url :
            stream_url = decodeUrl(url,use='pgate5')            
            if not stream_url or 'material_niedostepny' in stream_url :
                stream_url = decodeUrl(url,use='pgate3')                        
            if not stream_url or 'material_niedostepny' in stream_url :
                stream_url = decodeUrl(url,use='proxy')                
            proxy=True
    else:
        stream_url=''
        proxy=False
    return stream_url
    
def getUrlProxy2(url):    
    import requests
    global COOKIEFILE
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Referer': 'https://darmowe-proxy.pl/',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
    }
    req=requests.get(BRAMKA3,headers=headers)
    cookies=req.cookies
    data = {'u': url,'encodeURL': 'on','encodePage': 'on','allowCookies': 'on'}
    data = urllib_parse.urlencode(data)
    vurl = BRAMKA3+'/includes/process.php?action=update'
    link=requests.post(vurl,data=data,headers=headers,cookies=cookies).content
    if six.PY3:
        link = link.decode(encoding='utf-8', errors='strict')
    return link        
    
def getUrlProxy5(url):    
    import requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Referer': 'https://www.sslsecureproxy.com/',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    html=requests.get('https://www.sslsecureproxy.com/',headers=headers).content
    if six.PY3:
        html = html.decode(encoding='utf-8', errors='strict')
    selip=re.findall('"(.+?)">Poland',html)[0]
    data = {
    'u': url,
    'u_default': 'https://www.google.com/',
    'urlsub': '',
    'server_name': 'pl',
    'selip': selip,
    'customip': '',
    'allowCookies': 'on',
    'autoPermalink': 'on'
    }

    response = requests.post('https://www.sslsecureproxy.com/query', headers=headers, data=data).content
    if six.PY3:
        response = response.decode(encoding='utf-8', errors='strict')
    return response
    
def decodeUrl(url='http://sport.tvp.pl/sess/tvplayer.php?copy_id=35828270&object_id=35828270&autoplay=true',use=''):
    vid_link=''
    if not url: return vid_link
    if use=='pgage':
        data = getUrl(BRAMKA+urllib_parse.quote_plus(url)+'&hl=2a5')
        vid_link = getM3u8src(data)

    elif use=='pgate5':
        data = getUrlProxy5(url)
        vid_link = getM3u8src(data)
    
    elif use=='pgate3':    
        data=getUrlProxy2(url)
        vid_link = getM3u8src(data)
        
    elif use=='proxy':
        
        proxies = getProxyList()
        listOUT = list()
        prList = [[] for x in proxies]
        for i,proxy in enumerate(proxies):
            thread = threading.Thread(name='Thread%d'%i, target = chckPrList, args=[url,proxy,prList,i])
            listOUT.append(thread)
            thread.start()
        while any([i.isAlive() for i in listOUT]) and len(vid_link)==0:
            for l in prList:
                l = prList[3]
                if isinstance(l,list):
                    vid_link = l
                    break
            time.sleep(0.1)
        del listOUT[:]
    else:
        #
        data = getUrl(url)
        vid_link = getM3u8src(data)
    return vid_link
    
def getM3u8src(data):

    vid_link=''
    if six.PY3:
        data = data.decode(encoding='utf-8', errors='strict')
    vid_link = re.compile('1:{src[:\\s]+[\'"](.+?)[\'"]', re.DOTALL).findall(data)
    if vid_link:
        if 'm3u8' in vid_link[0]:
            vid_link = vid_link[0]
        else:
            vid_link = re.compile('0:{src[:\\s]+[\'"](.+?)[\'"]', re.DOTALL).findall(data)
            vid_link = vid_link[0] if vid_link else ''

    if not vid_link:
        vid_link = re.compile("0:{src:'(.+?)'", re.DOTALL).findall(data)
        vid_link = vid_link[0] if vid_link else ''

    return vid_link
    
def chckPrList(ex_link ,proxy, prList, index):
    data = getUrl(ex_link,proxy,timeout=10)
    linkSRC = m3u8Quality(getM3u8src(data))
    prList[index]= linkSRC if not 'material_niedostepny' in linkSRC else ''
    
def m3u8Quality(url):
    out=url
    if url and url.endswith('.m3u8'):
        srcm3u8 = re.search('/(\\w+)\\.m3u8',url)
        srcm3u8 = srcm3u8.group(1) if srcm3u8 else 'manifest'
        content = getUrl(url)
        matches=re.compile('RESOLUTION=(.*?)\r\n(QualityLevels\\(.*\\)/manifest\\(format=m3u8-aapl\\))').findall(content)
        if matches:
            out=[{'title':'auto','url':url}]
            for title, part in matches:
                one={'title':title,'url':url.replace(srcm3u8,part)}
                out.append(one)
    return out
