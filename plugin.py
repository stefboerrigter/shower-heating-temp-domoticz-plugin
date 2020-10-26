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
import DomoticzAPI as dom

class BasePlugin:
    enabled = False
    def __init__(self):
        #self.var = 123
        self.debugging = "Debug"
        self.maintherm = 80
        self.bathherm  = 50
        self.mainoverr = 2
        self.bathoverr = 8
        self.timeoverr = 45
        self.featureActive = 0
        self.heartBeatsSeen = 0
        self.heartBeatsRequired = 0

        return

    def initialize(self, mainThermIdx, bathThermIdx, MainTempOverr, BathTempOverr, TimeOverr):
        self.maintherm = mainThermIdx
        self.bathherm  = bathThermIdx
        self.mainoverr = MainTempOverr
        self.bathoverr = BathTempOverr
        self.timeoverr = TimeOverr

        self.featureActive = 0
        self.heartBeatsSeen = 0
        self.heartBeatsRequired = (int(self.timeoverr) * 6)

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
        #object
 
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
        
        #ToDo, behaviour!
        if (Command == "Off"):
            Devices[1].Update(0, str(0)) # switch is not updated from domoticz itself. 
        else:
            Devices[1].Update(2, str(100)) # switch is not updated from domoticz itself. 
            self.featureActive = int(1)
            self.heartBeatsSeen = int(0)


    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        if (self.featureActive):
            Domoticz.Log("onHeartbeat Feature Active" + str(self.featureActive) + " ==> " + str(self.heartBeatsSeen) + " > "  + str(self.heartBeatsRequired))
            self.heartBeatsSeen = int(self.heartBeatsSeen) + 1
            if(int(self.heartBeatsSeen) >= int(self.heartBeatsRequired)):
                Domoticz.Log("Timeout, we should disable the device!")
                Devices[1].Update(0, str(0)) #Switch off wrapper??
                self.featureActive = 0

        #Domoticz.Log("ShowerController Process called [MainThermIDX: " + str(self.maintherm) + ": BathTherMIDX: " + str(self.bathherm) + "MainOverride: " + str(self.mainoverr) + ": BathOverride: " + str(self.bathoverr) + "TimeOverride: " + str(self.timeoverr)  + "]")


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