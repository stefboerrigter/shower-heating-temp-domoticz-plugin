#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .server import Server
from .api import API
from datetime import datetime


class UserVariable:

    UVE_TYPE_INTEGER = 0
    UVE_TYPE_FLOAT = 1
    UVE_TYPE_STRING = 2
    UVE_TYPE_DATE = 3
    UVE_TYPE_TIME = 4
    UVE_TYPES = [
        UVE_TYPE_INTEGER,
        UVE_TYPE_FLOAT,
        UVE_TYPE_STRING,
        UVE_TYPE_DATE,
        UVE_TYPE_TIME,
    ]

    _param_add_user_variable = "adduservariable"
    _param_delete_user_variable = "deleteuservariable"
    _param_get_user_variable = "getuservariable"
    _param_get_user_variables = "getuservariables"
    _param_update_user_variable = "updateuservariable"

    _date = "%d/%m/%Y"
    _time = "%H:%M"

    def __init__(self, server, name, type=UVE_TYPE_STRING, value=None):
        """Args:
                server (:obj:`Server`): Domoticz server object where to maintain the user variable
                name (:obj:`str`): Name of the user variable
                type (:obj:`int`, optional): Type of the user variable (default = UVE_TYPE_STRING)
                    UVE_TYPE_INTEGER    = Integer, e.g. -1, 1, 0, 2, 10
                    UVE_TYPE_FLOAT      = Float, e.g. -1.1, 1.2, 3.1
                    UVE_TYPE_STRING     = String
                    UVE_TYPE_DATE       = Date in format DD/MM/YYYY
                    UVE_TYPE_TIME       = Time in 24 hr format HH:MM
                value (:obj:`str`, optional): Value of the user variable (default = None)
        """
        if isinstance(server, Server) and server.exists():
            self._server = server
        else:
            self._server = None
        self._idx = None
        if server is not None and len(name) > 0:
            self._api = self._server.api
            self._lastupdate = None
            self._name = name
            self._server = server
            if type in self.UVE_TYPES:
                self._type = type
            else:
                self._type = None
            # Function will handle None values
            self._value = self.__value(self._type, value)
            self.__init()

    def __str__(self):
        return "{}({}, {}: \"{}\", {}, \"{}\")".format(
            self.__class__.__name__,
            str(self._server),
            self._idx,
            self._name,
            self._type,
            self._value)

    # ..........................................................................
    # Private methods
    # ..........................................................................
    def __init(self):
        if self._idx is not None:
            # /json.htm?type=command&param=getuservariable&idx=IDX
            self._api.querystring = "type=command&param={}&idx={}".format(
                self._param_get_user_variable,
                self._idx
            )
        else:
            # /json.htm?type=command&param=getuservariables
            self._api.querystring = "type=command&param={}".format(
                self._param_get_user_variables)
        self._api.call()
        if self._api.is_OK() and self._api.has_payload():
            for var in self._api.payload:
                if (self._idx is not None and int(var.get("idx")) == self._idx) or (self._name is not None and var.get("Name") == self._name):
                    self._idx = int(var.get("idx"))
                    self._value = var.get("Value")
                    self._type = int(var.get("Type"))
                    self._lastupdate = var.get("LastUpdate")
                    break

    def __update(self):
        # /json.htm?type=command&param=updateuservariable&idx=IDX&vname=NAME&vtype=TYPE&vvalue=VALUE
        if self.exists():
            self._api.querystring = "type=command&param={}&idx={}&vname={}&vtype={}&vvalue={}".format(
                self._param_update_user_variable,
                self._idx,
                self._name,
                self._type,
                self._value
            )
            self._api.call()
            self.__init()

    def __value(self, type, value):
        if value is None:
            result = value
        elif type == self.UVE_TYPE_INTEGER:
            result = str(int(float(value)))
        elif type == self.UVE_TYPE_FLOAT:
            result = str(float(value))
        elif type == self.UVE_TYPE_DATE:
            try:
                dt = datetime.strptime(value, self._date)
            except:
                dt = None
            if dt is not None:
                result = dt.strftime(self._date)
            else:
                result = None
        elif type == self.UVE_TYPE_TIME:
            try:
                dt = datetime.strptime(value, self._time)
            except:
                dt = None
            if dt is not None:
                result = dt.strftime(self._time)
            else:
                result = None
        elif type == self.UVE_TYPE_STRING:
            result = value
        else:
            result = None
        return result

    # ..........................................................................
    # Public methods
    # ..........................................................................
    def add(self):
        """Add uservariable to Domoticz."""
        # /json.htm?type=command&param=adduservariable&vname=NAME&vtype=TYPE&vvalue=VALUE
        if not self.exists():
            if len(self._name) > 0 and self._type in self.UVE_TYPES and len(self._value) > 0:
                self._api.querystring = "type=command&param={}&vname={}&vtype={}&vvalue={}".format(
                    self._param_add_user_variable,
                    self._name,
                    self._type,
                    self._value
                )
                self._api.call()
                if self._api.status == self._api.OK:
                    # If an uservariable with the same name is added, the status will be "Variable name already exists!"!
                    self.__init()

    def delete(self):
        """Delete uservariable from Domoticz."""
        # /json.htm?type=command&param=deleteuservariable&idx=IDX
        if self.exists():
            self._api.querystring = "type=command&param={}&idx={}".format(
                self._param_delete_user_variable,
                self._idx)
            self._api.call()
            if self._api.status == self._api.OK:
                self._idx = None

    def exists(self):
        """Checks if uservariable exists in Domoticz.

            Returns:
                True if uservariable exists in Domoticz, False otherwise.
        """
        return self._idx is not None

    # ..........................................................................
    # Properties
    # ..........................................................................
    @property
    def api(self):
        """:obj:`API`: API object."""
        return self._api

    @property
    def idx(self):
        """int: Unique id for this uservariable."""
        return self._idx

    @property
    def lastupdate(self):
        """:obj:`datetime`: Date and time of the last update."""
        return datetime.strptime(self._lastupdate, "%Y-%m-%d %H:%M:%S")

    @property
    def name(self):
        """str: Name of the uservariable."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.__update()

    @property
    def server(self):
        """:obj:`Server`: Domoticz server object where to maintain the user variable"""
        return self._server

    @property
    def type(self):
        """int: Uservariable type, eg. UVE_TYPE_INTEGER."""
        return self._type

    @type.setter
    def type(self, value):
        if value in self.UVE_TYPES:
            self._type = value
            self.__update()

    @property
    def value(self):
        """str: Value for uservariable."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = self.__value(self._type, value)
        self.__update()
