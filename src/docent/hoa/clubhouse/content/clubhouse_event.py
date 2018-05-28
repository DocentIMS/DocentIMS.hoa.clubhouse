# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity.content import Item, Container
from plone.directives import form
from plone.namedfile.field import NamedBlobFile
from zope import schema


import logging
logger = logging.getLogger("Plone")

from docent.hoa.clubhouse import _


class IClubHouseEvent(form.Schema):
    """
    Uses IDublinCore
    """


class ClubHouseEvent(Item):
    """
    """

    renter_id = schema.ASCIILine(title=_(u"Member User Id"),
                                 required=False)
