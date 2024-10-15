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

main_url = 'https://methstreams.com/schedules/'

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
	return [{'title':'Schedule','href':'dzien','image':'x','plot':'Methstreams - schedule', 'mode':'listschedule:methstreams'}]

def ListChannels():
	out=[]
	html = request_sess(main_url+'/24-hours-channels.php', 'get', headers=headers)	
	
	for x,y in re.findall('grid-item"><a href="([^"]+)"\starget.*?<strong>([^<]+)<\/strong>',html,re.DOTALL): 
		if sys.version_info < (3,0,0):
			if type(y) is not str:
				y=y.encode('utf-8')
		out.append({'title':y,'href':main_url+x,'mode':'playvid:daddy','image':'nic'})
	return out
def gettime(tstamp):
	from datetime import datetime
	
	timestamp = int(tstamp)/1000# 1545730073
	
	return getRealTime(datetime.utcfromtimestamp(timestamp).strftime('%H:%M'))

def ListSchedule(url):

	out=[]
	
	
	url2 = main_url if 'dzien' in url else url
	
	
	
	
	
	
	
	
	
	response = request_sess(url2, 'get', headers=headers)
	
	if 'dzien' in url:
		
		event_data =  parseDOM(response,'ul', attrs={'class': "nav\s*navbar.*?"})[0]
		
		for href,title in re.findall(' href\s*=\s*"([^"]+)">([^<]+)<',event_data, re.DOTALL):
			href ='https://methstreams.com'+href if href.startswith('/') else href
			out.append({'title':title,'href':href,'image':title, 'empty':'false','mode':'listschedule:methstreams'})
#
	else:
		event_data =  parseDOM(response,'div', attrs={'class': "col-xs-12 col-md-8 col-sm-12"})[0]
		ids = [(a.start(), a.end()) for a in re.finditer('<a', event_data)]
		ids.append( (-1,-1) )

		for i in range(len(ids[:-1])):
			item = event_data[ ids[i][1]:ids[i+1][0] ]
			title1 = parseDOM(item,'h4')[0]
			href = re.findall('href\s*=\s*"([^"]+)"', item,re.DOTALL)[0]
			href = 'https://methstreams.com'+href if href.startswith('/') else href
			czas = parseDOM(item,'p')[0]
			title = czas + ' ' +title1.replace('streams live','')
			icn = parseDOM(item,'img', ret="src")#[0] 
			if icn:
				icn = 'https://methstreams.com'+icn[0] if icn[0].startswith('/') else icn
			else:
				icn ='none'
			out.append({'title':title,'href':href+'|'+urllib_parse.quote_plus(title),'empty':'false','image':icn, 'mode':'playvid:methstreams'})

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
		outx.append({'title':title,'href':t.get('href', None),'empty':'false','mode':'getlinks:sport365'})
	return outx	
		

def GetLinks(url):

	out=[]
	html = request_sess(url, 'get', headers=headers)
	channels =  parseDOM(html,'th', attrs={'class': "play channel_names"})[0]
	hreftitle = re.findall('href\s*=\s*"([^"]+)".*?>([^>]+)<\/a>', channels)
	for href,title in hreftitle:
		out.append({'title':title,'href':href,'empty':'false'})
	return out

def GetVid(url):
	vid_url =''
	url,title = url.split('|')
	html = request_sess(url, 'get', headers=headers)
	iframe = parseDOM(html,'iframe', ret="src")#[0] 
	if iframe:
		headers.update({'referer': url})
		html = request_sess(iframe[0], 'get', headers=headers)

		atob = re.findall('atob\("([^"]+)"',html,re.DOTALL)
		if atob:
			import base64
			vid_url = base64.b64decode(atob[0]).decode("utf-8")
			vid_url +='|Referer='+urllib_parse.quote(str(iframe[0]))+'&User-Agent='+UA
	return vid_url


def get_delta():

	local = datetime.datetime.now()
	utc =  datetime.datetime.utcnow()
	delta = (int((local - utc).days * 86400 + round((local - utc).seconds, -1)))/3600
	return delta
	
def getRealTime(godzina, minus=0):

	delta = get_delta()
	try:
		date_time_obj=datetime.datetime.strptime(godzina, '%H:%M')#+ datetime.timedelta(hours=minus)
	except TypeError:
		date_time_obj=datetime.datetime(*(time.strptime(godzina, '%H:%M')[0:6]))#+ datetime.timedelta(hours=minus)
	date_time_obj = date_time_obj+ datetime.timedelta(hours=int(delta))

	return date_time_obj.strftime("%H:%M")
