# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from docent.hoa.clubhouse.testing import DOCENT_HOA_CLUBHOUSE_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that docent.hoa.clubhouse is properly installed."""

    layer = DOCENT_HOA_CLUBHOUSE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if docent.hoa.clubhouse is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'docent.hoa.clubhouse'))

    def test_browserlayer(self):
        """Test that IDocentHoaClubhouseLayer is registered."""
        from docent.hoa.clubhouse.interfaces import (
            IDocentHoaClubhouseLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IDocentHoaClubhouseLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = DOCENT_HOA_CLUBHOUSE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['docent.hoa.clubhouse'])

    def test_product_uninstalled(self):
        """Test if docent.hoa.clubhouse is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'docent.hoa.clubhouse'))

    def test_browserlayer_removed(self):
        """Test that IDocentHoaClubhouseLayer is removed."""
        from docent.hoa.clubhouse.interfaces import \
            IDocentHoaClubhouseLayer
        from plone.browserlayer import utils
        self.assertNotIn(
           IDocentHoaClubhouseLayer,
           utils.registered_layers())
