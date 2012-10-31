import unittest2 as unittest
import transaction
from ftw.contenttemplates.testing import CONTENT_TEMPLATES_FUNCTIONAL_TESTING
from plone.app.testing import login, setRoles
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing.z2 import Browser


class TestSetup(unittest.TestCase):

    layer = CONTENT_TEMPLATES_FUNCTIONAL_TESTING

    def setUp(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)
        setRoles(portal, TEST_USER_ID, ['Manager'])
        self.browser = Browser(self.layer['app'])
        self.folder = portal[portal.invokeFactory(id='folder',
                                                  type_name='Folder')]
        # create templates folder
        self.templates = portal[portal.invokeFactory(id='vorlagen',
                                                     type_name='Folder')]
        transaction.commit()

    def _open_url(self, url):
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
                TEST_USER_NAME, TEST_USER_PASSWORD))
        self.browser.open(url)

    def _create_templates(self, templates):
        # create a template / now there should be a template
        for template in templates:
            self.templates.invokeFactory(
                id = template['id'],
                type_name = template['type'],
                title = template['title'])
        transaction.commit()

    def test_action_exists(self):
        self._open_url(self.folder.absolute_url())
        # create_from_template action in add menu
        self.assertIn('create_from_template', self.browser.contents)

    def test_no_templates(self):
        # no templates are defined
        self._open_url("%s/create_from_template" % self.folder.absolute_url())
        self.assertIn('No templates', self.browser.contents)

    def test_cancel_form(self):
        self._create_templates([{'id': 'f1', 'type': 'Folder', 'title': 'Folder1'}])
        self._open_url("%s/create_from_template" % self.folder.absolute_url())
        self.browser.getControl(name='form.cancel').click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/folder')
        self.assertIn('Creation aborted', self.browser.contents)

    def test_nothing_selected(self):
        self._create_templates([{'id': 'f1', 'type': 'Folder', 'title': 'Folder1'}])
        self._open_url("%s/create_from_template" % self.folder.absolute_url())
        self.browser.getControl(name='form.submitted').click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/folder/create_from_template')
        self.assertIn('Please select a template to create a content from it.',
                      self.browser.contents)

    def test_list_templates(self):
        self._create_templates([{'id': 'f1', 'type': 'Folder', 'title': 'Folder1'}])
        self._open_url("%s/create_from_template" % self.folder.absolute_url())
        self.assertIn('Folder1', self.browser.contents)

    def test_templates_order(self):
        self._create_templates([
                {'id': 'f1', 'type': 'Folder', 'title': 'Folder1'},
                {'id': 'f2', 'type': 'Folder', 'title': 'Folder2'}])
        self.templates.moveObjectToPosition('f1', 1)
        transaction.commit()
        self._open_url("%s/create_from_template" % self.folder.absolute_url())
        # Folder1 should be last element
        self.assertIn('Folder1</label>\n              </dt>\n            </dl>',
                      self.browser.contents)

    def test_copy_template(self):
        self._create_templates([{'id': 'f1', 'type': 'Folder', 'title': 'Folder1'}])
        self._open_url("%s/create_from_template" % self.folder.absolute_url())
        # select template f1
        self.browser.getControl(name='template_id').getControl(value='f1').click()
        self.assertTrue(
            self.browser.getControl(name='template_id').getControl(value='f1').selected)
        self.browser.getControl(name='form.submitted').click()
        self.assertEqual(
            self.browser.url,
            '%s/edit' % self.folder.objectValues()[0].absolute_url())

    def test_change_id(self):
        self._create_templates([{'id': 'f1',
                                 'type': 'Folder',
                                 'title': 'Folder1',
                                 'description': 'A simple description.'}])
        self._open_url("%s/create_from_template" % self.folder.absolute_url())
        self.browser.getControl(name='template_id').getControl(value='f1').click()
        self.browser.getControl(name='form.submitted').click()
        # Change the title
        self.browser.getControl(name='title').value = 'MyFolder'
        self.browser.getControl(name='form.button.save').click()
        # The id should be generated from title
        self.assertEqual(self.browser.url, 'http://nohost/plone/folder/myfolder/')
        self.assertEqual(self.folder.myfolder.Description(),
                         self.templates.f1.Description())

    def test_change_id_news(self):
        # the portal type in generated id should contain _ instead of spaces
        self._create_templates([{'id': 'n1', 'type': 'News Item', 'title': 'News1'}])
        self._open_url("%s/create_from_template" % self.folder.absolute_url())
        self.browser.getControl(name='template_id').getControl(value='n1').click()
        self.browser.getControl(name='form.submitted').click()
        # Change the title
        self.browser.getControl(name='title').value = 'MyNews'
        self.browser.getControl(name='form.button.save').click()
        # The id should be generated from title
        self.assertEqual(self.browser.url, 'http://nohost/plone/folder/mynews')
