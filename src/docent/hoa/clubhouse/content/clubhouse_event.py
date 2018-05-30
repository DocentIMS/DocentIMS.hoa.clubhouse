# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
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

    renter_id = schema.ASCIILine(title=_(u"Member User Id"),
                                 required=False)


class ClubHouseEvent(Item):
    """
    """

    def after_creation_processor(self, event):
        sm = getSecurityManager()
        role = 'Manager'
        tmp_user = BaseUnrestrictedUser(sm.getUser().getId(), '', [role], '')
        portal = api.portal.get()
        tmp_user = tmp_user.__of__(portal.acl_users)
        newSecurityManager(None, tmp_user)
        try:
            api.content.transition(obj=self, transition='publish')
            setSecurityManager(sm)
        except Exception as e:
            setSecurityManager(sm)
            logger.warn("CLUBHOUSE EVENT ERROR: COULD NOT TRANSITION EVENT: %s" % e)
