#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .api import API
from .utilities import (base64_encode, bool_2_str, int_2_bool, str_2_bool)
import base64
import hashlib

class User:

    USER_RIGHTS_VIEWER = 0
    USER_RIGHTS_USER = 1
    USER_RIGHTS_ADMIN = 2
    USER_RIGHTS = {USER_RIGHTS_VIEWER,
                   USER_RIGHTS_USER,
                   USER_RIGHTS_ADMIN,
                   }

    USER_TAB_NONE = 0
    USER_TAB_SWITCHES = 1 << 0
    USER_TAB_SCENES = 1 << 1
    USER_TAB_TEMPERATURE = 1 << 2
    USER_TAB_WEATHER = 1 << 3
    USER_TAB_UTILITY = 1 << 4
    USER_TAB_CUSTOM = 1 << 5
    USER_TAB_FLOORPLAN = 1 << 6
    USER_TAB_ALL = USER_TAB_SWITCHES | USER_TAB_SCENES | USER_TAB_TEMPERATURE | USER_TAB_WEATHER | USER_TAB_UTILITY | USER_TAB_CUSTOM | USER_TAB_FLOORPLAN
    USER_TABS = {
        USER_TAB_SWITCHES,
        USER_TAB_SCENES,
        USER_TAB_TEMPERATURE,
        USER_TAB_WEATHER,
        USER_TAB_UTILITY,
        USER_TAB_CUSTOM,
        USER_TAB_FLOORPLAN,
    }

    _type_users = "users"

    _param_add_user = "adduser"
    _param_delete_user = "deleteuser"
    _param_update_user = "updateuser"
    # /json.htm?type=setshareduserdevices&idx=1&devices=82;81;1
    # /json.htm?type=getshareduserdevices&idx=1

    def __init__(self, server, *args, **kwargs):
        """User class

        Args:
            server (:obj:`Server`): Domoticz server
            *args:
                (int): idx from existing user
            **kwargs: Keyword arguments:
                enabled (bool): enabled
                idx (int): idx of an existing user
                name (:obj:`str`): name of the user
                password (:obj:`str`): password of the user
                remotesharing (bool): remotesharing
                rights (int): user rights
                tabsenabled (int): tabs enabled for the user
        """
        if server.exists():
            self._enabled = True
            self._idx = None
            self._password = None
            self._remotesharing = False
            self._rights = self.USER_RIGHTS_VIEWER
            self._server = server
            self._api = server.api
            self._tabsenabled = self.USER_TAB_NONE
            self._username = None
            if len(args) == 1:
                # For existing user
                #   user = dom.User(server, 3)
                self._idx = args[0]
            else:
                self._idx = kwargs.get("idx")
                if self._idx is None:
                    self._enabled = kwargs.get("enabled",
                                               True)
                    self._password = self._md5hash(kwargs.get("password"))
                    self._remotesharing = kwargs.get("remotesharing",
                                                     False)
                    self._rights = kwargs.get(
                        "rights", self.USER_RIGHTS_VIEWER)
                    self._tabsenabled = kwargs.get(
                        "tabsenabled", self.USER_TAB_NONE)
                    self._username = kwargs.get("name")
            self._init()

    def __str__(self):
        return "{}({}, {}: \"{}\")".format(self.__class__.__name__,
                                           str(self._server),
                                           self._idx,
                                           self._username)

    # ..........................................................................
    # Private methods
    # ..........................................................................
    def _add_param(self, key, value):
        if key is not None and value is not None:
            if isinstance(value, bool):
                return "&{}={}".format(key, bool_2_str(value))
            else:
                return "&{}={}".format(key, value)
        else:
            return ""

    def _init(self):
        if self._server.exists():
            # /json.htm?type=users
            self._api.querystring = "type={}".format(
                self._type_users)
            self._api.call()
            if self._api.payload:
                myDict = {}
                temp_idx = None
                for dict in self._api.payload:
                    if self._idx is not None and int(dict.get("idx")) == self._idx:
                        myDict = dict
                        break
                    if self._idx is None and dict.get("Username") == self._username:
                        if temp_idx is None or temp_idx < int(dict.get("idx")):
                            self._idx = int(dict.get("idx"))
                            temp_idx = self._idx
                            myDict = dict
                if self._idx is not None:
                    self._enabled = str_2_bool(myDict.get("Enabled"))
                    self._password = myDict.get("Password")
                    self._remotesharing = int_2_bool(
                        myDict.get("RemoteSharing"))
                    self._rights = myDict.get("Rights")
                    self._tabsenabled = myDict.get("TabsEnabled")
                    self._username = myDict.get("Username")

    def _update(self):
        """Update user data in Domoticz
        """
        if self.exists():
            # /json.htm?type=command&param=updateuser&idx=IDX&enabled=ENABLED&username=NAME&password=PASSWORD&rights=RIGHTS&RemoteSharing=REMOTESHARING&TabsEnabled=TABS
            self._api.querystring = "type=command&param={}&enabled={}&username={}&password={}&rights={}&RemoteSharing={}TabsEnabled={}".format(
                self._param_update_user,
                bool_2_str(self._enabled),
                self._username,
                self._password,
                self._rights,
                bool_2_str(self._remotesharing),
                self._tabsenabled
            )
            self._api.call()

    @staticmethod
    def _md5hash(value):
        if value is None:
            return value
        else:
            return hashlib.md5(value.encode()).hexdigest()

    # ..........................................................................
    # Public methods
    # ..........................................................................
    def add(self):
        """Add user to Domoticz
        """
        # test/test admin
        # /json.htm?type=command&param=adduser&enabled=true&username=test&password=098f6bcd4621d373cade4e832627b4f6&rights=2&RemoteSharing=false&TabsEnabled=0
        if not self.exists() and self._username is not None and self._password is not None:
            self._api.querystring = "type=command&param={}&username={}".format(
                self._param_add_user,
                self._username
            )
            self._api.querystring += self._add_param(
                "enabled", self._enabled)
            self._api.querystring += self._add_param(
                "password", self._password)
            self._api.querystring += self._add_param(
                "rights", self._rights)
            self._api.querystring += self._add_param(
                "RemoteSharing", self._remotesharing)
            self._api.querystring += self._add_param(
                "TabsEnabled", self._tabsenabled)
            self._api.call()
            if self._api.is_OK():
                self._init()

    def add_tab(self, tab):
        """Add tab for user

        Args:
            tab (`int`): tab
        """
        if tab in self.USER_TABS:
            self._tabsenabled |= tab

    def delete(self):
        """Delete the user from Domoticz
        """
        if self.exists():
            # /json.htm?type=command&param=deleteuser&idx=1
            self._api.querystring = "type=command&param={}&idx={}".format(
                self._param_delete_user,
                self._idx
            )
            self._api.call()
            if self._api.is_OK():
                self._idx = None

    def exists(self):
        """Checks if user exists

        Returns:
            True if user exists in Domoticz, otherwise False
        """
        return self._idx is not None

    def has_tab(self, tab):
        """Check if tab is available for user

        Args:
            tab (`int`): tab

        Returns:
            True if tab is available for user, otherwise False
        """
        if tab in self.USER_TABS:
            return (self._tabsenabled & tab) > self.USER_TAB_NONE

    def remove_tab(self, tab):
        """Add tab for user

        Args:
            tab (`int`): tab
        """
        if tab in self.USER_TABS:
            self._tabsenabled &= ~tab

    # ..........................................................................
    # Properties
    # ..........................................................................
    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if isinstance(value, bool):
            self._enabled = value
        else:
            self._enabled = True
        self._update()

    @property
    def idx(self):
        return self._idx

    @property
    def name(self):
        return self._username

    @name.setter
    def name(self, value):
        self._username = value
        self._update()

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = self._md5hash(value)
        self._update()

    @property
    def remotesharing(self):
        return self._remotesharing

    @remotesharing.setter
    def remotesharing(self, value):
        if isinstance(value, bool):
            self._remotesharing = value
        else:
            self._remotesharing = False
        self._update()

    @property
    def rights(self):
        return self._rights

    @rights.setter
    def rights(self, value):
        if value in self.USER_RIGHTS:
            self._rights = value
            self._update()

    @property
    def tabsenabled(self):
        return self._tabsenabled

    @tabsenabled.setter
    def tabsenabled(self, value):
        self._tabsenabled = value
        self._update()
