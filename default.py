# -*- coding: utf-8 -*-
"""This module gets system hardware sensor data from OpenHardwareMonitorValues
and sets home window properties with the sonsor data.  See OHMV documentation
for possible senors to monitor.  Sonsors must be edited into the MyAddon class
__init__ constructor method
"""


import json
import os.path
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
__addonprofile__        = xbmcvfs.translatePath(__addon__.getAddonInfo('profile'))
xbmc.log(f'{__addonname__}: profile path: {__addonprofile__}', level=xbmc.LOGDEBUG)
WINDOW = xbmcgui.Window(10000)
UPDATE_INTERVAL = __addon__.getSettingInt('update_interval')
OHM_PORT = __addon__.getSettingInt('OHM_port')
SHORT_VALUE = __addon__.getSettingBool('Short_value')
ENABLE_DEBUG = __addon__.getSettingBool('Enable_debug')
UPDATE_FAILED = False

class MyMonitor(xbmc.Monitor):
    """Wraps Kodi Monitor class to monitor settings

    Args:
        xbmc.Monitor (class): Kodi's Monitor class
    """

    def onSettingsChanged(self):
        """updates the update interval when user changes the setting"""
        global UPDATE_INTERVAL
        global OHM_PORT
        global SHORT_VALUE
        global ENABLE_DEBUG
        global UPDATE_FAILED
        UPDATE_INTERVAL = __addon__.getSettingInt('update_interval')
        if OHM_PORT != __addon__.getSettingInt('OHM_port'):
            UPDATE_FAILED = False
        OHM_PORT = __addon__.getSettingInt('OHM_port')
        SHORT_VALUE = __addon__.getSettingBool('Short_value')
        ENABLE_DEBUG = __addon__.getSettingBool('Enable_debug')

class MyAddon:
    """class provides all the functions for the addon
    """
    def __init__(self):
        """class constructor executes class instance
        """
        monitor = MyMonitor()
        GET_SENSORS = __addon__.getSettingBool('get_sensors')
        if GET_SENSORS or not os.path.exists(os.path.join(__addonprofile__, 'sensorlist.json')):
            self.update_sensors()
            __addon__.setSettingBool('get_sensors', False)
        with open(os.path.join(__addonprofile__, 'sensorlist.json'), 'rb') as json_sensor:
            activesensorlist = json.load(json_sensor)
        wip = self.get_wan_ip()
        lanip = self.get_system_ip()
        xbmc.log(f"{__addonname__} ---->WANIP:{wip}", level=xbmc.LOGINFO)
        xbmc.log(f"{__addonname__} ---->LANIP:{lanip}", level=xbmc.LOGINFO)
        WINDOW.setProperty("SkinHelperIP.wanip",wip)
        WINDOW.setProperty("SkinHelperIP.lanip",lanip)
        self.runner(monitor, activesensorlist)

    def update_sensors(self):
        """gets the active sensors from OHM as a list of dicts and opens a multi-
        select dialog to allow the user to select which sensors to monitor.  The
        monitored sensors are saved to sensorlist.json as a serialized list of sensor ids,
        """
        try:
            with open(os.path.join(__addonprofile__, 'sensorlist.json'), 'w') as json_sensor:
                url = f"http://127.0.0.1:{OHM_PORT}/data.json"
                with urllib.request.urlopen(url) as page:
                    data = page.read().decode('utf-8')
                data = json.loads(data)
                sensorlist = []
                sensorlist = self.traverse_tree(data, sensorlist)
                sensorlist_as_string = []
                for sensor in sensorlist:
                    new_sensor = f'id {sensor["id"]} -- {sensor["Text"]}'
                    sensorlist_as_string.append(new_sensor)
                if ENABLE_DEBUG:
                    xbmc.log(f'{__addonname__}: update num sensors: {len(sensorlist)} sensorlist {sensorlist}', level=xbmc.LOGDEBUG)
                active_sensors_index = xbmcgui.Dialog().multiselect(
                                        __addon__.getLocalizedString(32004),
                                        sensorlist_as_string)
                active_sensors = []
                for index in active_sensors_index:
                    active_sensors.append(sensorlist[index]['id'])
                json.dump(active_sensors, json_sensor)
        except Exception as ex:
            self.notify_msg(f'udate sensor list fail {ex}')

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
            self.notify_msg(f'get api.ipify.org fail {ex}')

    def traverse_tree(self, tree: dict, sensorlist: list, parent_text = '') -> list:
        """traverses over the OHM sensor tree dict to retrieve sensor id, text,
        and value for each node

        Args:
            tree (dict): a dict with 0 or more children as a list
            sensorlist (list): the list of sensors, each sensor is a dict

        Returns:
            list: the updated sensor list
        """
        if tree['Children'] == []:
            node = {'id':tree['id'], 'Text':(parent_text + tree['Text']), 'Value':tree['Value']}
            sensorlist.append(node)
            #xbmc.log(f'{__addonname__}: node {node} type {type(sensorlist)} sensors: {len(sensorlist)} {sensorlist}', level=xbmc.LOGDEBUG)
            return sensorlist
        else:
            parent_text = tree.get('Text', '') + ' - '
            #xbmc.log(f'{__addonname__}: parent text {parent_text}', level=xbmc.LOGDEBUG)
            for child in tree['Children']:
                sensorlist = self.traverse_tree(child, sensorlist, parent_text)
            return sensorlist

    def runner(self, monitor, activesensorlist):
        """daemon runs with default 10 sec update until Kodi exits

        Args:
            monitor (xbmc.Monitor): a monitor to check for exit
            activesensorlist (list): a list of int of 0-5 sensors to minitor
        """
        global UPDATE_FAILED
        while not monitor.abortRequested():
            try:
                url = f"http://127.0.0.1:{OHM_PORT}/data.json"
                with urllib.request.urlopen(url) as page:
                    data = page.read().decode('utf-8')
                data2 = json.loads(data)
                #xbmc.log(f'{__addonname__}: data2 {data2}', level=xbmc.LOGDEBUG)
                sensorlist = []
                sensorlist = self.traverse_tree(data2, sensorlist)
                if ENABLE_DEBUG:
                    xbmc.log(f'{__addonname__}: runner sensorlist {sensorlist} activesensorlist {activesensorlist}', level=xbmc.LOGDEBUG)
                sensordata = []
                for id_sensor in activesensorlist:
                    for index in sensorlist:
                        if index['id'] == id_sensor:
                            if SHORT_VALUE:
                                sensordata.append(f'{index["Value"]}')
                            else:
                                sensordata.append(f'{index["Text"]} {index["Value"]}')
                if ENABLE_DEBUG:
                    xbmc.log(f'{__addonname__}: sensordata {sensordata}',
                                level=xbmc.LOGDEBUG)
                for count, sensor_value in enumerate(sensordata):
                    WINDOW.setProperty(f'SkinHelperIP.sensor{count}', sensor_value)
            except Exception as exc_msg:
                xbmc.log(f'{__addonname__}: runner exc message {exc_msg}',
                            level=xbmc.LOGDEBUG)
                if not UPDATE_FAILED:
                    UPDATE_FAILED = True
                    self.notify_msg('Check OHM port assignment[CR]in settings')
            monitor.waitForAbort(UPDATE_INTERVAL)

    def notify_msg(self,mss: str):
        """Shows a Kodi notification dialog using JSON-RPC

        Args:
            mss (str): notification message text
        """
        note = (f'{{"id":1,"jsonrpc":"2.0", '
                f'"method":"GUI.ShowNotification", '
                f'"params":{{"title":"Skinhelper IP","message":"{mss}"}}}}')
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
