#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .server import Server
from .const import (OFF, ON, ONOFF)
from .utilities import (bool_2_int, int_2_bool, str_2_bool, onoff_2_str)


class Scene:

    STYPE_SCENE = 0
    STYPE_GROUP = 1
    STYPES = [
        STYPE_GROUP,
        STYPE_SCENE,
    ]

    _stype_2_num = {
        "Scene": STYPE_SCENE,
        "Group": STYPE_GROUP,
    }

    # /json.htm?type=command&param=getsceneactivations&idx=IDX

    _type_add_scene = "addscene"
    _type_delete_scene = "deletescene"
    _type_scenes = "scenes"
    _type_update_scene = "updatescene"

    _param_make_favorite = "makescenefavorite"
    _param_switch_scene = "switchscene"

    def __init__(self, server, **kwargs):
        """Scene/Group class

        Args:
            server (:obj:`Server`): Domoticz server object where to maintain the scene or group
              idx (:obj:`int`, optional): ID of an existing scene or group
            or 
              name (:obj:`str`, optional): Name of the scene or group
        """
        self._idx = None
        self._name = None
        if isinstance(server, Server) and server.exists():
            self._server = server
            self._idx = kwargs.get("idx")
            if self._idx is None:
                self._name = kwargs.get("name")
            self._api = self._server.api
            self._init()
        else:
            self._server = None

    def __str__(self):
        return "{}(({}) {}: \"{}\" - {})".format(self.__class__.__name__,
                                                 str(self._server),
                                                 self._idx,
                                                 self._name,
                                                 self._type)

    # ..........................................................................
    # Private methods
    # ..........................................................................
    def _add_param(self, key, value):
        if key is not None and value is not None:
            return "&{}={}".format(key, value)
        else:
            return ""

    def _init(self):
        found_dict = {}
        if self._server is not None:
            if self._idx is not None or self._name is not None:
                # Get all scenes: /json.htm?type=scenes&displayhidden=1
                self._api.querystring = "type={}&displayhidden=1".format(
                    self._type_scenes)
                self._api.call()
                if self._api.is_OK():
                    d = self._api.data
                    # For some reason next property is only given in device and scene calls.
                    self._server._acttime = d.get("ActTime")
                    # For some reason next property is only given in this scene call, but is a setting!!!.
                    # self._server._allowwidgetordering = d.get("AllowWidgetOrdering")
                    # Update the server properties.
                    self._server._astrtwilightend = d.get("AstrTwilightEnd")
                    self._server._astrtwilightstart = d.get(
                        "AstrTwilightStart")
                    self._server._civtwilightend = d.get("CivTwilightEnd")
                    self._server._civtwilightstart = d.get("CivTwilightStart")
                    self._server._daylength = d.get("DayLength")
                    self._server._nauttwilightend = d.get("NautTwilightEnd")
                    self._server._nauttwilightstart = d.get(
                        "NautTwilightStart")
                    self._server._servertime = d.get("ServerTime")
                    self._server._sunatsouth = d.get("SunAtSouth")
                    self._server._sunrise = d.get("Sunrise")
                    self._server._sunset = d.get("Sunset")
                    # Search for the given scene
                    if self._api.payload:
                        for result_dict in self._api.payload:
                            if (self._idx is not None and int(result_dict.get("idx")) == self._idx) \
                                    or (self._name is not None and result_dict.get("Name") == self._name):
                                # Found scene :)
                                found_dict = result_dict
                                break
        if found_dict:
            self._description = found_dict.get("Description")
            self._favorite = int_2_bool(found_dict.get("Favorite"))
            self._idx = int(found_dict.get("idx"))
            self._lastupdate = found_dict.get("LastUpdate")
            self._name = found_dict.get("Name")
            self._offaction = found_dict.get("OffAction")
            self._onaction = found_dict.get("OnAction")
            self._protected = found_dict.get("Protected")
            self._status = found_dict.get("Status")
            self._timers = str_2_bool(found_dict.get("Timers"))
            self._type = self._stype_2_num.get(found_dict.get("Type"))
            self._usedbycamera = found_dict.get("UsedByCamera")
        else:
            self._description = None
            self._favorite = False
            self._idx = None
            self._lastupdate = None
            self._offaction = None
            self._onaction = None
            self._protected = False
            self._status = None
            self._timers = False
            self._type = None
            self._usedbycamera = False

    def _update(self, key, value):
        if self.exists() and value is not None:
            # idx, but also for some reason, the scenetype, and name are required
            # /json.htm?type=updatescene&idx=IDX&scenetype=0&name=Name&description=DESC&onaction=&offaction=&protected=false
            if key == "scenetype":
                querystring = "type={}&idx={}&name={}{}".format(
                    self._type_update_scene,
                    self._idx,
                    self._name,
                    self._add_param(key, value))
            elif key == "name":
                querystring = "type={}&idx={}&scenetype={}{}".format(
                    self._type_update_scene,
                    self._idx,
                    self._type,
                    self._add_param(key, value))
            else:
                querystring = "type={}&idx={}&scenetype={}&name={}{}".format(
                    self._type_update_scene,
                    self._idx,
                    self._type,
                    self._name,
                    self._add_param(key, value))
            self._api.querystring = querystring
            self._api.call()
            self._init()

    # ..........................................................................
    # Public methods
    # ..........................................................................
    def add(self):
        '''Add scene/group to Domoticz

        Add least type(SCENE or GROUP) and name are required
        '''
        # /json.htm?type=addscene&name=NAME&scenetype=TYPE
        if not self.exists() and self._name is not None and self._type is not None:
            if self._type in self.STYPES:
                querystring = "type={}&name={}&scenetype={}".format(
                    self._type_add_scene,
                    self._name,
                    self._type)
                self._api.querystring = querystring
                self._api.call()
                if self._api.is_OK():
                    self._init()

    def delete(self):
        '''Delete current scene/group from Domoticz
        '''
        if self.exists():
            querystring = "type={}&idx={}".format(
                self._type_delete_scene,
                self._idx)
            self._api.querystring = querystring
            self._api.call()
            self._idx = None

    def exists(self):
        """Check if scene/group exists in Domoticz """
        return self._idx is not None

    # ..........................................................................
    # Properties
    # ..........................................................................
    @property
    def description(self):
        """Description of the scene/group"""
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        self._update("description", self._description)

    @property
    def favorite(self):
        """(un)set scene/group as favorite in Domoticz"""
        return self._favorite
        
    @favorite.setter
    def favorite(self, value):
        if isinstance(value, bool):
            self._favorite = value
            if self.exists():
                # /json.htm?type=command&param=makescenefavorite&idx=IDX&isfavorite=1
                querystring = "type=command&param={}&idx={}&isfavorite={}".format(
                    self._param_make_favorite,
                    self._idx,
                    bool_2_int(self._favorite))
                self._api.querystring = querystring
                self._api.call()

    @property
    def idx(self):
        """Unique id of the scene/group in Domoticz"""
        return self._idx

    @property
    def lastupdate(self):
        """Datetime scene/group last updated"""
        return self._lastupdate

    @property
    def name(self):
        """Name of the scene/group"""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self._update("name", self._name)

    @property
    def offaction(self):
        """"Action to switch off the scene/group
        
        Should start with http:// or script://
        """
        return self._offaction

    @offaction.setter
    def offaction(self, value):
        self._offaction=value
        self._update("offaction", self._offaction)

    @property
    def onaction(self):
        """"Action to switch on the scene/group
        
        Should start with http:// or script://
        """
        return self._onaction

    @onaction.setter
    def onaction(self, value):
        self._onaction = value
        self._update("onaction", self._onaction)

    @property
    def protected(self):
        """(Un)set scene/group protected
        
        When protected, a password is required
        """
        return self._protected

    @protected.setter
    def protected(self, value):
        if isinstance(value, bool):
            self._protected = value
            self._update("protected", str(self._protected).lower())

    @property
    def server(self):
        """:obj:`Server`: Domoticz server object where to maintain this scene/group"""
        return self._server

    @property
    def status(self):
        """Status of the scene/group
        
        Can be ON or OFF
        """
        return self._status

    @status.setter
    def status(self, value):
        if value in ONOFF:
            # /json.htm?type=command&param=switchscene&idx=5&switchcmd=On&passcode=
            # /json.htm?type=command&param=switchscene&idx=5&switchcmd=Off&passcode=
            self._status = value
            querystring = "type=command&param={}&idx={}&switchcmd={}&passcode=".format(
                self._param_switch_scene,
                self._idx,
                onoff_2_str(self._status)
            )
            self._api.querystring = querystring
            self._api.call()
            self._init()

    @property
    def timers(self):
        return self._timers

    @property
    def type(self):
        """Type of the scene
        
        Can be Scene.STYPE_SCENE or Scene.STYPE_GROUP
        """
        return self._type

    @type.setter
    def type(self, value):
        if value in self.STYPES:
            self._type = value
            self._update("scenetype", self._type)

    @property
    def usedbycamera(self):
        """Used by camera?"""
        return self._usedbycamera

class SceneDevice:

    # /json.htm?type=command&param=getscenedevices&idx=IDX&isscene=true     # &isscene=true seems to be mandatory!!!
    # /json.htm?type=command&param=addscenedevice&idx=IDX&isscene=true&devidx=DEVICEIDX 
    #       &command=ONOFF&level=LEVEL&color=COLOR&ondelay=ONDELAY&offdelay=OFFDELAY
    # /json.htm?type=command&param=deletescenedevice&idx=IDX

    def __init__(self):
        pass
