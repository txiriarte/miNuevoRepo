# -*- coding: UTF-8 -*-

import sys, re, ast, os
import six
from six.moves import urllib_parse

import requests
from requests.compat import urlparse

import datetime
import time

#import html
from resources.lib.brotlipython import brotlidec
if sys.version_info >= (3,0,0):
    from resources.lib.cmf3 import parseDOM
else:
    from resources.lib.cmf2 import parseDOM

    
import xbmcaddon, xbmcvfs,    xbmc
    
    
    
sess = requests.Session()

UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'

main_url = 'https://klubsports.xyz/'
headers = {'user-agent': UA,}

addonInfo = xbmcaddon.Addon().getAddonInfo

try:
    dataPath        = xbmcvfs.translatePath(addonInfo('profile'))
except:
    dataPath       = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
vleagueFile = os.path.join(dataPath, 'vleague.txt')


def resp_text(resp):
    """Return decoded response text."""
    if resp and resp.headers.get('content-encoding') == 'br':
        out = []
        # terrible implementation but it's pure Python
        return brotlidec(resp.content, out).decode('utf-8')
    response_content = resp.text

    return response_content.replace("\'",'"')
    
    
def request_sess(url, method='get', data={}, headers={}, result=True, json=False, allow=True , json_data = False):
    if method == 'get':
        resp = sess.get(url, headers=headers, timeout=15, verify=False, allow_redirects=allow)
        
    elif method == 'post':
        if json_data:
            resp = sess.post(url, headers=headers, json=data, timeout=15, verify=False, allow_redirects=allow)
        else:
            resp = sess.post(url, headers=headers, data=data, timeout=15, verify=False, allow_redirects=allow)

    if result:
        return resp.json() if json else resp_text(resp)
    else:
        return resp


def get_delta():

    local = datetime.datetime.now()
    utc =  datetime.datetime.utcnow()
    delta = (int((local - utc).days * 86400 + round((local - utc).seconds, -1)))/3600
    return delta
    
def getRealTime(godzina, minus=-1):

    delta = get_delta()
    #'%Y-%m-%dT%H:%M'   2022-07-10T05:30
    try:
        date_time_obj=datetime.datetime.strptime(godzina, '%Y-%m-%dT%H:%M')+ datetime.timedelta(hours=minus)
    except TypeError:
        date_time_obj=datetime.datetime(*(time.strptime(godzina, '%Y-%m-%dT%H:%M')[0:6]))+ datetime.timedelta(hours=minus)
    date_time_obj = date_time_obj+ datetime.timedelta(hours=int(delta))

    return date_time_obj.strftime("%H:%M")
        
def ListMenu():
    return [{'title':'Competitions','href':'https://vipleague.im/','image':'x','plot':'Vipleague - competitions', 'mode':'listcompetitions:vipleague'}, {'title':'Live now','href':'https://vipleague.im/live-now-streaming','image':'x','plot':'Vipleauge - live now', 'mode':'listschedule:vipleague'}, {'title':'Top streaming','href':'https://vipleague.im/top-streaming','image':'x','plot':'Vipleauge - top streaming', 'mode':'listschedule:vipleague'}]

    
    
    
    
    
