from Acquisition import aq_parent, aq_inner
from ftw.contenttemplates.interfaces import IContentTemplatesSettings
from ftw.contenttemplates.interfaces import IFreshOutOfTheFactory
from ftw.contenttemplates.interfaces import ICreateFromTemplate
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces._content import IContentish
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from zope.component import adapts
from zope.component import queryUtility
from zope.interface import alsoProvides
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
            if hasattr(new_obj, 'markCreationFlag'):
                # Only Archetypes supports this, not dexterity.
                new_obj.markCreationFlag()
                # generate a new id, so the id will be renamed after edit
                new_obj.setId(new_obj.generateUniqueId(new_obj.portal_type))

            # Apply a marker interface used to identify objects created
            # from a template.
            alsoProvides(new_obj, IFreshOutOfTheFactory)

        return new_obj

    @view.memoize_contextless
    def templates(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        catalog = getToolByName(self.context, 'portal_catalog')
        # Build the query.
        query = {"sort_on": "getObjPositionInParent"}
        constrain = ISelectableConstrainTypes(self.context, None)
        if constrain is not None:
            # search only for addable types
            query['portal_type'] = constrain.getImmediatelyAddableTypes()
        base_path = '/'.join(portal.getPhysicalPath())
        brains = []
        for templatefolder_location in self.templatefolder_locations():
            query['path'] = {
                'query': '%s/%s' % (base_path, templatefolder_location),
                'depth': 1}
            brains.extend(catalog(**query))
        return brains

    def templatefolder_locations(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IContentTemplatesSettings)

        return [path.lstrip('/').encode('utf8')
                for path in settings.template_folder
                if path]

    def has_addable_templates(self):
        return len(self.templates())


class SiteRootTemplateFactory(TemplateFactory):
    """Create content by copy&paste for (Plone) Site root."""

    implements(ICreateFromTemplate)
    adapts(ISiteRoot, Interface)
