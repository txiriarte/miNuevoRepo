# -*- coding: utf-8 -*-


import threading

import requests


try:  # Python 3
    from http.server import BaseHTTPRequestHandler
except ImportError:  # Python 2
    from BaseHTTPServer import BaseHTTPRequestHandler

try:  # Python 3
    from socketserver import TCPServer
except ImportError:  # Python 2
    from SocketServer import TCPServer


import xbmcaddon, xbmc
addon = xbmcaddon.Addon('plugin.video.sportliveevents')

class Proxy(BaseHTTPRequestHandler):

    server_inst = None

    @staticmethod
    def start():
        """ Start the Proxy. """

        def start_proxy():
            """ Start the Proxy. """
            Proxy.server_inst = TCPServer(('127.0.0.1', 0), Proxy)

            port = Proxy.server_inst.socket.getsockname()[1]
            addon.setSetting('proxyport', str(port))

            Proxy.server_inst.serve_forever()

        thread = threading.Thread(target=start_proxy)
        thread.start()

        return thread

    @staticmethod
    def stop():
        """ Stop the Proxy. """
        if Proxy.server_inst:
            Proxy.server_inst.shutdown()
    def do_HEAD(self):

        self.send_response(200)
        self.end_headers()
    def do_GET(self):  
    
        path = self.path 
        if 'MLB=' in path:
            try:
                m3u_url = (path).split('MLB=')[-1]
    
                if 'm3u8' in m3u_url:
    
                    result = requests.get(m3u_url, verify=False, timeout = 30).content
                    result = result.decode(encoding='utf-8', errors='strict')
                    mainuri =     addon.getSetting("mainurikey")
                    changedurikey =     addon.getSetting("changedurikey")
    
                    manifest_data = result.replace(mainuri,changedurikey)
    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/x-mpegURL')
                    self.end_headers()
                    self.wfile.write(manifest_data.encode(encoding='utf-8', errors='strict'))
                elif (m3u_url).endswith('.ts'):
                    result=requests.get(m3u_url, verify=False, timeout = 30).content
                
                    self.send_response(200)
                    self.send_header('Content-Type', 'video/mp2t')
                    
                    self.send_header('Content-Length', len(result))
                    self.end_headers()
    
                    self.wfile.write(result)

            except Exception as exc: 
                xbmc.log('blad w proxy: %s'%str(exc), level=xbmc.LOGINFO)
                self.send_response(500)
                self.end_headers()

