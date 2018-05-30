# -*- coding: utf-8 -*-
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from docent.hoa.clubhouse import _
from plone.app.event.browser.event_view import EventView
from Products.Five.browser import BrowserView
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IOccurrence
from Products.Five.browser import BrowserView

class ClubHouseEventView(EventView):

    index = ViewPageTemplateFile('templates/clubhouse_event_view.pt')

    def __call__(self):
        if IOccurrence.providedBy(self.context):
            # The transient Occurrence objects cannot be edited. disable the
            # edit border for them.
            self.request.set('disable_border', True)
        self.update()
        return self.index()

    def update(self):

        current_user = api.user.get_current()
        current_user_id = current_user.getId()
        self.current_user = current_user
        self.current_user_id = current_user_id

    def hasEditPermissions(self):
            # who can edit? Managers, Site Administrators, RV Managers
            return api.user.has_permission('Modify portal content', user=self.current_user, obj=self.context)

    def isRenter(self):
        renter_id = getattr(self.context, 'renter_id', '') or ''
        if renter_id == self.current_user_id:
            return True
        return False

    def canView(self):
        return self.hasEditPermissions() or self.isRenter()
