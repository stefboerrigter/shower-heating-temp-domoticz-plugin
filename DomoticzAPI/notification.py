#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .server import Server
from .api import API


class Notification:
    """
        Notification
    """

    NSS_ALL = None
    NSS_GOOGLE_CLOUD_MESSAGING = "gcm"
    NSS_HTTP = "http"
    NSS_KODI = "kodi"
    NSS_LOGITECH_MEDIASERVER = "lms"
    NSS_NMA = "nma"
    NSS_PROWL = "prowl"
    NSS_PUSHALOT = "pushalot"
    NSS_PUSHBULLET = "pushbullet"
    NSS_PUSHOVER = "pushover"
    NSS_PUSHSAFER = "pushsafer"
    NSS_TELEGRAM = "telegram"

    _param_notification = "sendnotification"

    _subsystems = {
        NSS_GOOGLE_CLOUD_MESSAGING,
        NSS_HTTP,
        NSS_KODI,
        NSS_LOGITECH_MEDIASERVER,
        NSS_NMA,
        NSS_PROWL,
        NSS_PUSHALOT,
        NSS_PUSHBULLET,
        NSS_PUSHOVER,
        NSS_PUSHSAFER,
        NSS_TELEGRAM,
    }

    def __init__(self, server, subject=None, body=None, subsystem=NSS_ALL):
        if isinstance(server, Server) and server.exists():
            self._server = server
        else:
            self._server = None
        self._subject = subject
        self._body = body
        if subsystem in self._subsystems:
            self._subsystem = subsystem
        else:
            self._subsystem = self.NSS_ALL
        self._api = self._server.api

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, self._subject)

    # ..........................................................................
    # Private methods
    # ..........................................................................

    # ..........................................................................
    # Public methods
    # ..........................................................................

    def send(self):
        # /json.htm?type=command&param=sendnotification&subject=SUBJECT&body=THEBODY
        # /json.htm?type=command&param=sendnotification&subject=SUBJECT&body=THEBODY&subsystem=SUBSYSTEM
        if self._server is not None and self._subject is not None and self._body is not None:
            self._api.querystring = "type=command&param={}&subject={}&body={}".format(
                self._param_notification,
                self._subject,
                self._body
            )
            if self._subsystem is not None:
                self._api.querystring += "&subsystem={}".format(
                    self._subsystem)
            self._api.call()

    # ..........................................................................
    # Properties
    # ..........................................................................
    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        self._body = value

    @property
    def server(self):
        return self._server

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, value):
        self._subject = value

    @property
    def subsystem(self):
        return self._subsystem

    @subsystem.setter
    def subsystem(self, value):
        if value in self._subsystems:
            self._subsystem = value
        else:
            self._subsystem = self.NSS_ALL
