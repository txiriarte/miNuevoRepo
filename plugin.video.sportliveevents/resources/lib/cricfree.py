# -*- coding: UTF-8 -*-

import sys,re, ast 
import six
from six.moves import urllib_parse

import requests
from requests.compat import urlparse

import datetime
import time
import xbmcaddon

from resources.lib.brotlipython import brotlidec
if sys.version_info >= (3,0,0):
    from resources.lib.cmf3 import parseDOM
else:
    from resources.lib.cmf2 import parseDOM
sess = requests.Session()

addon = xbmcaddon.Addon(id='plugin.video.sportliveevents')

proxyport = addon.getSetting('proxyport')

UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'

main_url = 'https://en.cricfree.io/'
headers = {
    'user-agent': UA,}

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
    
def getRealTime(godzina):

    delta = get_delta()
    try:
        date_time_obj=datetime.datetime.strptime(godzina, '%H:%M')+ datetime.timedelta(hours=-1)
    except TypeError:
        date_time_obj=datetime.datetime(*(time.strptime(godzina, '%H:%M')[0:6]))+ datetime.timedelta(hours=-1)
    date_time_obj = date_time_obj+ datetime.timedelta(hours=int(delta))

    return date_time_obj.strftime("%H:%M")
        
def ListMenu():
    return [{'title':'Channels','href':main_url,'image':'x','plot':'Cricfree - 24/7', 'mode':'listchannels:cric'}, {'title':'Schedule','href':main_url,'image':'x','plot':'Cricfree - schedule', 'mode':'listschedule:cric'}]

def ListSchedule(url):
    zz=''
    out=[]
    html = request_sess(main_url, 'get', headers=headers)

    result = parseDOM(html,'article')[0]
    tables = parseDOM(result,'table')
    for table in tables:
        day = parseDOM(table,'th')[0]
        day = '[B]................[COLOR khaki]'+day+'[/COLOR]................[/B]'
        out.append({'title':day,'href':day,'empty':'true'})
        links = parseDOM(table,'tr', attrs={'id': "schedule_.*?"})#[0]
        for link in links:
            czas_data = parseDOM(link,'td', attrs={'class': "time dtstart"})[0]
            czas = parseDOM(czas_data,'span')[0]
            godz = getRealTime(czas)
            
            
            event_data =  parseDOM(link,'td', attrs={'class': "event"})[0]
            title = parseDOM(event_data,'span')[0]
            title = godz + ' - ' +title

            href = parseDOM(event_data,'a', ret="href")[0] 
            if 'live.gif' in link:
                title = '[B][COLOR lightgreen]LIVE  [/B][/COLOR]' +title
            out.append({'title':title,'href':href,'empty':'false', 'mode':'getlinks:cric'})
    return out

def ListChannels():
    out=[]
    html = request_sess('http://cricfree.live/live/sky-sports-premier-league', 'get', headers=headers)    

    for x,y in re.findall('href="([^"]+)" title="([^"]+)"',html,re.DOTALL): 

        out.append({'title':y,'href':x,'mode':'playvid:cric','image':'nic'})
    return out

def GetLinks(url):
    zz=''
    out=[]
    html = request_sess(url, 'get', headers=headers)
    channels =  parseDOM(html,'th', attrs={'class': "play channel_names"})[0]
    hreftitle = re.findall('href\s*=\s*"([^"]+)".*?>([^>]+)<\/a>', channels)
    for href,title in hreftitle:
        out.append({'title':title,'href':href,'empty':'false'})
    return out
    
