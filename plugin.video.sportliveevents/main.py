# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys,re, ast 
import six
from six.moves import urllib_parse

import requests
from requests.compat import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc, xbmcvfs
if six.PY3:
    basestring = str
    unicode = str
    xrange = range
    from resources.lib.cmf3 import parseDOM
else:
    from resources.lib.cmf2 import parseDOM

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(urllib_parse.parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.sportliveevents')

PATH            = addon.getAddonInfo('path')
if six.PY2:
    DATAPATH        = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
else:
    DATAPATH        = xbmcvfs.translatePath(addon.getAddonInfo('profile'))

RESOURCES       = PATH+'/resources/'
FANART=RESOURCES+'../fanart.jpg'
ikona =RESOURCES+'../icon.png'
prawo =RESOURCES+'right.png'
images = RESOURCES+'images/'

exlink = params.get('url', None)
nazwa= params.get('title', None)
rys = params.get('image', None)

try:
    inflabel = ast.literal_eval(params.get('ilabel', None))
except:
    inflabel = params.get('ilabel', None)
    
page = params.get('page',[1])[0]

def encoded_dict(in_dict):
    try:
        # Python 2
        iter_dict = in_dict.iteritems
    except AttributeError:
        # Python 3
        iter_dict = in_dict.items
    out_dict = {}
    for k, v in iter_dict():
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Must be encoded in UTF-8
            v.decode('utf8')
        out_dict[k] = v
    return out_dict
    
def build_url(query):
    return base_url + '?' + urllib_parse.urlencode(encoded_dict(query))
    
    
    
def add_item(url, name, image, mode, itemcount=1, page=1,fanart=FANART, infoLabels=False,contextmenu=None,IsPlayable=False, folder=False):

    if six.PY3:    
        list_item = xbmcgui.ListItem(name)

    else:
        list_item = xbmcgui.ListItem(name, iconImage=image, thumbnailImage=image)
    if IsPlayable:
        list_item.setProperty("IsPlayable", 'True')    
        
    if not infoLabels:
        infoLabels={'title': name}    
    list_item.setInfo(type="video", infoLabels=infoLabels)    
    list_item.setArt({'thumb': image,'icon': image,  'poster': image, 'banner': image, 'fanart': fanart})
    
    if contextmenu:
        out=contextmenu
        list_item.addContextMenuItems(out, replaceItems=True)

    xbmcplugin.addDirectoryItem(
        handle=addon_handle,
        url = build_url({'mode': mode, 'url' : url, 'page' : page, 'title':name,'image':image, 'ilabel':infoLabels}),            
        listitem=list_item,
        isFolder=folder)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%R, %Y, %P")
    
def home():
    add_item('', 'CricFree', images+ 'crfree.png', "listmenu:cric", folder=True,IsPlayable=False)    
  #  add_item('', 'DaddyLive', images+ 'dlive.png', "listmenu:daddy" , folder=True,IsPlayable=False)
    add_item('', 'TVP Sport', images+ 'tvpsport.png', "listmenu:tvpsport", folder=True,IsPlayable=False)
    add_item('', 'SportHD.live', ikona, "listmenu:sporthd", folder=True,IsPlayable=False)
   # add_item('', 'KlubSports', ikona, "listmenu:klubsports", folder=True,IsPlayable=False)
    add_item('', 'FIFA Plus', images+ 'fplus.png', "listmenu:fifaplus", folder=True,IsPlayable=False)
    add_item('', 'Stream2Watch', images+ 's2w.png', "listmenu:stream2watch", folder=True,IsPlayable=False)
  #  add_item('', 'Vipleague', images+ 'vleague.png', "listmenu:vipleague", folder=True,IsPlayable=False)
    add_item('', 'SPORT365.live', images+ 's365.png', "listmenu:sport365", folder=True,IsPlayable=False)
    add_item('', 'Methstreams', ikona, "listmenu:methstreams", folder=True,IsPlayable=False)
	
def import_mod(s):
    mod = {}
    if   s == 'cric': from resources.lib import cricfree as mod
    elif s == 'daddy': from resources.lib import daddy as mod
    elif s == 'sporthd': from resources.lib import sporthd as mod
    
    elif s == 'klubsports': from resources.lib import klubsports as mod
    elif s == 'tvpsport': from resources.lib import tvpsport as mod
    
    elif s == 'fifaplus': from resources.lib import fifaplus as mod
    
    elif s == 'stream2watch': from resources.lib import stream2watch as mod
    elif s == 'vipleague': from resources.lib import vipleague as mod
    elif s == 'sport365': from resources.lib import sport365 as mod
    elif s == 'methstreams': from resources.lib import methstreams as mod
    
    return mod
    
def get_id(id):
    if id:
        
        id = id.lower().replace(' ','_').replace('-schedule','').replace('schedule-','')
        
        id = id.replace('ice_hockey','hockey').replace('football','soccer').replace('american_soccer','football').replace('rugby_union','rugby').replace('combat_sport','fighting').replace('rugby_league','rugby').replace('field_hockey','fieldhockey').replace('ncaa','basketball')
        id = id.replace('winter_sport','skiing').replace('water_sports','waterpolo').replace('billiard','snooker').replace('racing','f1').replace('boxing','fighting').replace('water_polo','waterpolo').replace('e-sports','esports')
        id = id.replace('motorsport','f1').replace('motorsports','f1').replace('mma','fighting').replace('live_now','schedule').replace('motor_sports','f1').replace('nba','basketball').replace('nfl','football')
        if 'mma' in id or 'ufc' in id or 'wwe' in id:
            id = 'fighting'
        elif 'transmisje' in id:
            id ='schedule'
        elif 'calendar' in id:
            id ='schedule'
        elif 'competitions' in id:
            id ='schedule'
        elif 'top_streaming' in id:
            id ='schedule'
    else:
        id = 'icon'
    return images+id+'.png'
    
    
    
def router(paramstring):
    params = dict(urllib_parse.parse_qsl(paramstring))
    if params:    
        mode = params.get('mode', None)

        if 'listmenu' in mode:
            mode2= mode.split(':')[-1]
            mod = import_mod(mode2)
            links = mod.ListMenu()
            for link in links:
                imag = get_id(link.get('title', None))
                
                add_item(name=link.get('title', None), url=link.get('href', None), mode=link.get('mode', None), image=imag, infoLabels={'plot':link.get('plot', None),'title':link.get('title', None)},folder=True, IsPlayable=False)
            if links:
                xbmcplugin.endOfDirectory(addon_handle)    
        elif 'listschedule' in mode:
            mode2= mode.split(':')[-1]
            
            mod = import_mod(mode2)
            links = mod.ListSchedule(exlink)
            modx= ''
            for link in links:
                if link.get('empty', None) == 'true':

                    if link.get('image', None):
                        if not 'http' in link.get('image', None):
                            ikonax = images+'nic.png'
                        else:
                            ikonax = link.get('image', None)
                    else:
                        ikonax = images+'nic.png'
                    add_item(name=link.get('title', None), url=link.get('href', None), mode='empty', image=ikonax, infoLabels={'plot':link.get('title', None),'title':link.get('title', None)},folder=False, IsPlayable=False)

                else:

                    try:
                        if not 'http' in link.get('image', None):
                            imag = ikona
                        else:
                            imag = link.get('image', None)
                            
                    except:
                        imag = ikona
                    if not imag:
                        imag = ikona
                    fold = True
                    ispla = False
                    modx = link.get('mode', None)
                    opis = link.get('plot', None) 
                    opis = opis if opis else link.get('title', None)

                    if 'playvid' in modx:
                        fold = False
                        ispla = True
                        if not 'tvpsport' in mode:
                            imag = images+'play.png'
                    add_item(name=link.get('title', None), url=link.get('href', None), mode=link.get('mode', None), image=imag, infoLabels={'code':link.get('code', None), 'plot':opis ,'title':link.get('title', None)},folder=fold, IsPlayable=ispla)
            if links:
                if 'playvid' in modx:
                    xbmcplugin.setContent(addon_handle, 'videos')
                xbmcplugin.endOfDirectory(addon_handle)    
        
        elif 'listchannels' in mode:
            mode2= mode.split(':')[-1]
            mod = import_mod(mode2)
            if mode2=='klubsports':
                links,ntpage = mod.ListChannels(exlink)
                for link in links:
                    add_item(name=link.get('title', None), url=link.get('href', None), mode=link.get('mode', None), image=ikona, infoLabels={'plot':link.get('title', None),'title':link.get('title', None)},folder=False, IsPlayable=True)
                if ntpage:
                    add_item(name='>> next page >>', url=ntpage, mode='listchannels:klubsports', image=prawo, infoLabels={'plot':'>> next page >>','title':'>> next page >>'},folder=True, IsPlayable=False)

                if links:
                    xbmcplugin.endOfDirectory(addon_handle)    
            elif mode2=='stream2watch':
                links = mod.ListChannels(exlink)
                for link in links:
                    #imag = get_id(link.get('image', None)) if not 'http' in link.get('image', None) else link.get('image', None)
                    modx = link.get('mode', None)
                    ispla = False
                    fold = True
                    #if 'playvid' in modx:
                    #    ispla = True
                    #    fold = False
                    add_item(name=link.get('title', None), url=urllib_parse.unquote(link.get('href', None)), mode=modx, image=ikona, infoLabels={'plot':link.get('title', None),'title':link.get('title', None)},folder=fold, IsPlayable=ispla)
                if links:
                    xbmcplugin.endOfDirectory(addon_handle)    
            else:
                links = mod.ListChannels()
                for link in links:
                    add_item(name=link.get('title', None), url=link.get('href', None), mode=link.get('mode', None), image=ikona, infoLabels={'plot':link.get('title', None),'title':link.get('title', None)},folder=False, IsPlayable=True)
                if links:
                    xbmcplugin.endOfDirectory(addon_handle)    
        
        
        
        elif 'getlinks' in mode:
            mode2= mode.split(':')[-1]
            mod = import_mod(mode2)
            links = mod.GetLinks(exlink)
            for link in links:
                imag = images+'play.png'
                add_item(name=link.get('title', None), url=link.get('href', None), mode='playvid:'+mode2, image=imag, infoLabels={'plot':link.get('title', None),'title':link.get('title', None)},folder=False, IsPlayable=True)
            if links:
                xbmcplugin.endOfDirectory(addon_handle)    
        
        elif 'playvid' in mode:
            mode2= mode.split(':')[-1]
            mod = import_mod(mode2)
            vid_url = mod.GetVid(exlink)
            

            if vid_url:

                if 'tvpsport' in mode or 'fifaplus' in mode or '127.0.' in vid_url or 'sport365' in mode or 'methstreams' in mode:

                    play_item = xbmcgui.ListItem(path=vid_url)
                    play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
                    play_item.setContentLookup(False)
                    if sys.version_info[0] > 2:
                        play_item.setProperty('inputstream', 'inputstream.adaptive')
                    else:
                        play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
                    play_item.setProperty("IsPlayable", "true")

                else:
                    play_item = xbmcgui.ListItem(path=vid_url)

                xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item) 
        elif mode =='listcalendar':
            from resources.lib import fifaplus as mod
            links = mod.ListCalendar()
            for link in links:
                if link.get('empty', None) == 'true':
                    ikonax = images+'nic.png'
                    add_item(name=link.get('title', None), url=link.get('href', None), mode='empty', image=ikonax, infoLabels={'plot':link.get('title', None),'title':link.get('title', None)},folder=False, IsPlayable=False)

                else:
                    try:
                        if not 'http' in link.get('image', None):
                            imag = ikona
                        else:
                            imag = link.get('image', None)
                    except:
                        imag = ikona
                    if not imag:
                        imag = ikona
                    fold = True
                    ispla = False
                    modx = link.get('mode', None)
                    opis = link.get('plot', None) 
                    opis = opis if opis else link.get('title', None)

                    add_item(name=link.get('title', None), url=link.get('href', None), mode=link.get('mode', None), image=imag, infoLabels={'code':link.get('code', None), 'plot':opis ,'title':link.get('title', None)},folder=fold, IsPlayable=ispla)
            if links:

                xbmcplugin.endOfDirectory(addon_handle) 
            

        elif mode =='schedulemenu':
            from resources.lib import vipleague as mod
            links = mod.ListScheduleMenu(exlink)
            for link in links:
                if link.get('empty', None) == 'true':
                    ikonax = images+'nic.png'
                    add_item(name=link.get('title', None), url=link.get('href', None), mode='empty', image=ikonax, infoLabels={'plot':link.get('title', None),'title':link.get('title', None)},folder=False, IsPlayable=False)

                else:
                    try:
                        if not 'http' in link.get('image', None):
                            imag = ikona
                        else:
                            imag = link.get('image', None)
                    except:
                        imag = ikona
                    if not imag:
                        imag = ikona
                    fold = True
                    ispla = False
                    modx = link.get('mode', None)
                    opis = link.get('plot', None) 
                    opis = opis if opis else link.get('title', None)

                    add_item(name=link.get('title', None), url=link.get('href', None), mode=link.get('mode', None), image=imag, infoLabels={'code':link.get('code', None), 'plot':opis ,'title':link.get('title', None)},folder=fold, IsPlayable=ispla)
            if links:

                xbmcplugin.endOfDirectory(addon_handle) 




            
        elif mode =='listretransmisje':
            from resources.lib import tvpsport as mod
            links,ntpage = mod.Retransmisje(exlink)
            for link in links:

                modx = link.get('mode', None)
                opis = link.get('plot', None) 
                opis = opis if opis else link.get('title', None)
                imag = link.get('image', None)

                fold = False
                ispla = True

                add_item(name=link.get('title', None), url=link.get('href', None), mode=link.get('mode', None), image=imag, infoLabels={'code':link.get('code', None), 'plot':opis ,'title':link.get('title', None)},folder=fold, IsPlayable=ispla)
            if links and ntpage:
                add_item(name='>> następna strona >>', url=ntpage, mode='listretransmisje', image=prawo, infoLabels={'plot':'>> następna strona >>','title':'>> następna strona >>'},folder=True, IsPlayable=False)

            xbmcplugin.endOfDirectory(addon_handle)     
            
        elif 'listcompetitions' in mode:
            mode2= mode.split(':')[-1]
            mod = import_mod(mode2)
            links, ntpage  = mod.ListCompetitions(exlink)
            for link in links:

                modx = link.get('mode', None)
                opis = link.get('plot', None) 
                opis = opis if opis else link.get('title', None)
                try:
                    if not 'http' in link.get('image', None):
                        imag = ikona
                    else:
                        imag = link.get('image', None)
                        
                except:
                    imag = ikona
                if not imag:
                    imag = ikona

                fold = True
                ispla = False

                add_item(name=link.get('title', None), url=link.get('href', None), mode=link.get('mode', None), image=imag, infoLabels={'code':link.get('code', None), 'plot':opis ,'title':link.get('title', None)},folder=fold, IsPlayable=ispla)
            if links and ntpage:
                add_item(name='>> następna strona >>', url=ntpage, mode='listretransmisje', image=prawo, infoLabels={'plot':'>> następna strona >>','title':'>> następna strona >>'},folder=True, IsPlayable=False)

            xbmcplugin.endOfDirectory(addon_handle)     
            
            
            
    else:
        home()
        xbmcplugin.endOfDirectory(addon_handle)    
if __name__ == '__main__':
    router(sys.argv[2][1:])