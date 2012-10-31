from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from ftw.contenttemplates import _
from ftw.contenttemplates.interfaces import IContentTemplatesSettings
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility


class CreateFromTemplate(BrowserView):

    template_form = ViewPageTemplateFile('create_from_template.pt')

    def __call__(self):
        messages = IStatusMessage(self.request)
        # handle cancel
        if self.request.form.get('form.cancel', None):
            messages.addStatusMessage(
                _(u'Creation aborted.'),
                type="info")
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        template_id = self.request.form.get('template_id', None)
        if self.request.form.get('form.submitted', None) and template_id:
            portal = getToolByName(self.context, 'portal_url').getPortalObject()
            templates_folder = portal.restrictedTraverse(self.templatefolder_location())
            cp = templates_folder.manage_copyObjects(template_id)
            new_objs = self.context.manage_pasteObjects(cp)
            new_id = new_objs and new_objs[0]['new_id'] or None
            if new_id:
                new_obj = self.context.restrictedTraverse(new_id, None)
                new_obj.markCreationFlag()
                # generate a new id, so the id will be renamed after edit
                new_obj.setId(new_obj.generateUniqueId(new_obj.portal_type))
                return self.request.RESPONSE.redirect(new_id+'/edit')

        if self.request.form.get('form.submitted', None) and not template_id:
            messages.addStatusMessage(
                _(u'Please select a template to create a content from it.'),
                type="error")
        return self.template_form()

    def templatefolder_location(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IContentTemplatesSettings)
        return settings.template_folder.lstrip('/').encode('utf8')

    @view.memoize_contextless
    def templates(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(
            path = {
                'query': '%s/%s' % (
                    '/'.join(portal.getPhysicalPath()),
                    self.templatefolder_location()),
                'depth': 1},
            portal_type = self.context.immediatelyAddableTypes,
            sort_on="getObjPositionInParent")

    def has_addable_templates(self):
        return len(self.templates())