def GetVid(url):
    zz=''
    out=[]

    url = url.replace('/live/','/live/embed/')

    html = request_sess(url, 'get', headers=headers)

    iframe = re.findall('iframe src="([^"]+)"', html,re.DOTALL)[0]
    headers.update({'referer': url})
    html = request_sess(iframe, 'get', headers=headers)
    if re.findall('(cdn\d+\.link\/)',html,re.DOTALL):
        nturl = parseDOM(html, 'iframe', ret='src')[0]
        headers.update({'referer': iframe})
        html = request_sess(nturl, 'get', headers=headers)

    video_url = None

    if 'castfree.me/embed.' in html:
        fid = re.findall('fid="([^"]+)"', html,re.DOTALL)[0]

        url = 'https://castfree.me/embed.php?player=desktop&live='+fid
        headers.update({'referer': iframe})
        html = request_sess(url, 'get', headers=headers)
        str_url = re.findall('return\((\["h","t.*?\])',html, re.DOTALL+re.IGNORECASE)
        video_url=(''.join(ast.literal_eval(str_url[0]))).replace('\\/','/')
        video_url += '|User-Agent={ua}&Referer=https://castfree.me/'.format(ua=UA)
    elif '/poscitech.' in html or 'eplayer.click' in html:
        nturl = parseDOM(html, 'iframe', ret='src')[0]
        headers.update({'referer': iframe})
        html = request_sess(nturl, 'get', headers=headers)
        if '/eplayer.' in html:
            play_url = parseDOM(html, 'iframe', ret='src')[0]
            headers.update({'referer': nturl})
            html = request_sess(play_url, 'get', headers=headers)

            headers.update({'referer': 'https://eplayer.click/'})

            if 'widevine.' in html:

                nturl = parseDOM(html,'iframe', ret="src")[1] 
                html = request_sess(nturl, 'get', headers=headers)
                if 'licenses4.me/player.php?id=eplayer$' in html:

                    fid = re.findall('\?id=(.*?)$',nturl,re.DOTALL)[0]
                    nturl = 'https://player.licenses4.me/player.php?id=eplayer'+fid
                
            else:
                nturl = re.findall('iframe src="([^"]+)"',html,re.DOTALL)[0]
            html = request_sess(nturl, 'get', headers=headers)
            stream=re.compile('source\:\s*"([^"]+)"').findall(html)[-1]
            
            hdr='Referer='+urllib_parse.quote(str(nturl))+'&User-Agent='+UA
            video_url=stream+'|'+hdr
    elif 'daddylive.' in html:
        nturl = parseDOM(html, 'iframe', ret='src')[0]
        from resources.lib import daddy 
        video_url = daddy.GetVid(nturl)
    #elif 'eplayer.click' in html:
    #    nturl = parseDOM(html, 'iframe', ret='src')[0]
    #    nturl = parseDOM(html, 'iframe', ret='src')[0]
    #    headers.update({'referer': iframe})
    #    html = request_sess(nturl, 'get', headers=headers)
        
    #    avc=''
    elif 'tutele.' in html:
        nturl = parseDOM(html, 'iframe', ret='src')[0]
        headers.update({'referer': iframe})
        html = request_sess(nturl, 'get', headers=headers)
        
        iframe = re.findall('iframe src="([^"]+)"', html, re.DOTALL)[0]
        iframe+=urllib_parse.quote_plus(str('http://cricplay2.xyz/'))
        headers.update({'referer': nturl.replace('.sx','.nl')})
        
        html = request_sess(iframe, 'get', headers=headers)
        atob = re.findall('input name=".*?" id=".*?" value="([^"]+)"',html, re.DOTALL)
        xauth=''

        if atob:
            import base64
            atob = base64.b64decode(atob[0]).decode("utf-8")

            CHANNEL = re.findall('CHANNEL\s*=\s*(\{.*?\})',html,re.DOTALL)
            import json
            CHANNEL = json.loads(CHANNEL[0])
            auth = CHANNEL.get('auth', None)

            hea = urllib_parse.urlencode({"Origin": 'https://www.tutele.nl/', "Referer": 'https://www.tutele.nl/','User-Agent': UA, 'Xauth':auth}, safe = '')
            video_url = atob+'|'+hea
    elif 'weakstreams.com/' in html:
        
        nturl = parseDOM(html, 'iframe', ret='src')[0]
        headers.update({'referer': iframe})
        html = request_sess(nturl, 'get', headers=headers)
        playerdata = re.findall('(<script>.*?var player.*?)<', html, re.DOTALL)
        if playerdata:
            playerdata = playerdata[0]
            
            avc=''
            vidgstream = re.findall('vidgstream = "([^"]+)"',playerdata, re.DOTALL)[0]
        
            header = {
                'Host': 'weakstreams.com',
                'User-Agent': UA,
                'Accept': 'application/json',
                'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'Referer': nturl}
        
            url = 'http://weakstreams.com/gethls?idgstream='+urllib_parse.quote_plus(vidgstream)+'&serverid=&cid='
        
            try:
                html = request_sess(url, 'get', headers=header, json = True)
                rawUrl = html.get('rawUrl', None)
        
                video_url = 'http://127.0.0.1:{port}/MLB='.format(port=proxyport)+rawUrl
                try:
        
                    p1p2 = re.findall('rewrittenUrl\s*=\s*url\.replace\("([^"]+)"\s*,\s*"([^"]+)',playerdata, re.DOTALL)[0]
                    if len(p1p2)==2:
                        addon.setSetting("mainurikey",str(p1p2[0]))
                        addon.setSetting("changedurikey",str(p1p2[1]))
                except:
                    pass
            except:
                video_url = ''

    elif 'vikistream.' in html:

        fid = re.findall('fid="([^"]+)"', html,re.DOTALL)
        if fid:
            nturl = 'https://vikistream.com/embed2.php?player=desktop&live='+fid[0]
            headers.update({'referer': url})
            html = request_sess(nturl, 'get', headers=headers)
            str_url = re.findall('return\((\["h","t.*?\])',html, re.DOTALL+re.IGNORECASE)
            video_url=(''.join(ast.literal_eval(str_url[0]))).replace('\\/','/')
            video_url += '|User-Agent={ua}&Referer=https://vikistream.com'.format(ua=UA)
    elif '/gocast' in html:

        fid = re.findall('fid="([^"]+)"', html,re.DOTALL)
        if fid:
            nturl = 'https://gocast2.com/embedcr.php?player=desktop&live='+ fid[0]
            #nturl = 'https://vikistream.com/embed2.php?player=desktop&live='+fid[0]
            headers.update({'referer': iframe})
            html = request_sess(nturl, 'get', headers=headers)

            str_url = re.findall('return\((\["h","t.*?\])',html, re.DOTALL+re.IGNORECASE)
            video_url=(''.join(ast.literal_eval(str_url[0]))).replace('\\/','/')
            video_url += '|User-Agent={ua}&Referer=https://gocast2.com'.format(ua=UA)
    return video_url
        
        
        
