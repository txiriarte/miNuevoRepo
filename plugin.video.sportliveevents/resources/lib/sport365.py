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

main_url = 'https://sport365.live/'

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
	return [{'title':'Schedule','href':'dzien','image':'x','plot':'Sport365 - schedule', 'mode':'listschedule:sport365'}]

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
	
	
	#dt_object = datetime.fromtimestamp(timestamp)	
	#return dt_object
def ListSchedule(url):

	out=[]
	headersx = {
		'Host': 'sport365.live',
		'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
		'accept-language': 'pl,en-US;q=0.7,en;q=0.3',
		'dnt': '1',
		'upgrade-insecure-requests': '1',
		'sec-fetch-dest': 'document',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-site': 'none',
		'sec-fetch-user': '?1',
		# Requests doesn't support trailers
		# 'te': 'trailers',
	}
	
	
	
	
	
	
	
	
	
	response = request_sess(main_url, 'get', headers=headersx)
	
	mainurl = re.findall('onclick\s*=\s*"window\.open\("(.*?)\$\{',response, re.DOTALL)[-1]
	headersx = {
		'Host': 'sport365.live',
		'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0',
		'accept': '*/*',
		'accept-language': 'pl,en-US;q=0.7,en;q=0.3',
		'referer': 'https://sport365.live/',
		'dnt': '1',
		'sec-fetch-dest': 'empty',
		'sec-fetch-mode': 'cors',
		'sec-fetch-site': 'same-origin',

	}
	response = request_sess('https://sport365.live/assets/events.json', 'get', headers=headersx, json=True)
	for jsdata in response:

		home = jsdata.get('home', None)
		away = jsdata.get('away', None)

		pair = home+' vs '+away if away else home
		t1 = pair
		typ = (jsdata.get('type', None)).replace(' ','-').replace('/','-')	.lower()

		pair = (pair.replace(' ','-').replace('/','-'))	.lower()
		czas = gettime(jsdata.get('time', None))

		streams=[]
		langs=[]
		for x in jsdata.get("streams", None):
			ch = x.get('ch', None)
			lang = x.get('lang', None)
			url_player = mainurl+typ+'/'+pair+'?player='+ch
			title = '[B][COLOR yellowgreen]'+czas+ '[/COLOR] '+home+' vs '+away +' [COLOR yellowgreen](%s)'%lang+'[/COLOR][/B]'
			langs.append(str(lang))

			streams.append({'title':title,'href':url_player}) 
		if streams:

			title1 = '[COLOR yellowgreen][B]'+ str(czas) + '[/COLOR] ' +t1 + ' [COLOR yellowgreen]'+str(langs).replace("'",'')+'[/COLOR][/B]'
			home = home.replace(' ','-').replace('/','-')
			out.append({'title':title1,'href':urllib_parse.quote_plus(str(streams)),'empty':'false','mode':'getlinks:sport365'})
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

	return ast.literal_eval( urllib_parse.unquote_plus(url))

def GetVid(url):
	UAx = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0'
	headersx = {
		'Host': 'h5.sportstreams.link',
		'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
		'accept-language': 'pl,en-US;q=0.7,en;q=0.3',
		'dnt': '1',
		'upgrade-insecure-requests': '1',
		'sec-fetch-dest': 'document',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-site': 'cross-site',
		# Requests doesn't support trailers
		# 'te': 'trailers',
	}
	response = request_sess(url, 'get', headers=headersx)

	src = re.findall('source\s*src\s*=\s*"([^"]+)',response,re.DOTALL)[0]
	host = urlparse(url).netloc
	vid_url = 'https://'+host+src if src.startswith('/') else 'https://'+host+'/'+src
	vid_url += '|User-Agent='+UAx+'&Referer='+urllib_parse.quote_plus(url)
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
