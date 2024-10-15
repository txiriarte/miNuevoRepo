# -*- coding: UTF-8 -*-

import sys,re, ast 
import six
from six.moves import urllib_parse

import requests
from requests.compat import urlparse

import datetime
import time

from resources.lib.brotlipython import brotlidec
if sys.version_info >= (3,0,0):
    from resources.lib.cmf3 import parseDOM
    import html as html
else:
    import HTMLParser
    html = HTMLParser.HTMLParser()
    from resources.lib.cmf2 import parseDOM

sess = requests.Session()

UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'

main_url = 'https://daddylive.eu'

headers = {'user-agent': UA,}

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
        
        
def ListMenu():
    return [{'title':'Channels','href':main_url,'image':'x','plot':'Daddylive - channels', 'mode':'listchannels:daddy'}, {'title':'Schedule','href':'dzien','image':'x','plot':'Daddylive - schedule', 'mode':'listschedule:daddy'}]

def ListChannels():
    out=[]
    html = request_sess(main_url+'/24-hours-channels.php', 'get', headers=headers)    
    
    for x,y in re.findall('grid-item"><a href="([^"]+)"\starget.*?<strong>([^<]+)<\/strong>',html,re.DOTALL): 
        if sys.version_info < (3,0,0):
            if type(y) is not str:
                y=y.encode('utf-8')
        out.append({'title':y,'href':main_url+x,'mode':'playvid:daddy','image':'nic'})
    return out
    
def ListSchedule(url):

    out=[]
    
    html = request_sess(main_url, 'get', headers=headers)
    #if 'day' in url:
    #html = html.replace('<h2></strong>','</h5></strong>')
    #html = html.replace('<center><h2>','<center><h5>')
    html = html.replace('<h3></strong>','</h5></strong>')
    html = html.replace('<center><h3>','<center><h5>')
    
    
    html = html.replace('<h3></strong>','</h2></strong>')
    html = html.replace('<center><h3>','<center><h2>').replace('<h2 style="text-align: center;"><span style="color: #ff0000;">','<h2 style="text-align: center;"><strong>')
    if 'dzien' in url:
        days=html.split('<h5')
    else:
        days=html.split('<h2')
    srt = False
    for day in days:
        if 'dzien' in url and 'Time UK' in day:

            dzien = re.findall('<strong>([^<]+)<',day,re.DOTALL)[0]
            href = urllib_parse.quote(dzien)+'|categ'
            out.append({'title':dzien.split('-')[0],'href':href,'empty':'false','mode':'listschedule:daddy'})
        elif '|' in url:
            dzien,categor = url.split('|')
            
            dzien = urllib_parse.unquote(dzien)
            categor = urllib_parse.unquote(categor)
            if dzien in day:
                blocks=day.split('role=\"alert\"')

                for b in blocks:
                    
                    if categor == 'categ':
                        if 'noopener' in b and '<h4>' in b:
                            categ=re.compile('#ff0000;\">(.*)</span></h4>').findall(b)
                            if len(categ)==1:
                                href = urllib_parse.quote(dzien)+'|'+urllib_parse.quote(categ[0])
                                out.append({'title':categ[0],'href':href,'empty':'false','mode':'listschedule:daddy'})
                    else:
                        if 'noopener' in b and '<h4>' in b and categor in b:
                            srt = True
                            b = b.replace('<hr>' ,'<h4>')
                            zz=''

                            transm = b.split('h4')
                            for tr in transm:

                                srcs=[]
                                if 'href' in tr:

                                    try:

                                        title = re.findall('>([^<]+)<sp', tr,re.DOTALL)[0]
                                    except:
                                        title = re.findall('>([^<]+)<', tr,re.DOTALL)[0]

                                        zz=''
                                    title = re.sub('((\d+\:\d+)\s*\:)', r'\2', title) 
                                    title = title.replace(' - ',' : ')
                                    rozgr = re.findall('\:\d+\s(.*?)(?:\:|\-)',title,re.DOTALL)
                                    
                                    
                                    if rozgr:
                                        title = title.replace(rozgr[0],'[COLOR yellow]'+rozgr[0]+'[/COLOR]')

                                    maintit = re.findall('\:\d+\s(.+?)$',title,re.DOTALL)#[0]

                                    for x,y in re.findall('href="([^"]+)".*?noopener">([^<]+)',tr,re.DOTALL): 

                                        if maintit:
                                            tit = maintit[0]+' - [COLOR khaki]' +y+'[/COLOR]'
                                        else:
                                            tit ='[COLOR khaki]' +y+'[/COLOR]'
                                        srcs.append({'title':tit,'href':x})
                                    srcsx = urllib_parse.quote(str(srcs))
                                    
                                    title = 'z'+ title if title.startswith(('00:','01:','02:','03:')) else title

                                    out.append({'title':title,'href':srcsx})

    if srt:
        out = PosortujData(out)

    return out            

def PosortujData(out):
    outx=[]
    out = sorted(out, key=lambda x: x.get('title', None))
    for t in out:
        title=html.unescape(t.get('title', None)).replace('z0','0')
        if sys.version_info < (3,0,0):
            if type(title) is not str:
                title=title.encode('utf-8')
        czas=re.findall('(.+?)\s',title,re.DOTALL)[0]
    
        godz = getRealTime(czas)
        title = title.replace(czas,godz)
        outx.append({'title':title,'href':t.get('href', None),'empty':'false','mode':'getlinks:daddy'})
    return outx    
        

def GetLinks(url):
    return ast.literal_eval( urllib_parse.unquote(url))

def GetVid(url):

    html = request_sess(url, 'get', headers=headers)
    
    nturl = re.findall('iframe src="([^"]+)" width',html,re.DOTALL)[0]
    headers.update({'referer': url})
    html = request_sess(nturl, 'get', headers=headers)
    
    nturl2 = re.findall('iframe src="([^"]+)" width',html,re.DOTALL)[0]
    headers.update({'referer': nturl})
    
    html = request_sess(nturl2, 'get', headers=headers)
    
    stream=re.compile('source\:\s*"([^"]+)"').findall(html)[-1]
#    hdr='Referer=https://player.licenses4.me/&User-Agent='+UA
    hdr='Referer='+urllib_parse.quote(str(nturl2))+'&User-Agent='+UA
    stream_url=stream+'|'+hdr
    return stream_url

def get_delta():

    local = datetime.datetime.now()
    utc =  datetime.datetime.utcnow()
    delta = (int((local - utc).days * 86400 + round((local - utc).seconds, -1)))/3600
    return delta
    
def getRealTime(godzina, minus=-1):

    delta = get_delta()
    try:
        date_time_obj=datetime.datetime.strptime(godzina, '%H:%M')+ datetime.timedelta(hours=minus)
    except TypeError:
        date_time_obj=datetime.datetime(*(time.strptime(godzina, '%H:%M')[0:6]))+ datetime.timedelta(hours=minus)
    date_time_obj = date_time_obj+ datetime.timedelta(hours=int(delta))

    return date_time_obj.strftime("%H:%M")
