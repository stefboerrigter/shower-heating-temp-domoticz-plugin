#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .const import (NUM_MAX, NUM_MIN)
from ast import literal_eval
import colorsys


class Color:
    # Key
    COLOR_KEY = "color"

    # Parameters
    COLOR_PARAMETER_MODE = "m"
    COLOR_PARAMETER_TEMP = "t"
    COLOR_PARAMETER_R = "r"
    COLOR_PARAMETER_G = "g"
    COLOR_PARAMETER_B = "b"
    COLOR_PARAMETER_COLD_WHITE = "cw"
    COLOR_PARAMETER_WARM_WHITE = "ww"

    # Color Modes
    COLOR_MODE_NONE = 0  # Illegal
    COLOR_MODE_WHITE = 1  # White. Valid fields: none
    COLOR_MODE_TEMP = 2  # White with color temperature. Valid fields: t
    COLOR_MODE_RGB = 3  # Color. Valid fields: r, g, b.
    # Custom (color + white). Valid fields: r, g, b, cw, ww, depending on device capabilities
    COLOR_MODE_CUSTOM = 4
    COLOR_MODES = [
        COLOR_MODE_NONE,
        COLOR_MODE_WHITE,
        COLOR_MODE_TEMP,
        COLOR_MODE_RGB,
        COLOR_MODE_CUSTOM,
    ]

    def __init__(self, **kwargs):
        """Domoticz Color class

            Domoticz color format:

            Example: color={"m":3,"t":0,"r":0,"g":0,"b":50,"cw":0,"ww":0}

                Color {
                    m:  # Above color mode 0 .. 4
                    t:  # Range: 0 .. 255, Color temperature (warm / cold ratio, 0 is coldest, 255 is warmest)
                    r:  # Range: 0 .. 255, Red level
                    g:  # Range: 0 .. 255, Green level
                    b:  # Range: 0 .. 255, Blue level
                    cw: # Range: 0 .. 255, Cold white level
                    ww: # Range: 0 .. 255, Warm white level (also used as level for monochrome white)
                }
        """
        self._m = NUM_MIN
        self._t = NUM_MIN
        self._r = NUM_MIN
        self._g = NUM_MIN
        self._b = NUM_MIN
        self._cw = NUM_MIN
        self._ww = NUM_MIN
        myDict = literal_eval(kwargs.get(self.COLOR_KEY))
        #  myDict = kwargs.get("color")
        if myDict is not None:
            self.m = myDict.get(self.COLOR_PARAMETER_MODE, NUM_MIN)
            self.t = myDict.get(self.COLOR_PARAMETER_TEMP, NUM_MIN)
            self.r = myDict.get(self.COLOR_PARAMETER_R, NUM_MIN)
            self.g = myDict.get(self.COLOR_PARAMETER_G, NUM_MIN)
            self.b = myDict.get(self.COLOR_PARAMETER_B, NUM_MIN)
            self.cw = myDict.get(self.COLOR_PARAMETER_COLD_WHITE, NUM_MIN)
            self.ww = myDict.get(self.COLOR_PARAMETER_WARM_WHITE, NUM_MIN)
        else:
            self.m = kwargs.get(self.COLOR_PARAMETER_MODE, NUM_MIN)
            self.t = kwargs.get(self.COLOR_PARAMETER_TEMP, NUM_MIN)
            self.r = kwargs.get(self.COLOR_PARAMETER_R, NUM_MIN)
            self.g = kwargs.get(self.COLOR_PARAMETER_G, NUM_MIN)
            self.b = kwargs.get(self.COLOR_PARAMETER_B, NUM_MIN)
            self.cw = kwargs.get(self.COLOR_PARAMETER_COLD_WHITE, NUM_MIN)
            self.ww = kwargs.get(self.COLOR_PARAMETER_WARM_WHITE, NUM_MIN)

    def __str__(self):
        return "{}({}: {}, {}: {}, {}: {}, {}: {}, {}: {}, {}: {}, {}: {})".format(
            self.__class__.__name__,
            self.COLOR_PARAMETER_MODE,
            self._m,
            self.COLOR_PARAMETER_TEMP,
            self._t,
            self.COLOR_PARAMETER_R,
            self._r,
            self.COLOR_PARAMETER_G,
            self._g,
            self.COLOR_PARAMETER_B,
            self._b,
            self.COLOR_PARAMETER_COLD_WHITE,
            self._cw,
            self.COLOR_PARAMETER_WARM_WHITE,
            self._ww
        )

    # ..........................................................................
    # Private methods
    # ..........................................................................
    def _minmax(self, v):
        return int(min(max(v, NUM_MIN), NUM_MAX))

    # ..........................................................................
    # Public methods
    # ..........................................................................
    def rgb(self, red, green, blue):
        self.r = red
        self.g = green
        self.b = blue

    # ..........................................................................
    # Properties
    # ..........................................................................
    @property
    def color(self):
        return "{" + "\"{}\":{},\"{}\":{},\"{}\":{},\"{}\":{},\"{}\":{},\"{}\":{},\"{}\":{}".format(
            self.COLOR_PARAMETER_MODE,
            self._m,
            self.COLOR_PARAMETER_TEMP,
            self._t,
            self.COLOR_PARAMETER_R,
            self._r,
            self.COLOR_PARAMETER_G,
            self._g,
            self.COLOR_PARAMETER_B,
            self._b,
            self.COLOR_PARAMETER_COLD_WHITE,
            self._cw,
            self.COLOR_PARAMETER_WARM_WHITE,
            self._ww
        ) + "}"

    @property
    def m(self):
        return self._m

    @m.setter
    def m(self, mode):
        if mode in self.COLOR_MODES:
            self._m = int(mode)
        else:
            self._m = self.COLOR_MODE_NONE
        if self._m == self.COLOR_MODE_NONE or self._m == self.COLOR_MODE_WHITE:
            self._t = NUM_MIN
            self._r = NUM_MIN
            self._g = NUM_MIN
            self._b = NUM_MIN
            self._cw = NUM_MIN
            self._ww = NUM_MIN
        elif self._m == self.COLOR_MODE_TEMP:
            self._r = NUM_MIN
            self._g = NUM_MIN
            self._b = NUM_MIN
            self._cw = NUM_MIN
            self._ww = NUM_MIN
        elif self._m == self.COLOR_MODE_RGB:
            self._t = NUM_MIN
            self._cw = NUM_MIN
            self._ww = NUM_MIN
        else:
            self._t = NUM_MIN

    @property
    def t(self):
        return self._t

    @t.setter
    def t(self, temperature):
        if self._m == self.COLOR_MODE_TEMP:
            self._t = self._minmax(temperature)
        else:
            self._t = NUM_MIN

    @property
    def r(self):
        return self._r

    @r.setter
    def r(self, red):
        if self._m in (self.COLOR_MODE_RGB, self.COLOR_MODE_CUSTOM):
            self._r = self._minmax(red)
        else:
            self._r = NUM_MIN

    @property
    def g(self):
        return self._g

    @g.setter
    def g(self, green):
        if self._m in (self.COLOR_MODE_RGB, self.COLOR_MODE_CUSTOM):
            self._g = self._minmax(green)
        else:
            self._g = NUM_MIN

    @property
    def b(self):
        return self._b

    @b.setter
    def b(self, blue):
        if self._m in (self.COLOR_MODE_RGB, self.COLOR_MODE_CUSTOM):
            self._b = self._minmax(blue)
        else:
            self._b = NUM_MIN

    @property
    def cw(self):
        return self._cw

    @cw.setter
    def cw(self, cold):
        if self._m == self.COLOR_MODE_CUSTOM:
            self._cw = self._minmax(cold)
        else:
            self._cw = NUM_MIN

    @property
    def ww(self):
        return self._ww

    @ww.setter
    def ww(self, warm):
        if self._m == self.COLOR_MODE_CUSTOM:
            self._ww = self._minmax(warm)
        else:
            self._ww = NUM_MIN
