#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .utilities import(os_command)
import json


class Translation:

    def __init__(self, server, **kwargs):
        self._translations = {}
        self._server = server
        self._language = kwargs.get(
            "language",
            self._server.setting.get_value("Language"))
        self._getTranslations()

    def __str__(self):
        return "{}({}: \"{}\")".format(self.__class__.__name__, self._server, self._language)

    # ..........................................................................
    # Private methods
    # ..........................................................................
    def _getTranslations(self):
        # /i18n/domoticz-XX.json
        # Get translation for language with code XX, eg. uk, en, fr, nl, ru, etc.
        self._server._api.querystring = None
        if self._server is not None:
            command = "curl"
            command += " -s -X GET \"http://{}:{}/i18n/domoticz-{}.json\"".format(
                self._server._address,
                self._server._port,
                self._language)
            try:
                r = json.loads(os_command(command))
                self._translations = r
                self._server._api._message = None
                self._server._api.status = self._server._api.OK
                self._title = "domoticz-{}".format(self._language)
            except:
                self._server._api._message = "Invalid call"
                self._server._api._status = None
                self._server._api._title = None
            self._server._api._data = {}
            self._server._api._payload = None

    # ..........................................................................
    # Properties
    # ..........................................................................
    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, value):
        if value is None:
            self._language = self._server.language
        else:
            self._language = value
        self._getTranslations()

    def value(self, key):
        return self._translations.get(key, key)
