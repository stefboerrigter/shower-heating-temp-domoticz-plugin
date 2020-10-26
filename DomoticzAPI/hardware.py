#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .api import API
from .utilities import (str_2_bool, bool_2_str)
from .const import (HTYPE_DUMMY, HTYPE_PYTHONPLUGIN)


class Hardware:
    """
    The Hardware class represents the Domoticz hardware
    """
    _type_hardware = "hardware"

    _param_add_hardware = "addhardware"
    _param_delete_hardware = "deletehardware"
    _param_update_hardware = "updatehardware"
    _param_get_hardwaretypes = "gethardwaretypes"

    def __init__(self, server, *args, **kwargs):
        """ Hardware
        """
        self._address = None
        self._datatimeout = 0
        self._enabled = True
        self._extra = None
        self._hardwaretype = None
        self._idx = None
        self._mode1 = None
        self._mode2 = None
        self._mode3 = None
        self._mode4 = None
        self._mode5 = None
        self._mode6 = None
        self._name = None
        self._password = None
        self._port = None
        self._server = server
        self._api = self._server.api
        self._serialport = None
        self._type = None
        self._username = None
        if len(args) == 1:
            # For existing hardware
            #   hw = dom.Hardware(server, 180)
            self._idx = args[0]
        else:
            if self._idx is None:
                # For existing hardware
                #   hw = dom.Hardware(server, idx=180)
                idx = kwargs.get("idx")
                self._idx = int(idx) if idx is not None else None
                if self.idx is None:
                    # For new hardware
                    #   hw = dom.Hardware(server, type=15, port=1, name="Sensors1", enabled="true")
                    self._address = kwargs.get("address")
                    self._datatimeout = kwargs.get("datatimeout", 0)
                    self._enabled = str_2_bool(kwargs.get("enabled", "true"))
                    self._extra = kwargs.get("extra")
                    self._mode1 = kwargs.get("mode1")
                    self._mode2 = kwargs.get("mode2")
                    self._mode3 = kwargs.get("mode3")
                    self._mode4 = kwargs.get("mode4")
                    self._mode5 = kwargs.get("mode5")
                    self._mode6 = kwargs.get("mode6")
                    self._name = kwargs.get("name")
                    self._password = kwargs.get("password")
                    self._port = kwargs.get("port")
                    self._serialport = kwargs.get("serialport")
                    self._type = kwargs.get("type")
                    self._username = kwargs.get("username")
        if self._idx is not None:
            self._init()

    def __str__(self):
        return "{}({}, {}: \"{}\", {})".format(self.__class__.__name__, str(self.server), self.idx, self.name,
                                               self.type)

    # ..........................................................................
    # Private methods
    # ..........................................................................
    def _add_param(self, key, value):
        if key is not None and value is not None:
            return "&{}={}".format(key, value)
        else:
            return ""

    def _init(self):
        # /json.htm?type=hardware
        self._api.querystring = "type={}".format(self._type_hardware)
        self._api.call()
        found_dict = {}
        if self._api.payload:
            for found_dict in self._api.payload:
                if found_dict.get("idx") == str(self._idx):
                    break
        self._address = found_dict.get("Address")
        self._datatimeout = found_dict.get("DataTimeout")
        self._enabled = found_dict.get("Enabled", "true") == "true"
        self._extra = found_dict.get("Extra")
        self._mode1 = found_dict.get("Mode1")
        self._mode2 = found_dict.get("Mode2")
        self._mode3 = found_dict.get("Mode3")
        self._mode4 = found_dict.get("Mode4")
        self._mode5 = found_dict.get("Mode5")
        self._mode6 = found_dict.get("Mode6")
        self._name = found_dict.get("Name")
        self._password = found_dict.get("Password")
        self._port = found_dict.get("Port")
        self._serialport = found_dict.get("SerialPort")
        self._type = found_dict.get("Type")
        self._hardwaretype = self._get_type_description(self._type)
        self._username = found_dict.get("Username")

    def _update(self, key, value):
        if value is not None and self.exists():
            # /json.htm?type=command&param=updatehardware&idx=IDX&name=NAME
            param = self._add_param(key, value)
            if key == "enabled":
                param += self._add_param("address", self._address)
                param += self._add_param("datatimeout", self._datatimeout)
                param += self._add_param("extra", self._extra)
                param += self._add_param("htype", self._type)
                param += self._add_param("mode1", self._mode1)
                param += self._add_param("mode2", self._mode2)
                param += self._add_param("mode3", self._mode3)
                param += self._add_param("mode4", self._mode4)
                param += self._add_param("mode5", self._mode5)
                param += self._add_param("mode6", self._mode6)
                param += self._add_param("name", self._name)
                param += self._add_param("password", self._password)
                param += self._add_param("port", self._port)
                param += self._add_param("serialport", self._serialport)
                param += self._add_param("username", self._username)
            querystring = "type=command&param={}&idx={}{}".format(
                self._param_update_hardware,
                self._idx,
                param)
            self._api.querystring = querystring
            self._api.call()
            if key == "htype":
                self._hardwaretype = self._get_type_description(self._type)

    def _get_type_description(self, type):
        # /json.htm?type=command&param=gethardwaretypes
        self._api.querystring = "type=command&param={}".format(
            self._param_get_hardwaretypes)
        self._api.call()
        if self._api.payload:
            for found_dict in self._api.payload:
                if found_dict.get("idx") == type:
                    break
            return found_dict.get("name")
        else:
            return None

    # ..........................................................................
    # Public methods
    # ..........................................................................

    def exists(self):
        return self._idx is not None

    def add(self):
        # At least Name and Type are required
        if self._idx is None and self._name is not None and self._type is not None:
            # Currently only Dummy device is allowed to create
            if self._type == HTYPE_DUMMY:
                querystring = "type=command&param={}".format(
                    self._param_add_hardware)
                querystring += self._add_param("address", self._address)
                querystring += self._add_param("datatimeout",
                                               self._datatimeout)
                querystring += self._add_param("enabled", bool_2_str(self._enabled))
                querystring += self._add_param("extra", self._extra)
                querystring += self._add_param("htype", self._type)
                querystring += self._add_param("mode1", self._mode1)
                querystring += self._add_param("mode2", self._mode2)
                querystring += self._add_param("mode3", self._mode3)
                querystring += self._add_param("mode4", self._mode4)
                querystring += self._add_param("mode5", self._mode5)
                querystring += self._add_param("mode6", self._mode6)
                querystring += self._add_param("name", self._name)
                querystring += self._add_param("password", self._password)
                querystring += self._add_param("port", self._port)
                querystring += self._add_param("serialport", self._serialport)
                querystring += self._add_param("username", self._username)
                self._api.querystring = querystring
                self._api.call()
                
                if self._api.status == self._api.OK:
                    self._idx = int(self._api.data.get("idx"))
                    self._init()

    def add_virtual(self):
        self._type = HTYPE_DUMMY
        self.add()

    def delete(self):
        if self.exists():
            self._api.querystring = "type=command&param={}&idx={}".format(
                self._param_delete_hardware,
                self.idx)
            self._api.call()
            if self._api.status == self._api.OK:
                self._idx = None

    def is_dummy(self):
        return self._type == HTYPE_DUMMY

    def is_python_plugin(self):
        return self._type == HTYPE_PYTHONPLUGIN

    # **************************************************************************
    # Properties
    # **************************************************************************
    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = str(value) if value is not None else None
        self._update("address", self._address)

    @property
    def api(self):
        return self._api

    @property
    def datatimeout(self):
        return int(self._datatimeout)

    @datatimeout.setter
    def datatimeout(self, value):
        self._datatimeout = int(value)
        self._update("datatimeout", self._datatimeout)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    # /json.htm?type=command&param=updatehardware&htype=HTYPE&idx=IDX&name=NAME&username=&password=&address=&port=&serialport=&Mode1=&Mode2=&Mode3=&Mode4=&Mode5=&Mode6=Normal&extra=&enabled=true&datatimeout=0
    def enabled(self, value):
        if isinstance(value, bool):
            self._enabled = value
        else:
            self._enabled = False
        self._update("enabled", bool_2_str(self._enabled))

    @property
    def extra(self):
        return self._extra

    @extra.setter
    def extra(self, value):
        self._extra = str(value) if value is not None else None
        self._update("extra", self._extra)

    @property
    # In /json.htm?type=devices: HardwareID
    def idx(self):
        return self._idx if self._idx is not None else None

    @property
    def mode1(self):
        return self._mode1

    @mode1.setter
    def mode1(self, value):
        self._mode1 = str(value) if value is not None else None
        self._update("mode1", self._mode1)

    @property
    def mode2(self):
        return self._mode2

    @mode2.setter
    def mode2(self, value):
        self._mode2 = str(value) if value is not None else None
        self._update("mode2", self._mode2)

    @property
    def mode3(self):
        return self._mode3

    @mode3.setter
    def mode3(self, value):
        self._mode3 = str(value) if value is not None else None
        self._update("mode3", self._mode3)

    @property
    def mode4(self):
        return self._mode4

    @mode4.setter
    def mode4(self, value):
        self._mode4 = str(value) if value is not None else None
        self._update("mode4", self._mode4)

    @property
    def mode5(self):
        return self._mode5

    @mode5.setter
    def mode5(self, value):
        self._mode5 = str(value) if value is not None else None
        self._update("mode5", self._mode5)

    @property
    def mode6(self):
        return self._mode6

    @mode6.setter
    def mode6(self, value):
        self._mode6 = str(value) if value is not None else None
        self._update("mode6", self._mode6)

    @property
    # In /json.htm?type=devices: HardwareName
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)
        self._update("name", self._name)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = str(value) if value is not None else None
        self._update("password", self._password)

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = int(value) if value is not None else None
        self._update("port", self._port)

    @property
    def serialport(self):
        return self._serialport

    @serialport.setter
    def serialport(self, value):
        self._serialport = str(value) if value is not None else None
        self._update("serialport", self._serialport)

    @property
    def server(self):
        return self._server

    @property
    # In /json.htm?type=devices: HardwareTypeVal
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = int(value) if value is not None else None
        if self._type == HTYPE_DUMMY:
            self._update("htype", self._type)

    @property
    # For some reason, this value is only returned in eg. /json.htm?type=devices in "HardwareType"
    # Now also using /json.htm?type=command&param=gethardwaretypes, see _get_type_description
    def type_name(self):
        return self._hardwaretype

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = str(value) if value is not None else None
        self._update("username", self._username)
