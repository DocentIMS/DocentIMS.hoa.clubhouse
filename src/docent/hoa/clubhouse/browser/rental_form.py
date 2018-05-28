# -*- coding: utf-8 -*-
from datetime import datetime
from plone import api
from plone.directives import form
from z3c.form import button, field
from zope.interface import Invalid

from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser

from plone import api
from plone.directives import form
from plone.namedfile.field import NamedBlobFile
from zope import schema
from z3c.form import interfaces
from docent.hoa.clubhouse.utils import getFullname, getHOAAccount, getAddress, getDivision, getLot, getEmail

import logging
logger = logging.getLogger("Plone")

from docent.hoa.clubhouse import _


def validateDate(value):
    if value:
        date_string = value.strftime('%m-%d-%Y')

        portal = api.portal.get()
        events = api.portal.find(context=portal,
                                 portal_type='Event',
                                 )

        for event_brain in events:
            start_date = event_brain.start
            start_date_string = datetime.fromtimestamp(start_date).strfttime('%m-%d-%Y')
            if date_string == start_date_string:
                raise Invalid(u"That date is unavailable.")


        clubhouse_events = api.portal.find(context=portal,
                                           portal_type='docent.hoa.clubhouse.clubhouse_event')
        for clubhouse_event_brain in clubhouse_events:
            start_date = clubhouse_event_brain.start
            start_date_string = datetime.fromtimestamp(start_date).strfttime('%m-%d-%Y')
            if date_string == start_date_string:
                raise Invalid(u"That date is unavailable.")

    return True


class IRentClubhousesForm(form.Schema):
    """

    """
    form.mode(fullname='display')
    fullname = schema.ASCIILine(title=_(u"Name"),
                               description=_(u""),
                               required=False,)

    form.mode(account='display')
    account = schema.ASCIILine(title=_(u"HOA Account"),
                               description=_(u""),
                               required=False,)

    form.mode(address='display')
    address = schema.TextLine(title=_(u"Address"),
                               description=_(u""),
                               required=False,)

    form.mode(division='display')
    division = schema.ASCIILine(title=_(u"Division"),
                               description=_(u""),
                               required=False,)

    form.mode(lot='display')
    lot = schema.ASCIILine(title=_(u"Lot"),
                               description=_(u""),
                               required=False,)

    phone = schema.ASCIILine(title=_(u"Phone"),
                               description=_(u"311-555-2106"),
                               required=False,)

    form.mode(email='display')
    email = schema.ASCIILine(title=_(u"Email"),
                               description=_(u""),
                               required=False,)

    form.mode(member_type='display')
    member_type = schema.ASCIILine(title=_(u"I am a Meadows"))

    date = schema.Date(title=_(u"Reservation Date"),
                       description=_(u"All reservations are from 9AM-10PM"),
                       required=False,
                       constraint=validateDate,)

    accept_rental_agreement = schema.Bool(title=_(u"Rental Agreement"),
                               description=_(u"I have read and accept the rental agreement."),
                               required=False,
                               default=False)

    initials = schema.TextLine(title=_(u"Initials"),
                               description=_(u"Enter your initials."),
                               required=True,
                               max_length=3)



