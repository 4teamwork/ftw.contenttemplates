from ftw.contenttemplates import _
from zope import schema
from zope.interface import Interface


class IContentTemplatesSettings(Interface):
    """Interface for registry entries.
    """
    template_folder = schema.List(
        title=_(u'label_templates_location', default=u'Templates location'),
        description=_(u'help_templates_location',
            default=u'Defines the path where the templates are.'),
        value_type=schema.TextLine(required=True),
        default=[u'/vorlagen'],
        required=True,
    )
