# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
import pytz
from plone import api
from z3c.form import button, field
from zope.interface import Invalid
from plone.dexterity.utils import createContent
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser

from plone import api
from plone.directives import form
from plone.namedfile.field import NamedBlobFile
from zope import schema
from z3c.form import interfaces
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from z3c.form.interfaces import ActionExecutionError

from docent.hoa.clubhouse.utils import getFullname, getHOAAccount, getAddress, getDivision, getLot, getEmail

from plone.formwidget.datetime.z3cform.widget import DateWidget

import logging
logger = logging.getLogger("Plone")

from docent.hoa.clubhouse import _


def getTodaysDate():
    return date.today()


def validateAccept(value):
    if not value == True:
        raise Invalid(u"You must accept the Rental Agreement before you can reserve the Clubhouse.")
    return True


def validateDate(value):
    if value:
        date_string = value.strftime('%m-%d-%Y')
        today = getTodaysDate()
        today_string = today.strftime('%m-%d-%Y')
        if date_string == today_string:
            return True

        if value < today:
            raise Invalid(u"Please select a date in the future.")

        portal = api.portal.get()
        events = api.content.find(context=portal,
                                 portal_type='Event',
                                 )
        for event_brain in events:
            event_obj = event_brain.getObject()
            start_date = event_obj.start
            start_date_string = start_date.strftime('%m-%d-%Y')
            if date_string == start_date_string:
                raise Invalid(u"That date is unavailable.")


        clubhouse_events = api.content.find(context=portal,
                                           portal_type='docent.hoa.clubhouse.clubhouse_event')
        for clubhouse_event_brain in clubhouse_events:
            che_obj = clubhouse_event_brain.getObject()
            start_date = che_obj.start
            start_date_string = start_date.strftime('%m-%d-%Y')
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
    account = schema.ASCIILine(title=_(u"Management Trust Account"),
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
                             description=_(u"Enter your phone number."),
                             required=False,)

    form.mode(email='display')
    email = schema.ASCIILine(title=_(u"Email"),
                             description=_(u""),
                             required=False,)

    form.mode(member_type='display')
    member_type = schema.ASCIILine(title=_(u"I am a Meadows"))

    form.widget('date', DateWidget)
    date = schema.Date(title=_(u"Reservation Date"),
                       description=_(u"All reservations are from 10AM-10PM. Reservations cannot be made on the same day of the event."),
                       required=True,
                       defaultFactory=getTodaysDate,
                       constraint=validateDate,)

    accept_rental_agreement = schema.Bool(title=_(u"Rental Agreement"),
                                          description=_(u"I have read and accept the rental agreement."),
                                          required=True,
                                          constraint=validateAccept)

    initials = schema.TextLine(title=_(u"Initials"),
                               description=_(u"Enter your initials."),
                               required=True,
                               max_length=3)



