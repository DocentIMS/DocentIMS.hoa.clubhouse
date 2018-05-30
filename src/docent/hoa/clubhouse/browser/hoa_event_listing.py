# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.event.browser.event_listing import EventListing


class HOAEventListing(EventListing):

    index = ViewPageTemplateFile('templates/hoa_event_listing.pt')


