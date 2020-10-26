#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse
#import requests
import urllib.request
import base64
import json


class API:

    PROTOCOL_HTTP = "http"
    PROTOCOL_HTTPS = "https"
    PROTOCOLS = {
        PROTOCOL_HTTP,
        PROTOCOL_HTTPS,
    }

    # type parameter
    TYPE = "type={}"
    TYPE_COMMAND = TYPE.format("command")

    PARAM = "param={}"
    IDX = "idx={}"

    TYPE_COMMAND_PARAM = "{}&{}".format(TYPE_COMMAND, PARAM)

    # Constants used by api
    URL = "json.htm"

    RESULT = "result"
    MESSAGE = "message"
    STATUS = "status"
    TITLE = "title"

    OK = "OK"
    ERROR = "ERR"
    UNKNOWN = "???"
    RESULTS = {
        OK,
        ERROR,
        UNKNOWN,
    }

    def __init__(self, server):
        """ API class to maintain status of the API calls

            Args:
                server (:obj:`Server`): Domoticz server object where to maintain the device            
        """
        self._message = None
        self._querystring = None
        self._payload = None
        self._protocol = server.protocol
        self._server = server
        self._status = self.UNKNOWN
        self._title = None
        self._session = None              # Session Object for Http Session

    def __str__(self):
        """
        The string representation of the API.

        :rtype: str

        """
        return "{}({}): {}-{}".format(self.__class__.__name__, self.endpoint, self._title, self._status)

    def __auth(self):
        if self._server._user is not None and self._server._password is not None:
            return base64.encodestring(("{}:{}".format(
                self._server._user,
                self._server._password)).encode()).decode().replace("\n", "")
        else:
            return ""

    # ..........................................................................
    # Public methods
    # ..........................................................................
    def call(self):
        """Call the Domoticz API"""
        if self._server is not None:
            try:
                if self._session == None:
                    self._session = requests.Session()

                if self._server._rights == self._server.RIGHTS_LOGIN_REQUIRED:
                    # TODO: check if base64 is required
                    self._session.auth = (
                        self._server._user, self._server._password)
                response = self._session.get(self.url,
                                             verify=False)  # bad fix for invalid domoticz certificate
                if response.status_code != 200:
                    raise Exception('call', response.reason)

                strContent = response.content.decode('utf8').replace("'", '"')
                data = json.loads(strContent)
                self._data = data
                self._message = data.get(self.MESSAGE)
                self._payload = data.get(self.RESULT)
                self.status = data.get(self.STATUS)  # set correct value
                self._title = data.get(self.TITLE)
            except Exception as e:
                self._data = {}
                self._message = "Invalid call"
                self._payload = None
                self._status = None
                self._title = None

    def has_payload(self):
        return self._payload is not None

    def is_OK(self):
        return self._status == self.OK

    def is_ERR(self):
        return self._status == self.ERROR

    # ..........................................................................
    # Properties
    # ..........................................................................
    @property
    def data(self):
        """ The complete response from the call """
        return self._data

    @property
    def endpoint(self):
        """ The endpoint to the Domoticz server """
        return ("{}://{}:{}/".format(
            self._protocol,
            self._server._address,
            self._server._port
        )
        )

    @property
    def message(self):
        """ Sometimes a message is returned """
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

    @property
    def payload(self):
        """ The payload (result) part of the response """
        return self._payload

    @property
    def protocol(self):
        """ The protocol used for the call 

        Args:
            `str`: API.PROTOCOL_HTTP or API.PROTOCOL_HTTPS
        """
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        if value in self.PROTOCOLS:
            self._protocol = value

    @property
    def querystring(self):
        """ The querystring used in the call """
        return self._querystring

    @querystring.setter
    def querystring(self, value):
        self._querystring = value

    @property
    def server(self):
        """ The Domoticz server """
        return self._server

    @property
    def status(self):
        """ The status in the response

        Args:
            `str`: API.OK, API.ERROR, or API.UNKNOWN
        """
        return self._status

    @status.setter
    def status(self, value):
        if value is None:
            self._status = self.ERROR
        else:
            # Sometimes ERROR is returned, so truncated to first 3 characters
            value = value[:3]
            if value in self.RESULTS:
                self._status = value
            else:
                # Sometimes the status contains error text!!!
                self._status = self.ERROR

    @property
    def title(self):
        """ Title returned in the response """
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def url(self):
        """ The complete url used to call the Domoticz json/API """
        if self._querystring is None:
            return None
        else:
            return ("{}{}?{}".format(
                self.endpoint,
                self.URL,
                parse.quote(self._querystring, safe="&=")
            ))