class RentClubHousesForm(form.SchemaForm):

    label = _(u"Club House Reservation Form")
    schema = IRentClubhousesForm
    ignoreContext = True

    template = ViewPageTemplateFile("templates/rental_form.pt")

    def update(self):
        super(RentClubHousesForm, self).update()
        request = self.request
        form = request.form
        self.thanks = False
        form_action = form.get('form_action') or ''
        if form_action == 'thanks':
            self.thanks = True

        self.rental_date = form.get('rental_date') or ''

        self.updateWidgets()

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

        self.member_fullname = member_fullname
        self.management_trust_account = management_trust_account
        self.member_email = member_email
        self.member_id = member_id
        self.member_type = member_type

        sm = getSecurityManager()
        role = 'Manager'
        tmp_user = BaseUnrestrictedUser(sm.getUser().getId(), '', [role], '')
        portal = api.portal.get()
        tmp_user = tmp_user.__of__(portal.acl_users)
        newSecurityManager(None, tmp_user)

        street_number = ''
        street_address = ''
        division = ''
        lot = ''

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
                    api.portal.show_message(message="%s, We show multiple homes for you. Please contact Meadows "
                                                    "Management." % member_fullname,
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

        self.street_number = street_number
        self.street_address = street_address
        self.address = u'%s %s' % (street_number, street_address)
        self.division = division
        self.lot = lot
        self.div_lot = u"%s_%s" % (division, lot)


    def updateWidgets(self):
        super(RentClubHousesForm, self).updateWidgets()
        self.widgets['phone'].size = 40
        self.widgets['initials'].size = 10


    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, actions):
        api.portal.show_message(message="Club House Rental Request Cancelled.",
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
        context = self.context
        data, errors = self.extractData()
        current_member = api.user.get_current()
        current_member_id = current_member.getId()
        portal = api.portal.get()
        events_obj = portal.get('events')
        date = data.get('date') or None
        if not date:
            api.portal.show_message(message="No date selected. Could not reserve the Club House.",
                                    request=self.request,
                                    type='warn')
            return
        date_string = date.strftime('%m-%d-%Y')
        today = getTodaysDate()
        today_string = today.strftime('%m-%d-%Y')
        if date_string == today_string:
            raise ActionExecutionError(Invalid(_(u"You may not reserve the Clubhouse on the same day as the event.")))
        logger.info("Datestring is %s" % date_string)

        date_dt = datetime.combine(date, datetime.min.time())
        tz = pytz.timezone('America/Los_Angeles')
        date_tz_dt = tz.localize(date_dt)

        fullname = data.get('fullname') or getattr(self, 'member_fullname', 'Unknown Member')
        hoa_account = data.get('account') or getattr(self, 'management_trust_account', 'Unknown Management Trust Account')
        address = data.get('address') or getattr(self, 'address', 'Unknown Address')
        lot = data.get('lot') or getattr(self, 'lot', 'Unknown Lot')
        division = data.get('division') or getattr(self, 'division', 'Unknown Division')
        phone = data.get('phone') or 'Unknown Phone'
        email = data.get('email') or getattr(self, 'member_email', '')
        member_type = data.get('member_type') or getattr(self, 'member_type', 'Unknown Member Type')
        accept_rental_agreement = data.get('accept_rental_agreement')
        initials = data.get('initials') or 'Unknown Initials'

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
                                          title='Private Event')
            events_obj._setObject(event_id, new_event_obj)
            start_date = date_tz_dt + timedelta(hours=10)

            end_date = date_tz_dt + timedelta(hours=22)
            event_obj = events_obj.get(event_id, None)
            setattr(event_obj, 'start', start_date)
            setattr(event_obj, 'end', end_date)
            setattr(event_obj, 'renter_id', current_member_id)
            setattr(event_obj, 'location', 'Clubhouse')
            setattr(event_obj, 'contact_name', fullname)
            setattr(event_obj, 'contact_email', email)
            setattr(event_obj, 'contact_phone', phone)
            event_obj.reindexObject()
            setSecurityManager(sm)
        except Exception as e:
            setSecurityManager(sm)
            logger.warn("CLUBHOUSE RENTAL FORM ERROR: COULD NOT SAVE EVENT: %s" % e)

        #send emails
        email_contacts = getattr(context, 'email_contacts', []) or []

        subject = "The Meadows Clubhouse Rental Request %s" % date_string
        msg = "Ensure you've made your payment\n"
        msg += "Send the signed agreement to porpertymanager@meadowsofredmond.org\n"
        msg += "Agreement: http://themeadowsofredmond.org/amenities/clubhouse-rental-agreement.pdf\n"
        msg += "Payment page: https://www.paydici.com/tmt/pay\n"
        msg += "\n=========================\n\n"
        msg += "Fullname: %s\n" % fullname
        msg += "HOA Account: %s\n" % hoa_account
        msg += "Address: %s\n" % address
        msg += "Div/Lot: %s_%s\n" % (division, lot)
        msg += "Phone: %s\n" % phone
        msg += "Email: %s\n" % email or "Unknown Email"
        msg += "Member Type: %s\n" % member_type
        msg += "Rental Data: %s\n" % date_string
        msg += "Accept Rental Agreement: %s\n" % accept_rental_agreement
        msg += "Initials: %s\n" % initials

        if email:
            email_contacts.append(email)

        for ec in email_contacts:
            try:
                api.portal.send_email(recipient=ec,
                                      subject=subject,
                                      body=msg,
                                      immediate=True)

                api.portal.show_message(message="Club House Reserved. Please complete the important steps below.",
                                        request=self.request,
                                        type='info')

            except Exception as e:
                logger.warn("Could Not Send Clubhouse Registration Emails.")
                api.portal.show_message(message="An error occured, could not send reservation emails. Please confirm your"
                                                "reservation with the property manager.",
                                        request=self.request,
                                        type='warn')

        return self.request.response.redirect('%s?form_action=thanks&rental_date=%s' % (context.absolute_url(),
                                                                                        date_string))