class RentClubHousesForm(form.SchemaForm):

    label = _(u"Online Club House Rental Request")
    schema = IRentClubhousesForm
    ignoreContext = True

    def updateFields(self):
        super(RentClubHousesForm, self).updateFields()
        current_member = api.user.get_current()
        member_fullname = current_member.getProperty('fullname')
        management_trust_account = current_member.getProperty('management_trust_account')
        member_email = current_member.getProperty('email')
        member_id = current_member.getId()
        member_groups = api.group.get_groups(user=current_member)
        owner_group = [True for i in member_groups if i.id == 'home_owners']
        renter_group = [True for i in member_groups if i.id == 'renters']
        member_type = "Unknown"
        if renter_group:
            member_type = "Resident"
        if owner_group:
            member_type = "Owner"

        sm = getSecurityManager()
        role = 'Manager'
        tmp_user = BaseUnrestrictedUser(sm.getUser().getId(), '', [role], '')
        portal = api.portal.get()
        tmp_user = tmp_user.__of__(portal.acl_users)
        newSecurityManager(None, tmp_user)
        try:
            catalog = api.portal.get_tool('portal_catalog')
            query_owner_one = {"portal_type": "hoa_house",}

            home_brains = catalog.searchResults(query_owner_one)
            member_homes = [i for i in home_brains if i.owner_one == member_id
                            or i.owner_two == member_id
                            or i.resident_one == member_id
                            or i.resident_two == member_id]

            if member_homes:
                if len(member_homes) > 1:
                    api.portal.show_message(message="%s, We show multiple homes for you. Please contact Meadows Management.",
                                            request=self.request,
                                            type='warn')
                member_home = member_homes[0]
                street_number = member_home.street_number
                street_address = member_home.street_address
                member_home_id = member_home.id
                division, lot = member_home_id.split('_')
                self.fields['fullname'].field.default = member_fullname
                self.fields['account'].field.default = management_trust_account
                self.fields['address'].field.default = u'%s %s' % (street_number, street_address)
                self.fields['division'].field.default = division
                self.fields['lot'].field.default = lot
                self.fields['email'].field.default = member_email
                self.fields['member_type'].field.default = member_type

            else:
                self.fields['address'].mode = interfaces.INPUT_MODE
                self.fields['division'].mode = interfaces.INPUT_MODE
                self.fields['lot'].mode = interfaces.INPUT_MODE
                self.fields['fullname'].field.default = member_fullname
                self.fields['account'].field.default = management_trust_account
                self.fields['email'].field.default = member_email
                self.fields['member_type'].field.default = member_type

            setSecurityManager(sm)
        except Exception as e:
            setSecurityManager(sm)
            logger.warn("CLUBHOUSE RENTAL FORM ERROR: %s" % e)



    def updateWidgets(self):
        super(RentClubHousesForm, self).updateWidgets()
        self.widgets['phone'].size = 40
        self.widgets['initials'].size = 10


    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, actions):
        api.portal.show_message(message="Online Club House Rental Request Cancelled.",
                                request=self.request,
                                type='info')
        portal = api.portal.get()
        return self.request.response.redirect(portal.absolute_url())

    @button.buttonAndHandler(u"Submit")
    def handleApply(self, actions):
        """

        :param actions:
        :return:
        """
        current_member = api.user.get_current()
        current_member_id = current_member.getId()
        current_member_fullname = current_member.getProperty('fullname')
        portal = api.portal.get()
        events_obj = portal.get('events')
        date = data.get('date') or None
        if not date:
            api.portal.show_message(message="No date selected. Could not reserve the Club House.",
                                    request=self.request,
                                    type='warn')
            return
        date_string = date.stftime('%m-%d-%Y')
        sm = getSecurityManager()
        role = 'Manager'
        tmp_user = BaseUnrestrictedUser(sm.getUser().getId(), '', [role], '')
        portal = api.portal.get()
        tmp_user = tmp_user.__of__(portal.acl_users)
        newSecurityManager(None, tmp_user)
        try:
            event_id = 'club-house-event-%s' % date_string
            new_event_obj = createContent('docent.hoa.clubhouse.clubhouse_event',
                                          id=event_id,
                                          title='Clubhouse Reservation')
            portal._setObject(event_id, new_event_obj)
            start_date = datetime.strptime('%sT10:00:00' % date_string,
                                  '%m-%d-%YT%H:%M:%S')

            end_date = datetime.strptime(('%sT22:00:00' % date_string,
                                  '%m-%d-%YT%H:%M:%S'))
            setattr(new_event_obj, 'start', start_date)
            setattr(new_event_obj, 'end', end_date)
            setattr(new_event_obj, 'renter_id', current_member_id)
            setattr(new_event_obj, 'location', 'Clubhouse')
            setattr(new_event_obj, 'attendees', current_member_fullname)
            new_event_obj.reindexObject()
        except Exception as e:
            setSecurityManager(sm)
            logger.warn("CLUBHOUSE RENTAL FORM ERROR: COULD NOT SAVE EVENT: %s" % e)

        #send emails

        return
