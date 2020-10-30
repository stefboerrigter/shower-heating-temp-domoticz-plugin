# Shower Temp Override plugin
#
# Author: SBoerrigter
#
"""
<plugin key="ShowerTempPlugin" name="Showering Temperature Plugin" author="sboerrigter" version="1.0.0">
    <description>
        <h2>Domoticz Shower thermostat Plugin</h2><br/>
        
        <h3>Features</h3>
        Still Open, todo fill this in
        <ul style="list-style-type:square">
            <li>Feature one...</li>
            <li>Feature two...</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>Device Type - What it does...</li>
        </ul>
        <h3>Configuration</h3>
        Configuration options...
    </description>
    <params>
        <param field="Address" label="Domoticz IP Address" width="200px" required="true" default="localhost"/>
        <param field="Port" label="Port" width="40px" required="true" default="8080"/>
        <param field="Mode1" label="IDX Main Thermostat" width="300px" required="true" default="80"/>
        <param field="Mode2" label="IDX Bathroom Thermostat" width="300px" required="true" default="50"/>
        <param field="Mode3" label="Main Therm override temp (deg C)" width="100px" required="true" default="2"/>
        <param field="Mode4" label="Bathroom Thermostat override temp (deg C)" width="100px" required="true" default="8"/>
        <param field="Mode5" label="Bathroom temp setting time (minutes)" width="100px" required="true" default="45"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="Extra verbose" value="Verbose+"/>
                <option label="Verbose" value="Verbose"/>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import json
from urllib import parse, request
from datetime import datetime, timedelta
import time
import base64
import itertools
from distutils.version import LooseVersion
from enum import Enum

class HeatingState(Enum):
    state_init      = 0
    state_idle      = 1
    state_activated = 2
    state_active    = 3
    state_closedown = 4

class Thermostats(Enum):
    main_therm       = 0
    bath_therm       = 1

class BasePlugin:

    def __init__(self):
        #TODO; cleanup!!
        self.debugging = "Debug"
        self.mainthermSet = 80
        self.mainthermGet = 79
        self.bathhermSet  = 50
        self.bathThermGet = 60
        self.mainoverr = 2
        self.bathoverr = 8
        self.timeoverr = 30
        self.heartBeatsLeft = 0
        self.heartBeatsRequired = 0
        self.state = HeatingState.state_init

        self.SavedThermostatSetpoints = {
            Thermostats.main_therm : 0,
            Thermostats.bath_therm : 0,
        }

        return

    '''
    State handler for Initializing the module
    '''
    def state_handler_init(self):
        Domoticz.Log("State handler INIT")
        self.state = HeatingState.state_idle

    '''
    State handler for idle, waiting for user input
    '''
    def state_handler_idle(self):
        Domoticz.Log("State handler IDLE")

    '''
    State handler for Activated -> Triggered, setting up 
    then proceed to state active
    '''
    def state_handler_activated(self):
        Domoticz.Log("State handler ACTIVATED")
        if self.storeTemperatures():
            self.setSetpointTemperaturesHigh()
            self.heartBeatsLeft = int(self.heartBeatsRequired)
            #Domoticz.Log("onHeartbeat Feature Active ==> " + str(self.heartBeatsLeft) + " >= "  + str(self.heartBeatsRequired))
            self.state = HeatingState.state_active

    '''
    State handler for active plugin, Keep heating untill 
    time has elapsed
    '''
    def state_handler_active(self):
        Domoticz.Log("State handler Active [" + str(self.heartBeatsLeft) + "]")
        self.heartBeatsLeft = self.heartBeatsLeft - 1
        if (int(self.heartBeatsLeft) <= 0): # int(self.heartBeatsRequired)):
            self.state = HeatingState.state_closedown

    def state_handler_closedown(self):
        Domoticz.Log("State handler Close")
        self.restoreSetpointTemperatures()
        Devices[1].Update(0, str(0)) #Switch off wrapper??
        self.state = HeatingState.state_init


    def initialize(self, mainThermIdx, bathThermIdx, MainTempOverr, BathTempOverr, TimeOverr):
        self.mainthermSet = mainThermIdx
        self.bathhermSet  = bathThermIdx
        self.mainoverr = MainTempOverr
        self.bathoverr = BathTempOverr
        self.timeoverr = TimeOverr

        self.heartBeatsLeft = 0
        self.heartBeatsRequired = (int(self.timeoverr) * 6) #describe minutes

        self.stateHandlers = {
            HeatingState.state_init:        self.state_handler_init,
            HeatingState.state_idle:        self.state_handler_idle,
            HeatingState.state_active:      self.state_handler_active,
            HeatingState.state_activated:   self.state_handler_activated,
            HeatingState.state_closedown:   self.state_handler_closedown
        }

    def onStart(self):
   #     Domoticz.Log("Print all Parameters:")
   #     for x in Parameters:
   #         if Parameters[x] != "":
   #             Domoticz.Log( "'" + x + "':'" + str(Parameters[x]) + "'")
        
        self.debugging = Parameters["Mode6"]
        
        Domoticz.Heartbeat(10) #Fix heartbeat on 10 seconds...

        if self.debugging == "Verbose+":
            Domoticz.Debugging(2+4+8+16+64)
        if self.debugging == "Verbose":
            Domoticz.Debugging(2+4+8+16+64)
        if self.debugging == "Debug":
            Domoticz.Debugging(2+4+8)
        Domoticz.Log("onStart called")
        
        if (len(Devices) == 0):
            Domoticz.Log("Devices not yet created.. first run or removed")
            Domoticz.Device(Name="Douche Verwarming", Unit=1, TypeName="Switch", Image=15).Create() # Image 15 heating device 
            Devices[1].Update(nValue=0, sValue="") #set to OFF on start
 
        #Initialize controller
        self.initialize(
            Parameters["Mode1"],
            Parameters["Mode2"],
            Parameters["Mode3"],
            Parameters["Mode4"],
            Parameters["Mode5"])

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        
        #just handle the switch (update) and set state accordingly
        if (Command == "Off"):
            Devices[1].Update(nValue=0, sValue="") # switch is not updated from domoticz itself.
            self.state = HeatingState.state_init
        else:
            Devices[1].Update(nValue=1, sValue="") 
            self.state = HeatingState.state_activated

        self.onHeartbeat()

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def storeTemperatures(self):
        ## devicesAPI = DomoticzAPI("type=devices&filter=temp&used=true&order=Name")
        ## if devicesAPI:
        ##     for device in devicesAPI["result"]:  # parse the devices for temperature sensors
        ##         idx = int(device["idx"])
        ##         if idx == self.mainthermGet:
        ##             self.SavedThermostatSetpoints[Thermostats.main_therm] = device["Temp"]
        ##         if idx == self.bathThermGet:
        ##             self.SavedThermostatSetpoints[Thermostats.bath_therm] = device["Temp"]
        ##         if "Temp" in device:
        ##             Domoticz.Debug("device: {}-{} = {}".format(device["idx"], device["Name"], device["Temp"]))
        found = 0
        BathThermSetAPI = DomoticzAPI("type=devices&rid=" + str(self.bathhermSet))
        if BathThermSetAPI:
            for device in BathThermSetAPI["result"]: #should only be one
                self.SavedThermostatSetpoints[Thermostats.bath_therm] = device["SetPoint"]
                found = int(found) + 1

        MainThermSetAPI = DomoticzAPI("type=devices&rid=" + str(self.mainthermSet))
        if MainThermSetAPI:
            for device in MainThermSetAPI["result"]: #should only be one
                self.SavedThermostatSetpoints[Thermostats.main_therm] = device["SetPoint"]
                found = int(found) + 1
        Domoticz.Log("Stored: + " + str(self.SavedThermostatSetpoints))
        if found >= 2:
            return 1
        else:
            return 0

    def setSetpointTemperaturesHigh(self):
        Domoticz.Log("Override -> Stored: + " + str(self.SavedThermostatSetpoints))
        tempRoom = float(self.SavedThermostatSetpoints[Thermostats.bath_therm])
        tempRoom = tempRoom + float(self.bathoverr)
        DomoticzAPI("type=command&param=setsetpoint&idx="+str(self.bathhermSet)+"&setpoint="+str(tempRoom))
        tempRoom = float(self.SavedThermostatSetpoints[Thermostats.main_therm])
        tempRoom = tempRoom + float(self.mainoverr)
        DomoticzAPI("type=command&param=setsetpoint&idx="+str(self.mainthermSet)+"&setpoint="+str(tempRoom))

    def restoreSetpointTemperatures(self):
        Domoticz.Log("Restore -> Stored: + " + str(self.SavedThermostatSetpoints))
        tempRoom = float(self.SavedThermostatSetpoints[Thermostats.bath_therm])
        DomoticzAPI("type=command&param=setsetpoint&idx="+str(self.bathhermSet)+"&setpoint="+str(tempRoom))
        tempRoom = float(self.SavedThermostatSetpoints[Thermostats.main_therm])
        DomoticzAPI("type=command&param=setsetpoint&idx="+str(self.mainthermSet)+"&setpoint="+str(tempRoom))

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat Feature " + str(self.state) + ".")
        self.stateHandlers[self.state]() #Just handle the state

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Plugin utility functions ---------------------------------------------------
def parseCSV(strCSV):

    listvals = []
    for value in strCSV.split(","):
        try:
            val = int(value)
        except:
            pass
        else:
            listvals.append(val)
    return listvals


def DomoticzAPI(APICall):

    resultJson = None
    url = "http://{}:{}/json.htm?{}".format(Parameters["Address"], Parameters["Port"], parse.quote(APICall, safe="&="))
    Domoticz.Debug("Calling domoticz API: {}".format(url))
    try:
        req = request.Request(url)
        if Parameters["Username"] != "":
            Domoticz.Debug("Add authentification for user {}".format(Parameters["Username"]))
            credentials = ('%s:%s' % (Parameters["Username"], Parameters["Password"]))
            encoded_credentials = base64.b64encode(credentials.encode('ascii'))
            req.add_header('Authorization', 'Basic %s' % encoded_credentials.decode("ascii"))

        response = request.urlopen(req)
        if response.status == 200:
            resultJson = json.loads(response.read().decode('utf-8'))
            if resultJson["status"] != "OK":
                Domoticz.Error("Domoticz API returned an error: status = {}".format(resultJson["status"]))
                resultJson = None
        else:
            Domoticz.Error("Domoticz API: http error = {}".format(response.status))
    except:
        Domoticz.Error("Error calling '{}'".format(url))
    return resultJson


def CheckParam(name, value, default):

    try:
        param = int(value)
    except ValueError:
        param = default
        Domoticz.Error("Parameter '{}' has an invalid value of '{}' ! defaut of '{}' is instead used.".format(name, value, default))
    return param

# END OF Plugin utility functions ---------------------------------------------------


    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return