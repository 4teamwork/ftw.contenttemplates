from ftw.builder import Builder
from ftw.builder import create
from ftw.contenttemplates.interfaces import IContentTemplatesSettings
from ftw.contenttemplates.interfaces import ICreateFromTemplate
from ftw.contenttemplates.testing import CONTENT_TEMPLATES_FUNCTIONAL_TESTING
from ftw.contenttemplates.testing import HAS_DEXTERITY
from plone.app.testing import login, setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from unittest2 import TestCase
from zope.component import queryMultiAdapter
from zope.component import queryUtility


class TestDefaultTemplateFactory(TestCase):

    layer = CONTENT_TEMPLATES_FUNCTIONAL_TESTING
    folder_type = 'folder'

    def setUp(self):
        super(TestDefaultTemplateFactory, self).setUp()

        self.portal = self.layer['portal']
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.templates = create(Builder(self.folder_type).titled(u'Vorlagen'))
        self.obj = create(Builder(self.folder_type))

    def get_factory(self, obj):
        return queryMultiAdapter((obj, obj.REQUEST), ICreateFromTemplate)

    def test_component_registered(self):
        template_factory = self.get_factory(self.obj)

        self.assertTrue(template_factory,
                        'Default creator is not registered properly')

    def test_registered_on_root(self):
        # Since 1.1.1 the portal can be adapted to a template factory.
        template_factory = self.get_factory(self.portal)
        self.assertIsNotNone(template_factory,
                             'Adapter should be available on portal')

    def test_templates(self):
        create(Builder(self.folder_type).within(self.templates))
        create(Builder(self.folder_type).within(self.templates))
        template_factory = self.get_factory(self.obj)

        self.assertEquals(2,
                          len(template_factory.templates()),
                          'Expect two templates')

    def test_templates_from_multiple_locations(self):
        templates2 = create(Builder(self.folder_type).titled(u'Vorlagen2'))
        template_factory = self.get_factory(self.obj)

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IContentTemplatesSettings)
        settings.template_folder = [u'/vorlagen', u'/vorlagen2']

        template1 = create(Builder(self.folder_type).within(self.templates))
        template2 = create(Builder(self.folder_type).within(templates2))

        self.assertEquals(2,
                          len(template_factory.templates()),
                          'Expect two templates')

        self.assertIn(template1.getId(),
            [item.getId for item in template_factory.templates()])

        self.assertIn(template2.getId(),
            [item.getId for item in template_factory.templates()])

    def test_template_locations(self):
        create(Builder(self.folder_type).titled(u'Vorlagen2'))
        obj = create(Builder(self.folder_type))
        template_factory = self.get_factory(obj)

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IContentTemplatesSettings)
        settings.template_folder = [u'/vorlagen', u'/vorlagen2']

        self.assertEquals([u'vorlagen', u'vorlagen2'],
            template_factory.templatefolder_locations())

    def test_has_addable_templates(self):
        create(Builder(self.folder_type).within(self.templates))
        template_factory = self.get_factory(self.obj)

        self.assertTrue(template_factory.has_addable_templates(),
            'Should be True, because there is a template')

    def test_no_addable_templates(self):
        template_factory = self.get_factory(self.obj)

        self.assertFalse(template_factory.has_addable_templates(),
            'Should be False, because there is no template')

    def test_create(self):
        template = create(Builder(self.folder_type)
            .within(self.templates)
            .titled(u'My template'))

        template_factory = self.get_factory(self.obj)

        template_path = '/'.join(template.getPhysicalPath())
        new_obj = template_factory.create(template_path)

        self.assertIn(new_obj, self.obj.objectValues())

    def test_create_invalid_template_path(self):

        template_factory = self.get_factory(self.obj)

        with self.assertRaises(Exception):
            template_factory.create('/dummy/path')


if HAS_DEXTERITY:
    from ftw.contenttemplates.testing import \
        DEXTERITY_TEMPLATES_FUNCTIONAL_TESTING

    class TestDexterityDefaultTemplateFactory(TestDefaultTemplateFactory):

        layer = DEXTERITY_TEMPLATES_FUNCTIONAL_TESTING
        folder_type = 'Folder'
