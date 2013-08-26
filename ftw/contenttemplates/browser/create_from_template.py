from ftw.contenttemplates import _
from ftw.contenttemplates.interfaces import ICreateFromTemplate
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import queryMultiAdapter
from zope.component import queryUtility


class CreateFromTemplate(BrowserView):

    template_form = ViewPageTemplateFile('create_from_template.pt')

    def __call__(self):

        templatefactory = queryMultiAdapter(
            (self.context, self.request), ICreateFromTemplate)

        if templatefactory is None:
            return 'Creation from template is on root not possible'

        self.templates = templatefactory.templates()

        messages = IStatusMessage(self.request)

        # handle cancel
        if self.request.form.get('form.cancel', None):
            messages.addStatusMessage(
                _(u'Creation aborted.'),
                type="info")
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        template_path = self.request.form.get('template_path', None)
        if self.request.form.get('form.submitted', None) and template_path:

            obj = templatefactory.create(template_path)
            url = '%s/edit' % obj.absolute_url()

            return self.request.RESPONSE.redirect(url)

        if self.request.form.get('form.submitted', None) and not template_path:
            messages.addStatusMessage(
                _(u'Please select a template to create a content from it.'),
                type="error")
        return self.template_form()

    def css_class(self, template):
        """ Returns the objects css class containing the normalized portal
        type for sprite.
        """
        idnormalizer = queryUtility(IIDNormalizer)
        normalize = idnormalizer.normalize

        return "contenttype-%s" % normalize(template.portal_type)

    def has_addable_templates(self):
        """Make traversable"""
        templatefactory = queryMultiAdapter(
            (self.context, self.request), ICreateFromTemplate)

        return templatefactory.has_addable_templates()