def ListSchedule(url):
    zz=''
    out=[]

    srt = False

    html = request_sess(url, 'get', headers=headers)
    
    result = parseDOM(html,'div',attrs = {'id':".+?",'class':"invisible"})#[0]    
    html = re.findall('siteConfig\s*=\s*({.*?});\<',html, re.DOTALL)[0]

    f = xbmcvfs.File(vleagueFile, 'w')
    f.write(html.encode('utf-8') if six.PY2 else html)
    f.close()
    if result:
        result = result[0]
        
        if not '-schedule-' in url:
            if 'mlbstream.me' in url or 'live.cricstream.me' in url:
                host = 'https://'+urlparse(url).netloc+'/'

                for x in re.findall('(<a.+?)</div>', result,re.DOTALL):
                    href = re.findall('href="([^"]+)"', x,re.DOTALL)[0]
                    tyt = re.findall('title="([^"]+)"', x,re.DOTALL)[0]
                    id = re.findall('id="([^"]+)"', x,re.DOTALL)[0]
                    dt=''
                    if '<span content' in x:
                        dt = re.findall('span content="([^"]+)"', x, re.DOTALL)[0]
                        dt = getRealTime(dt, minus = -1)
                    tit = '%s [COLOR gold](%s)[/COLOR]'%(tyt,dt)
                    idx = urllib_parse.quote_plus(id+'|'+host)
                    out.append({'title':tit,'href':str(idx)+'|'+tit,'image':'x','code':dt,'mode':'getlinks:vipleague'})
            else:
            
            
            
            
                tithrefikondt = re.findall('href="([^"]+)".*?title="([^"]+)".*?<span content="([^"]+)".*?id="([^"]+)">',result,re.DOTALL)#[0]
        
                for href,tyt,dt,idx in tithrefikondt:

                    dt = getRealTime(dt, minus = -1)
                    tit = '%s [COLOR gold](%s)[/COLOR]'%(tyt,dt)
    
                    out.append({'title':tit,'href':str(idx)+'|'+tit,'image':'x','code':dt,'mode':'getlinks:vipleague'})
        else:
            for x in re.findall('(<a.+?)</div>', result,re.DOTALL):
                href = re.findall('href="([^"]+)"', x,re.DOTALL)[0]
                tyt = re.findall('title="([^"]+)"', x,re.DOTALL)[0]

                idx = re.findall('id="([^"]+)"', x,re.DOTALL)[0]
                dt=''
                dt2 =''
                czs = ''
                if '<span content' in x:
                    dt = re.findall('span content="([^"]+)"', x, re.DOTALL)[0]
                    dt = getRealTime(dt, minus = -1)

                    dt2 = re.findall('data\-.*?="([^"]+)"', x, re.DOTALL)[-1]
                    czs = dt2 + ' '+dt

                tit = '%s [COLOR gold](%s)[/COLOR]'%(tyt,czs)
                out.append({'title':tit,'href':str(idx)+'|'+urllib_parse.quote_plus(tit),'image':'x','code':czs,'mode':'getlinks:vipleague'})

    return out
    

def PosortujData(out):
    outx=[]
    out = sorted(out, key=lambda x: x.get('title', None))
    for t in out:
        title=html.unescape(t.get('title', None)).replace('z0','0')

        czas=re.findall('(.+?)\s',title,re.DOTALL)[0]

        godz = getRealTime(czas, minus = -1)
        title = title.replace(czas,godz)
        outx.append({'title':title,'href':t.get('href', None),'empty':'false','mode':'getlinks:klubsports'})
    return outx    


def ListScheduleMenu(url):
    out=[]
    resp = request_sess(url, 'get', headers=headers,result = False)    
    urlk = resp.url
    html = resp_text(resp)
    hreftit = re.findall('<a class="btn btn-lg btn-light.*?href=([^>]+)>.*?<\/i>([^<]+)',html,re.DOTALL)
    for href,title in hreftit:
        href = urlk[:-1]+ href if href.startswith('/') else href
        #[:-1]
        mod = 'listschedule:vipleague'
        out.append({'title':title,'href':href,'mode':mod,'image':'nic'})

    return out
    
def ListCompetitions(url):

    out=[]
    html = request_sess(url, 'get', headers=headers)    

    listacomp = re.findall('class="text\-decoration-none" href="([^"]+)" title="([^"]+)"',html,re.DOTALL)
    for href,title in listacomp:
        title = title.replace(' Live','')
        href = 'https://vipleague.im'+ href if href.startswith('/') else href
        mod = 'listschedule:vipleague'
        if 'mlbstream.me' in href or 'live.cricstream.me' in href:
            mod = 'schedulemenu'


        out.append({'title':title,'href':href,'mode':mod,'image':'nic'})

    nturl = False

    return out,nturl

