from ftw.builder import Builder
from ftw.builder import create
from ftw.contenttemplates.interfaces import IContentTemplatesSettings
from ftw.contenttemplates.interfaces import ICreateFromTemplate
from ftw.contenttemplates.testing import CONTENT_TEMPLATES_FUNCTIONAL_TESTING
from plone.app.testing import login, setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from unittest2 import TestCase
from zope.component import queryMultiAdapter
from zope.component import queryUtility


class TestDefaultCreator(TestCase):

    layer = CONTENT_TEMPLATES_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestDefaultCreator, self).setUp()

        self.portal = self.layer['portal']
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.templates = create(Builder('folder').titled('Vorlagen'))
        self.obj = create(Builder('folder'))

    def get_creator(self, obj):
        return queryMultiAdapter((obj, obj.REQUEST), ICreateFromTemplate)

    def test_component_registered(self):
        creator = self.get_creator(self.obj)

        self.assertTrue(creator, 'Default creator is not registered properly')

    def test_not_registered_on_root(self):
        creator = self.get_creator(self.portal)
        self.assertIsNone(creator, 'Adapter should no be available on portal')

    def test_templates(self):
        create(Builder('folder').within(self.templates))
        create(Builder('folder').within(self.templates))
        creator = self.get_creator(self.obj)

        self.assertEquals(2, len(creator.templates()), 'Expect two templates')

    def test_templates_from_multiple_locations(self):
        templates2 = create(Builder('folder').titled('Vorlagen2'))
        creator = self.get_creator(self.obj)

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IContentTemplatesSettings)
        settings.template_folder = [u'/vorlagen', u'/vorlagen2']

        template1 = create(Builder('folder').within(self.templates))
        template2 = create(Builder('folder').within(templates2))

        self.assertEquals(2, len(creator.templates()), 'Expect two templates')

        self.assertIn(template1.getId(),
            [item.getId for item in creator.templates()])

        self.assertIn(template2.getId(),
            [item.getId for item in creator.templates()])

    def test_template_locations(self):
        create(Builder('folder').titled('Vorlagen2'))
        obj = create(Builder('folder'))
        creator = self.get_creator(obj)

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IContentTemplatesSettings)
        settings.template_folder = [u'/vorlagen', u'/vorlagen2']

        self.assertEquals([u'vorlagen', u'vorlagen2'],
            creator.templatefolder_locations())

    def test_has_addable_templates(self):
        create(Builder('folder').within(self.templates))
        creator = self.get_creator(self.obj)

        self.assertTrue(creator.has_addable_templates(),
            'Should be True, because there is a template')

    def test_no_addable_templates(self):
        creator = self.get_creator(self.obj)

        self.assertFalse(creator.has_addable_templates(),
            'Should be False, because there is no template')

    def test_create(self):
        template = create(Builder('folder')
            .within(self.templates)
            .titled('My template'))

        creator = self.get_creator(self.obj)

        template_path = '/'.join(template.getPhysicalPath())
        new_obj = creator.create(template_path)

        self.assertIn(new_obj, self.obj.objectValues())

    def test_create_invalid_template_path(self):

        creator = self.get_creator(self.obj)

        with self.assertRaises(Exception):
            creator.create('/dummy/path')
