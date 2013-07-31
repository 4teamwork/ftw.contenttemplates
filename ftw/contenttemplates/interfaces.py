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


class ICreateFromTemplate(Interface):
    """Create content from a template"""

    def __init__(context, request):
        """Adapts context and request.
        """

    def templates():
        """Return all possible templates"""

    def has_templates():
        """True if there are templates"""

    def templatefolder_locations():
        """Returns all templates locations (containing templates)"""

    def create(template_path, **kwargs):
        """Create content from a template path"""

