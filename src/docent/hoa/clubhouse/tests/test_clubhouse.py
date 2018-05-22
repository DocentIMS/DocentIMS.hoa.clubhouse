# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from docent.hoa.clubhouse.interfaces import IClubhouse
from docent.hoa.clubhouse.testing import DOCENT_HOA_CLUBHOUSE_INTEGRATION_TESTING  # noqa
from zope.component import createObject
from zope.component import queryUtility

import unittest


class ClubhouseIntegrationTest(unittest.TestCase):

    layer = DOCENT_HOA_CLUBHOUSE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='Clubhouse')
        schema = fti.lookupSchema()
        self.assertEqual(IClubhouse, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='Clubhouse')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='Clubhouse')
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(IClubhouse.providedBy(obj))

    def test_adding(self):
        obj = api.content.create(
            container=self.portal,
            type='Clubhouse',
            id='Clubhouse',
        )
        self.assertTrue(IClubhouse.providedBy(obj))
