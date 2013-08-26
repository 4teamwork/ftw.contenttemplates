from Acquisition import aq_parent, aq_inner
from ftw.contenttemplates.interfaces import IContentTemplatesSettings
from ftw.contenttemplates.interfaces import ICreateFromTemplate
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces._content import IContentish
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from zope.component import adapts
from zope.component import queryUtility
from zope.interface import implements
from zope.interface import Interface


class TemplateFactory(object):
    """Create content by copy&paste"""

    implements(ICreateFromTemplate)
    adapts(IContentish, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def create(self, template_path):
        portal = getToolByName(self.context,
                               'portal_url').getPortalObject()
        template = portal.restrictedTraverse(
            template_path, None)

        if template is None:
            raise('Template not found')

        templates_folder = aq_parent(aq_inner(template))
        cp = templates_folder.manage_copyObjects(template.getId())
        new_objs = self.context.manage_pasteObjects(cp)
        new_id = new_objs and new_objs[0]['new_id'] or None
        if new_id:
            new_obj = self.context.restrictedTraverse(new_id, None)
            new_obj.markCreationFlag()
            # generate a new id, so the id will be renamed after edit
            new_obj.setId(new_obj.generateUniqueId(new_obj.portal_type))

        return new_obj

    @view.memoize_contextless
    def templates(self):
        if not base_hasattr(self.context, 'getImmediatelyAddableTypes'):
            return []

        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = []
        for templatefolder_location in self.templatefolder_locations():
            brains.extend(catalog(
                    path={
                        'query': '%s/%s' % (
                            '/'.join(portal.getPhysicalPath()),
                            templatefolder_location),
                        'depth': 1},
                    portal_type=self.context.getImmediatelyAddableTypes(),
                    sort_on="getObjPositionInParent"))
        return brains

    def templatefolder_locations(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IContentTemplatesSettings)

        return [path.lstrip('/').encode('utf8')
                for path in settings.template_folder
                if path]

    def has_addable_templates(self):
        return len(self.templates())
