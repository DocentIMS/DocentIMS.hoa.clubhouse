# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

class IDocentHoaClubhouseLayer(Interface):
    """Marker interface that defines a browser layer."""


class IClubhouseEvent(Interface):
    """Explicit marker interface for Event
    """
