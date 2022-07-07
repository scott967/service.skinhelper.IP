# -*- coding: utf-8 -*-
"""This module gets system hardware sensor data from OpenHardwareMonitorValues
and sets home window properties with the sonsor data.  See OHMV documentation
for possible senors to monitor.  Sonsors must be edited into the MyAddon class
__init__ constructor method
"""


import urllib.error
import urllib.parse
import urllib.request

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

__addon__               = xbmcaddon.Addon()
__addon_id__            = __addon__.getAddonInfo('id')
__addonname__           = __addon__.getAddonInfo('name')
__icon__                = __addon__.getAddonInfo('icon')
__addonpath__           = xbmcvfs.translatePath(__addon__.getAddonInfo('path'))
WINDOW = xbmcgui.Window(10000)
UPDATE_INTERVAL = __addon__.getSettingInt('update_interval')

class MyMonitor(xbmc.Monitor):
    """Wraps Kodi Monitor class to monitor settings

    Args:
        xbmc.Monitor (class): Kodi's Monitor class
    """

    def onSettingsChanged(self):
        """updates the update interval when user changes the setting"""
        global UPDATE_INTERVAL
        UPDATE_INTERVAL = __addon__.getSettingInt('update_interval')

class MyAddon:
    """class provides all the functions for the addon
    """
    def __init__(self):
        """class constructor executes class instance
        """
        monitor = MyMonitor()
        wip = self.get_wan_ip()
        lanip = self.get_system_ip()
        xbmc.log(f"{__addonname__} ---->WANIP:{wip}", level=xbmc.LOGINFO)
        xbmc.log(f"{__addonname__} ---->LANIP:{lanip}", level=xbmc.LOGINFO)
        WINDOW.setProperty("SkinHelperIP.wanip",wip)
        WINDOW.setProperty("SkinHelperIP.lanip",lanip)
        self.runner(monitor)

    def get_item(self, iinputstring: str, kkkk: int) -> str:
        """parses the iinputstring and returns requested sensor item value

        Args:
            iinputstring (str): results from OHMV
            kkkk (int): sensor item

        Returns:
            str: sensor value
        """
        output = iinputstring.split('"Value": "')
        output2 = output[kkkk]
        output3 = output2.split('", ')
        output4 = output3[0].replace(' ','')
        return output4.strip()

    def get_wan_ip(self) -> str:
        """helper method finds your outward-facing WAN IP addr using ipify

        Returns:
            str: string representation of IP addr in nnn.nnn.nnn.nnn format
        """
        try:
            url="https://api.ipify.org/"
            with urllib.request.urlopen(url) as page:
                data=page.read().decode('utf-8')
            return data
        except Exception as ex:
            self.notify_msg(f'{ex}')

    def runner(self, monitor):
        """daemon runs with default 10 sec update until Kodi exits
        """
        while not monitor.abortRequested():
            try:
                url = "http://127.0.0.1:9900/data.json"
                with urllib.request.urlopen(url) as page:
                    data = page.read().decode('utf-8')
                # print(data)
                #output = data.split('"Value": "')
                # CPU temp
                temp1 = self.get_item(data,20)
                # GPU temp
                temp2 = self.get_item(data,38)
                # CPU load
                temp3 = self.get_item(data,22)
                # GPU load core
                temp4 = self.get_item(data,40)
                # GPU load video engine
                temp5 = self.get_item(data,40)
                WINDOW.setProperty("SkinHelperIP.cputemp",temp1)
                WINDOW.setProperty("SkinHelperIP.gputemp",temp2)
                WINDOW.setProperty("SkinHelperIP.cpulast",temp3)
                WINDOW.setProperty("SkinHelperIP.gpulast",temp4)
                WINDOW.setProperty("SkinHelperIP.gpulastengine",temp5)
            except Exception as exc_msg:
                xbmc.log(f'{__addonname__}:{exc_msg}', level=xbmc.LOGDEBUG)
            monitor.waitForAbort(UPDATE_INTERVAL)

    def notify_msg(self,mss: str):
        """Shows a Kodi notification dialog using JSON-RPC

        Args:
            mss (str): notification message text
        """
        note = (f'{{"id":1,"jsonrpc":"2.0"'
                f'"method":"GUI.ShowNotification", '
                f'"params":{{"title":"IP","message":"{mss}"}}}}')
        result = xbmc.executeJSONRPC(note)

    def get_system_ip(self) ->str:
        """Helper method gets LAN IP addr using Kodi infolabel

        Returns:
            str: string representation of LAN IP addr in nnn.nnn.nnn.nnn format
        """
        json_response = xbmc.getInfoLabel("Network.IPAddress")
        #xbmc.log("out:" + json_response, level=xbmc.LOGINFO)
        return str(json_response)


xbmc.log(f"{__addonname__}: start", level=xbmc.LOGINFO)
MyAddon()
xbmc.log(f"{__addonname__}: stop", level=xbmc.LOGINFO)
