#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .api import API
from .setting import Setting


class Security:

    SECURITY_STATUS_DISARMED = 0
    SECURITY_STATUS_ARMED_HOME = 1
    SECURITY_STATUS_ARMED_AWAY = 2
    SECURITY_STATUS_ARMED_UNKNOWN = 3
    SECURITY_STATUSSES = [
        SECURITY_STATUS_DISARMED,
        SECURITY_STATUS_ARMED_HOME,
        SECURITY_STATUS_ARMED_AWAY,
    ]

    _param_getsecstatus = "getsecstatus"
    _param_setsecstatus = "setsecstatus"

    def __init__(self, server):
        """
            Args:
                server (:obj:`Server`): Domoticz server object where to maintain the device            
        """
        self._server = server
        self._api = self._server.api
        self._password = self._server.setting.value("SecPassword")
        self._status = self.SECURITY_STATUS_ARMED_UNKNOWN
        self._secondelay = 0

    # ..........................................................................
    # Private methods
    # ..........................................................................
    def _get_status(self):
        # /json.htm?type=command&param=getsecstatus
        self._api.querystring = "type=command&param={}".format(
            self._param_getsecstatus)
        self._api.call()
        if self._api.status == self._api.OK:
            self._secondelay = self._api.data.get("secondelay")
            self._status = self._api.data.get("secstatus")

    @property
    def password(self):
        return self._server.setting.value("SecPassword")

    @property
    def secondelay(self):
        self._get_status()
        return self._secondelay

    @property
    def status(self):
        self._get_status()
        return self._status

    @status.setter
    def status(self, value):
        if value in self.SECURITY_STATUSSES:
            # /json.htm?type=command&param=setsecstatus&seccode=PASSWORD&secstatus=STATUS
            self._api.querystring = "type=command&param={}&seccode={}&secstatus={}".format(
                self._param_setsecstatus,
                self._password,
                value
            )
        self._api.call()
        if self._api.status == self._api.OK:
            self._get_status()
            self._secondelay = self._api.data.get("secondelay")
            self._status = self._api.data.get("secstatus")
