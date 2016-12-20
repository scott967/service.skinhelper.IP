# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import sys
import json
import os
import xbmcgui
import urllib2

__addon__               = xbmcaddon.Addon()
__addon_id__            = __addon__.getAddonInfo('id')
__addonname__           = __addon__.getAddonInfo('name')
__icon__                = __addon__.getAddonInfo('icon')
__addonpath__           = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')
__settings__            = xbmcaddon.Addon(id="service.skinhelper.IP")
WINDOW = xbmcgui.Window(10000)

class MyAddon:
    def GetItem(abwo,iinputstring,kkkk):
        output = iinputstring.split('"Value": "')
        output2 = output[kkkk]
        output3 = output2.split('", ')
        output4 = output3[0].replace(' ','')
        return output4.strip()

    def GetWANIP(self):
         try:
            url="https://api.ipify.org/"
            page =urllib2.urlopen(url)
            data=page.read()
            return str(data)
         except Exception as ex:
            self.Msg(str(ex))

    def __init__(self):
         wip = self.GetWANIP()
         lanip = self.GetSystemIP()
         xbmc.log("---->WANIP:" + wip, level=xbmc.LOGNOTICE)
         xbmc.log("---->LANIP:" + lanip, level=xbmc.LOGNOTICE)
         WINDOW.setProperty("SkinHelperIP.wanip",wip)
         WINDOW.setProperty("SkinHelperIP.lanip",lanip)
         count = 0
         while(not xbmc.abortRequested):
             xbmc.sleep(100)
             count += 1
             if count == 50:
                count = 1
                try:
                      url="http://127.0.0.1:9900/data.json"
                      page =urllib2.urlopen(url)
                      data=page.read()
                      # print(data)
                      #output = data.split('"Value": "')
                      # CPU temp
                      temp1 = self.GetItem(data,20)
                      # GPU temp
                      temp2 = self.GetItem(data,38)
                      # CPU load
                      temp3 = self.GetItem(data,22)
                      # GPU load core
                      temp4 = self.GetItem(data,40)
                      # GPU load video engine
                      temp5 = self.GetItem(data,40)
                      
                      WINDOW.setProperty("SkinHelperIP.cputemp",temp1)
                      WINDOW.setProperty("SkinHelperIP.gputemp",temp2)
                      WINDOW.setProperty("SkinHelperIP.cpulast",temp3)
                      WINDOW.setProperty("SkinHelperIP.gpulast",temp4)
                      WINDOW.setProperty("SkinHelperIP.gpulastengine",temp5)
                      
                      
                except Exception , msg:
                      xbmc.log("IP Helper:" + str(msg[0]) + ' , Error message : ' + msg[1], level=xbmc.LOGNOTICE)
                        
    def Msg(self,mss):
         note = '{"id":1,"jsonrpc":"2.0","method":"GUI.ShowNotification","params":{"title":"IP","message":"' + mss + '"}}'
         result = xbmc.executeJSONRPC(note)
         
    def GetSystemIP(self):
        json_response = xbmc.getInfoLabel("Network.IPAddress")
        #xbmc.log("out:" + json_response, level=xbmc.LOGNOTICE)
        return str(json_response)


xbmc.log("IP Helper service: start", level=xbmc.LOGNOTICE)
MyAddon()
xbmc.log("IP Helper service: stop", level=xbmc.LOGNOTICE)
     