def GetLinks(url):

    id,tyt = url.split('|')
    out = []
    import json
    f = xbmcvfs.File(vleagueFile)
    b = f.read()
    f.close()
    data =json.loads(b)
    slugs = data.get('slugs', None)

    id = urllib_parse.unquote_plus(id)
    mlb = False
    if '|' in id:
        id,host = id.split('|')

        mlb = True

    urlk = slugs.get(id,None)

    if mlb:
        mainurl = host+urlk+'-live/stream-{}'
    else:
        mainurl = 'https://vipleague.im/'+urlk+'-streaming-link-{}'
    data = data.get('links', None)
    tyt = urllib_parse.unquote_plus(tyt)
    dt = re.findall('(\(.+?\))',tyt,re.DOTALL)
    p1 = re.findall('^(.+?)\[COLOR',tyt,re.DOTALL)
    p1 = p1[0] if p1 else tyt
    
    nr = 1
    linki=data.get(id,None)
    for link in linki:
        href = mainurl.format(str(nr))
        hd = link.get('hd', None)
        hd = 'HD' if hd else 'SD'
        tit = link.get('player', None)
        lang = link.get('lang', None)
        lang = lang if lang else ''

        tytul= p1+' Link %d %s'%(nr,hd)

        tytul= p1+' Link %d %s'%(nr,hd)
    
        out.append({'title':tytul,'href':str(href),'image':'x','code':dt[0] if dt else tytul,'plot':p1,'mode':'playvid:vipleague'})
        nr+=1
    
    return out    

def GetVid(url):

    headers = {
        'Host': 'vipleague.im',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
    }
    html = request_sess(url, 'get', headers=headers)
    video_url =''

    if 'scripts/v2/emb' in html:
        zmid = re.findall('zmid\s*=\s*"([^"]+)"',html,re.DOTALL)

        pdettxt = re.findall('pdettxt\s*=\s*"([^"]+)"',html,re.DOTALL)
        pid = re.findall('pid\s*=\s*(\d+)',html,re.DOTALL)

        headers = {
            'Host': 'www.liveply.me',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'accept-language': 'pl,en-US;q=0.7,en;q=0.3',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://vipleague.im',
            'referer': 'https://vipleague.im/',
        }

        if zmid and pid and pdettxt:
            params = {
                'v': zmid[0],
            }
            
            data = {
                'pid': pid[0],
                'ptxt': pdettxt[0],
            }
            response_content = sess.post('https://www.liveply.me/sd0embed', params=params, headers=headers, data=data).text
        else:

            v_vid = re.findall('v_vid\s*=\s*"([^"]+)"',html,re.DOTALL)
            v_vpp = re.findall('v_vpp\s*=\s*"([^"]+)"',html,re.DOTALL)
            v_vpv = re.findall('v_vpv\s*=\s*"([^"]+)"',html,re.DOTALL)
            params = {
                'p': v_vpp[0],
                'id': v_vid[0],
                'v': v_vpv[0],
            }
            
            data = {
                'id': v_vid[0],
                'v': v_vpv[0],
                'p': v_vpp[0],
                'ptxt': '',
            }
            response_content = sess.post('https://www.liveply.me/hdembed', params=params, headers=headers, data=data).text
        skrypty = re.findall('<script>(.+?)<\/script>\\n',response_content,re.DOTALL)#<script>([^<]+)<\/script>',response_content,re.DOTALL)

        payload = """function abs() {%s};\n abs()    """
        a=''
        
        for skrypt in skrypty:
            if 'let' in skrypt and 'eval' in skrypt:
        
                    a = payload%(skrypt)
        
                    a = a[::-1].replace("eval"[::-1], "return"[::-1], 1)[::-1]
        
                    break
        
        jsPayload = a 
        
        import js2py
        
        js2py.disable_pyimport()
        context = js2py.EvalJs()

        try:
            context.execute(jsPayload)
            response_content = context.eval(jsPayload)
            response_content = response_content if response_content else ''
        except Exception as e:
        
            response_content=''
        
        
        
        
        
        UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'
        if 'function(h,u,n,t,e,r)' in response_content:
            from resources.lib import dehunt as dhtr
            import base64
            ff=re.findall('function\(h,u,n,t,e,r\).*?}\((".+?)\)\)',response_content,re.DOTALL)[0]#.spli
            ff=ff.replace('"','')
            h, u, n, t, e, r = ff.split(',')
            
            cc = dhtr.dehunt (h, int(u), n, int(t), int(e), int(r))
        
            cc=cc.replace("\'",'"')

            fil = re.findall('file:\s*window\.atob\((.+?)\)',cc,re.DOTALL)[0]
        
            src = re.findall(fil+'\s*=\s*"(.+?)"',cc,re.DOTALL)[0]
            video_url = base64.b64decode(src)
            ref ='https://www.liveply.me/'
            if six.PY3:
                video_url = video_url.decode(encoding='utf-8', errors='strict')
            video_url+='|User-Agent='+urllib_parse.quote(UA)+'&Referer='+urllib_parse.quote(ref)
        
        
    return video_url    
