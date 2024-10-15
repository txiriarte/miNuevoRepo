# -*- coding: UTF-8 -*-

import sys,re, ast 
import six
from six.moves import urllib_parse

import requests
from requests.compat import urlparse

import datetime
import time

if sys.version_info >= (3,0,0):

    import html as html
else:
    import HTMLParser
    html = HTMLParser.HTMLParser()

from resources.lib.brotlipython import brotlidec
if sys.version_info >= (3,0,0):
    from resources.lib.cmf3 import parseDOM
else:
    from resources.lib.cmf2 import parseDOM

sess = requests.Session()

UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'

main_url = 'https://1.vecdn.pw/program.php'
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
        
def ListMenu():
    return [{'title':'Channels','href':main_url,'image':'x','plot':'sporthd - channels', 'mode':'listchannels:sporthd'}, {'title':'Schedule','href':'dzien','image':'x','plot':'Cricfree - schedule', 'mode':'listschedule:sporthd'}]

def ListSchedule(url):
    zz=''
    out=[]
    html = request_sess(main_url, 'get', headers=headers)
    days = html.split('<button class="accordion">')
    categ = ''
    srt = False

    for day in days:
        if '"fas fa-calendar"' in day:
            
            if 'dzien' in url:
                title = re.findall('fff;">([^<]+)<',day,re.DOTALL)[0]
                href = urllib_parse.quote(title.strip(' '))+'|categ'
                out.append({'title':title,'href':href,'empty':'false','mode':'listschedule:sporthd'})
            elif '|' in url:
                srt = True
                dzien,categ = url.split('|')
                dzien = urllib_parse.unquote(dzien)
                categor = urllib_parse.unquote(categ)
                
                if dzien in day:
                    for event in day.split('<!--p---'):
                        srcs=[]
                        if 'allowFullScreen' in event:
                            event = re.sub('(<span class\=".*?">)','',event)
                            event = re.sub('(<\/span>)','',event)
                            
                            competitions = re.findall('<div class="left\d+">([^<]+)<',event)[0]
                            tytul = re.findall('(\d+.*?)\\n',competitions,re.DOTALL)

                            if len(tytul)>1:

                                for t in tytul:
                                
                                    for i, href in enumerate(re.findall('href="([^"]+)"',event,re.DOTALL), start=1 ):
                                        
                                        srcs.append({'title':t+' Link %s'%(str(i)),'href':href})
                                        srcsx = urllib_parse.quote(str(srcs))
                                    out.append({'title':t,'href':srcsx})

                            else:
                                try:
                                    tytul = re.findall('(\d+.*?)$',competitions,re.DOTALL)
                                except:
                                    pass
                                for i, href in enumerate(re.findall('href="([^"]+)"',event,re.DOTALL), start=1 ):
                                    
                                    try:
                                        srcs.append({'title':tytul[0]+' Link %s'%(str(i)),'href':href})
                                    except:
                                        pass
                                    srcsx = urllib_parse.quote(str(srcs))
                                out.append({'title':tytul[0],'href':srcsx})

                            
    if srt:
        out = PosortujData(out)

    return out    
    
def PosortujData(out):
    outx=[]
    out = sorted(out, key=lambda x: x.get('title', None))
    for t in out:
        title=html.unescape(t.get('title', None))

        czas=re.findall('(.+?)\s',title,re.DOTALL)[0]

        godz = getRealTime(czas, minus = -3)
        title = title.replace(czas,godz)
        outx.append({'title':title,'href':t.get('href', None),'empty':'false','mode':'getlinks:sporthd'})
    return outx    
    
def ListChannels():
    out=[]
    html = request_sess(main_url, 'get', headers=headers)    

    for x,y in re.findall('href="([^"]+)" target=.*?"tvch">([^<]+)<',html,re.DOTALL): 

        out.append({'title':y,'href':x,'mode':'playvid:sporthd','image':'nic'})
    return out

def GetLinks(url):
    return ast.literal_eval( urllib_parse.unquote(url))
    
def GetVid(url):
    zz=''
    out=[]

    html = request_sess(url, 'get', headers=headers)

    video_url = ''
    fid = re.findall('fid="([^"]+)"', html,re.DOTALL)
    
    if 'ragnaru.net' in html:
        if fid:
            nturl = 'https://ragnaru.net/jwembed.php?player=desktop&live='+fid[0]
            headers.update({'referer': url})
            html = request_sess(nturl, 'get', headers=headers)
            video_url = re.findall('file\:\s*"([^"]+)"',html,re.DOTALL)
            if video_url:
                video_url = video_url[0]+ '|User-Agent={ua}&Referer={ref}'.format(ref=nturl,ua=UA)
    elif 'vikistream.' in html:
        if fid:
            nturl = 'https://vikistream.com/embed2.php?player=desktop&live='+fid[0]
            headers.update({'referer': url})
            html = request_sess(nturl, 'get', headers=headers)
            str_url = re.findall('return\((\["h","t.*?\])',html, re.DOTALL+re.IGNORECASE)
            video_url=(''.join(ast.literal_eval(str_url[0]))).replace('\\/','/')
            video_url += '|User-Agent={ua}&Referer=https://vikistream.com'.format(ua=UA)
        #    
    elif 'nuevoplayer.' in html:
        fid = re.findall('nuevoplayer\.php\?id=(.*?)"',html,re.DOTALL)#[0]
        if fid:
            nturl = 'https://widevine.licenses4.me/nuevo.php?id='+fid[0]
            headers.update({'referer': url})
            html = request_sess(nturl, 'get', headers=headers)

            str_url = re.findall('src\:\s*"([^"]+)"',html, re.DOTALL+re.IGNORECASE)
            video_url=str_url[1]
            video_url += '|User-Agent={ua}&Referer=https://widevine.licenses4.me'.format(ua=UA)

    else:
        nturl = re.findall('iframe src="([^"]+)"',html,re.DOTALL)[0]
        nturl = 'https:' +nturl if nturl.startswith('//') else nturl
        headers.update({'referer': url})
        resp = request_sess(nturl, 'get', headers=headers, result=False)
        html = resp.text
        packer = re.compile('(eval\(function\(p,a,c,k,e,(?:r|d).*)')
        packeds = packer.findall(html)
        unpacked = ''
    
        if packeds:
            import resources.lib.jsunpack as jsunpack
            for packed in packeds:
                unpacked += jsunpack.unpack(packed)
            video_url = re.findall('var src="([^"]+)"',unpacked,re.DOTALL)
        else:
            nturl = nturl.replace('nuevoplayer.php','nuevo.php')
            html = request_sess(nturl, 'get', headers=headers, result=True)
            video_url = re.findall('src: "(.*m3u8)"',html,re.DOTALL)

        if video_url:
            video_url = video_url[0]+ '|User-Agent={ua}&Referer={ref}'.format(ref=nturl,ua=UA)
    return video_url
