# -*- coding: UTF-8 -*-

import sys,re, ast 
import six
from six.moves import urllib_parse

import requests
from requests.compat import urlparse

import calendar
from datetime import datetime, timedelta
import time

if sys.version_info >= (3,0,0):
	from resources.lib.cmf3 import parseDOM
	import html as html
else:
	import HTMLParser
	html = HTMLParser.HTMLParser()
	from resources.lib.cmf2 import parseDOM

from resources.lib.brotlipython import brotlidec
#from resources.lib.cmf3 import parseDOM

sess = requests.Session()

UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'

headers = {
    'user-agent': UA,
    'accept': 'application/json',
    'accept-language': 'pl,en-US;q=0.7,en;q=0.3',
    'authorization': 'Bearer 0FIQ3SKOSF09NH33IQO7IRARV5BSPT2N',
    'content-type': 'application/json',
    'origin': 'https://www.fifa.com',}

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
    return [{'title':'Live now','href':'cujo','image':'x','plot':'FIFA Plus - live now', 'mode':'listschedule:fifaplus'}, {'title':'Calendar','href':'cujo','image':'x','plot':'FIFA Plus - calendar', 'mode':'listcalendar'}]

    
def ListCalendar():    
    out = []
    days =CreateDays()
    for d in days:
        url = 'https://mcls-api.mycujoo.tv/bff/events/v1beta1?order_by=ORDER_START_TIME_ASC&page_size=65'+d.get('dodane', None)
        out.append({'title':d.get('dzien', None),'href':url,'empty':'false','image':'nic', 'plot':d.get('dzien', None), 'mode':'listschedule:fifaplus'})

    return out
    
def timeNow():
    now=datetime.utcnow()+timedelta(hours=2)

    czas=now.strftime('%Y-%m-%d')

    try:
        format_date=datetime.strptime(czas, '%Y-%m-%d')
    except TypeError:
        format_date=datetime(*(time.strptime(czas, '%Y-%m-%d')[0:6]))    
    return format_date
    
def CreateDays():
    dzis=timeNow()
    timestampdzis = calendar.timegm(dzis.timetuple())
    tydzien = int(timestampdzis)- 2627424
    out=[]
    for i in range(int(timestampdzis),tydzien,-86400):
        x = datetime.utcfromtimestamp(i)

        dzien = (x.strftime('%d.%m'))
        a1 = x.strftime("%Y.%d.%m")

        try:
            current_date_temp = datetime.strptime(a1, "%Y.%d.%m")
        except TypeError:
            current_date_temp = datetime(*(time.strptime(a1, "%Y.%d.%m")[0:6]))
        datastart = (current_date_temp + timedelta(days=-1)).strftime('%Y-%m-%dT')

        dataend = (current_date_temp).strftime('%Y-%m-%dT')
        dod ='&start_after_time='+datastart+'22%3A00%3A00.000Z&start_before_time='+dataend+'22%3A00%3A00.000Z'

        dnitygodnia = ("poniedziałek","wtorek","środa","czwartek","piątek","sobota","niedziela")
        
        day = x.weekday()

        dzientyg = dnitygodnia[day]

        out.append({'dzien':dzientyg+ ' '+dzien,'dodane':str(dod)}) 
        
    return out   
    
    
def getCorrectTime(czas):
    try:
        current_date_temp = datetime.strptime(czas, "%Y-%m-%dT%H:%M:%SZ") #'2022-04-16T12:30:00Z'
    except TypeError:
        current_date_temp = datetime(*(time.strptime(czas, "%Y-%m-%dT%H:%M:%SZ")[0:6]))
    datastart = (current_date_temp + timedelta(hours=+2)).strftime('%H:%M')
    return datastart
    
def ListSchedule(url):
    zz=''
    out=[]

    if not 'mcls-api.mycujoo' in url:
        now = datetime.now()+timedelta(hours=-4)
        czas=now.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        url = 'https://mcls-api.mycujoo.tv/bff/events/v1beta1?order_by=ORDER_START_TIME_ASC&page_size=45&start_after_time='+czas+'&status=EVENT_STATUS_STARTED'
    
    jsdata = request_sess(url, 'get', headers=headers, json=True)
        
    events = jsdata.get('events', None)
    for event in events:
    
        id = event.get('id', None)
        title = event.get('title', None)
        description = event.get('description', None)
        thumbnail_url = event.get('thumbnail_url', None)
        competition_name = event.get('metadata', None).get('competition_name', None)
    
        if event.get('status' , None) == 'EVENT_STATUS_FINISHED':
            metadata = event.get('metadata', None)
    
            try:
                gosp = metadata.get('home_team', None).get('score', None)
                gosc = metadata.get('away_team', None).get('score', None)
    
                title = title.replace(' vs ', ' [COLOR gold][B]('+str(gosp)+':'+str(gosc)+')[/B][/COLOR] ')
                description+='[CR][COLOR gold][B]('+str(gosp)+':'+str(gosc)+')[/B][/COLOR] '
            except:
                title=title
        elif event.get('status' , None) == 'EVENT_STATUS_SCHEDULED':
            start_time = event.get('start_time', None)
    
            cortime = getCorrectTime(start_time)
            title = '[COLOR yellow][B]'+cortime+'[/B][/COLOR] '+title
            description+='[CR][COLOR yellow][B]'+cortime+'[/B][/COLOR] '
    
        elif event.get('status' , None) == 'EVENT_STATUS_STARTED':
            
            title = '[COLOR lightgreen][B]LIVE [/B][/COLOR] '+title
    
        if competition_name:
            title+='  [COLOR khaki]('+competition_name+')[/COLOR]'    
        thumbnail_url = thumbnail_url if thumbnail_url else 'nic'
        out.append({'title':title,'href':id,'empty':'false','image':thumbnail_url, 'plot':description, 'mode':'playvid:fifaplus'})
    return out
    
def GetVid(id):
    stream=''
    url ='https://mls-api.mycujoo.tv/bff/events/v1beta1/'+id
    jsdata = request_sess(url, 'get', headers=headers, json=True)
    error = jsdata.get('streams', None)[0].get('error', None)
    if error:
        message = error.get("message", None)
        if 'geoblocked' in message:
            streams = jsdata.get('metadata', None).get("mcls_internal_data", None)
            for st in streams:
                if st.get('name', None) =='video_url':
                    stream = st.get('value', None)
                    break
    else:
        stream = jsdata.get('streams', None)[0].get('full_url', None)
        if not stream:
            streams = jsdata.get('metadata', None).get("mcls_internal_data", None)
            for st in streams:
                if st.get('name', None) =='video_url':
                    stream = st.get('value', None)
                    break

    return stream
