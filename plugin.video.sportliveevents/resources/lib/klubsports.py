# -*- coding: UTF-8 -*-

import sys,re, ast 
import six
from six.moves import urllib_parse

import requests
from requests.compat import urlparse

import datetime
import time

import html
from resources.lib.brotlipython import brotlidec
if sys.version_info >= (3,0,0):
	from resources.lib.cmf3 import parseDOM
else:
	from resources.lib.cmf2 import parseDOM

sess = requests.Session()

UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'

main_url = 'https://klubsports.xyz/'
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
	return [{'title':'Channels','href':'0|40','image':'x','plot':'Klubsports - channels', 'mode':'listchannels:klubsports'}, {'title':'Schedule','href':'dzien','image':'x','plot':'Klubsports - schedule', 'mode':'listschedule:klubsports'}]

def ListSchedule(url):
	zz=''
	out=[]

	srt = False
	html = request_sess(main_url, 'get', headers=headers)
	if 'dzien' in url:

		kategs = re.findall('<h4><.*?">([^<]+)<', html, re.DOTALL)
		for kateg in kategs:
			href = urllib_parse.quote(kateg)
			out.append({'title':kateg,'href':href,'empty':'false','image':kateg.lower().replace(' ','_'),'mode':'listschedule:klubsports'})
			avb=''
	else:
		
		kateg = urllib_parse.unquote(url)
		html = html.replace('&copy;','<h4>')
		
		events = re.findall('">'+kateg+'(.*?)<h4>',html,re.DOTALL)
		if events:
			srt = True
			events = events[0].replace('<p>','').replace('<strong>','<br>')
			for event in re.findall('\\n(.*?)<br>',events,re.DOTALL):
				srcs=[]

				try:
					title = re.findall('(\d+\:.*?)<',event,re.DOTALL)[0]
					title = 'z'+ title if title.startswith(('00:','01:','02:','03:')) else title	
					maintit = re.findall('\:\d+\s(.+?)$',title,re.DOTALL)[0]
					for x,y in re.findall('/>([^<]+)<.*?href="([^"]+)',event,re.DOTALL): 
						srcs.append({'title':maintit+' - [COLOR khaki]' +x+'[/COLOR]','href':y})	
					srcsx = urllib_parse.quote(str(srcs))	
					out.append({'title':title,'href':srcsx})	
				except:
					continue

	if srt:
		out = PosortujData(out)
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
	
def ListChannels(url):
	st,end = url.split('|')
	out=[]
	html = request_sess(main_url, 'get', headers=headers)	

	kanaly = re.findall('<a href="([^"]+)" target.*?strong>([^<]+)<',html,re.DOTALL)
	kanlylista= kanaly[int(st):int(end)]
	nturl = False
	if int(st)<len(kanaly):
		pocz = int(end)#+1
		kon = pocz+40
		nturl = '%s|%s'%(str (pocz),str (kon) )
	
	for href,title in kanlylista:
		href = 'https://klubsports.xyz'+href
		
		out.append({'title':title,'href':href,'mode':'playvid:klubsports','image':'nic'})

	return out,nturl

def GetLinks(url):
	return ast.literal_eval( urllib_parse.unquote(url))
	
def GetVid(url):
	zz=''
	out=[]
	if not 'poscitech.php' in url:
		html = request_sess(url, 'get', headers=headers)
	
		nturl = re.findall('iframe.*?src="([^"]+)"\s*name',html,re.DOTALL)[0]
		headers.update({'referer': url})
		html = request_sess(nturl, 'get', headers=headers)
	
		id = re.findall('id=(\d+); width',html,re.DOTALL)[0]
		fid = re.findall('var fid=id(.*?);',html,re.DOTALL)[0]
		fid = str(eval(str(id)+fid))
		headers.update({'referer': nturl})
		nturl = 'https://eplayer.click/premiumtv/klubsports.php?id='+fid
		html = request_sess(nturl, 'get', headers=headers)
		headers.update({'referer': nturl})
	else:
		headers.update({'referer': 'https://poscitech.click/'})
		html = request_sess(url, 'get', headers=headers)
		headers.update({'referer': 'https://eplayer.click/'})
	
	nturl = url
	if not 'eplayer.click streaming' in html:
		nturl = re.findall('iframe src="([^"]+)"',html,re.DOTALL)[0]
		html = request_sess(nturl, 'get', headers=headers)
	stream=re.compile('source\:\s*"([^"]+)"').findall(html)[-1]
	
	hdr='Referer='+urllib_parse.quote(str(nturl))+'&User-Agent='+UA
	stream_url=stream+'|'+hdr
	return stream_url
