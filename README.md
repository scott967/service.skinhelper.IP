# service.skinhelper.IP
publish IP / GPU / CPU stats for Kodi skins

Updated for Kodi 19+ by scott967
updates copyright 2022 by scott967  Licensed under GPL 2.0-or-later
See LICENSE.md

Usage:

Open Hardware Monitor must be installed and running on the system using this 
addon.  In the Open Hardware Monitor GUI, activate the webserver using the default
local port of 9900 or another port of your choosing (note port ID)

When first installed, service.skinhelper.IP will open a multi-select dialog window
in Kodi, listing the available sensors that can be monitored.  Select as many as
needed and close the dialog using the "OK" button.

All data from the addon is provided via skinning home window property key/value
pairs.  You can use these properties within a skin by adding the appropriate
label controls.  The window property infolabels take the form:
    $INFO[Window(home).Property(SkinHelperIP.sensor0)]
where sensor0 is the first selected sensor, sensor1 the second, etc.

In addition, the system outward-facing IP address is available as:
    $INFO[Window(home).Property(SkinHelperIP.wanip)]
and the LAN IP address is available as:
    $INFO[Window(home).Property(SkinHelperIP.lanip)]

A file, sensorlist.json is created in the active profile  addon_data addon's 
folder to persistently store the active monitored sensor list. Therefor the
addon must have write access to that folder.

Settings:

Available settings are:
    Update interval -- how often the sensors are scanned from Open Hardware Monitor
        (integer default is every 10 secs)
    Open Hardware Monitor port -- the port on which OHM is providing sensor data
        (integer default is 9900)
    Select OHM sensors to monitor -- toggle to display the multi-delect dialog
        (requires Kodi restart -- bool default is true for first run or if
        sensorlist.json is missing, then false)
    Use short values -- sets the value string for all monitored sensors
        (bool default is false) -- default is to provide fully characterized value
        such as "Termperatures - CPU Core #2 - 44.0°C".  When set to true, value will
        be set to "44.0°C"
    Enable debug logging -- enable addon debug logging
        (bool default is false) -- when set to true addon will log raw data received 
        from OHM when Kodi debug level ogging is enabled 
