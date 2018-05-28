# -*- coding: utf-8 -*-
from plone import api
from plone.app.textfield import RichText
from plone.dexterity.content import Item, Container
from plone.directives import form
from plone.namedfile.field import NamedBlobFile
from zope import schema


import logging
logger = logging.getLogger("Plone")

from docent.hoa.clubhouse import _

def defaultList():
    return list()


class IClubHouseForm(form.Schema):
    """
    Uses IDublinCore
    """
    email_contacts = schema.List(title=_(u"Email Contacts"),
                                 description=_(u"Email addresses of HOA contacts that should receive a notice when "
                                               u"the form is submitted"),
                                 value_type=schema.ASCIILine(),
                                 required=False,
                                 defaultFactory=defaultList)

    form_preface = RichText(title=u"Preface",
                            description=_(u"Form Helper Text"),
                            required=False)

    form_thankyou = RichText(title=u"Thank You",
                             description=_(u"Form Thank You Text"),
                             required=False)

class ClubHouseForm(Item):
    """
    """
