import pkg_resources
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import login
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import TEST_USER_NAME
from zope.configuration import xmlconfig
from ftw.builder.session import BuilderSession
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import set_builder_session_factory

try:
    pkg_resources.get_distribution('plone.app.dexterity')
except pkg_resources.DistributionNotFound:
    HAS_DEXTERITY = False
else:
    HAS_DEXTERITY = True
    from ftw.builder import builder_registry
    from ftw.builder.dexterity import DexterityBuilder
    from plone.dexterity.fti import DexterityFTI


def functional_session_factory():
    sess = BuilderSession()
    sess.auto_commit = True
    return sess


class ContentTemplatesLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        # Load ZCML

        import ftw.contenttemplates
        xmlconfig.file('configure.zcml',
                       ftw.contenttemplates,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        login(portal, TEST_USER_NAME)
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.contenttemplates:default')


if HAS_DEXTERITY:
    class FolderBuilder(DexterityBuilder):
        portal_type = 'Folder'

    class DexterityLayer(PloneSandboxLayer):
        defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

        def setUpZope(self, app, configurationContext):
            # Load ZCML

            import plone.app.dexterity
            self.loadZCML(name='meta.zcml', package=plone.app.dexterity)
            self.loadZCML(package=plone.app.dexterity)

            import ftw.contenttemplates
            xmlconfig.file('configure.zcml',
                           ftw.contenttemplates,
                           context=configurationContext)

        def setUpPloneSite(self, portal):
            self.applyProfile(portal, 'plone.app.dexterity:default')

            # Register two portal_types.
            self._add_folder_type(portal)
            builder_registry.register('Folder', FolderBuilder)

            # Install our profile at the end, because we change the
            # type info of the Folder.
            self.applyProfile(portal, 'ftw.contenttemplates:default')

        def _add_folder_type(self, portal):
            # Register a dexterity folder type.
            fti = DexterityFTI('Folder')
            portal.portal_types._delObject('Folder')
            portal.portal_types._setObject('Folder', fti)
            fti.klass = 'plone.dexterity.content.Container'
            fti.filter_content_types = False
            fti.behaviors = (
                'Products.CMFPlone.interfaces.constrains.'
                'ISelectableConstrainTypes',
                'plone.app.dexterity.behaviors.metadata.IBasic',
                'plone.app.content.interfaces.INameFromTitle')
            return fti


CONTENT_TEMPLATES_TAGS_FIXTURE = ContentTemplatesLayer()
CONTENT_TEMPLATES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(CONTENT_TEMPLATES_TAGS_FIXTURE,),
    name="ftw.contenttemplates:integration")
CONTENT_TEMPLATES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(CONTENT_TEMPLATES_TAGS_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.contenttemplates:functional")

if HAS_DEXTERITY:
    DEXTERITY_TEMPLATES_TAGS_FIXTURE = DexterityLayer()
    DEXTERITY_TEMPLATES_FUNCTIONAL_TESTING = FunctionalTesting(
        bases=(DEXTERITY_TEMPLATES_TAGS_FIXTURE,
               set_builder_session_factory(functional_session_factory)),
        name="ftw.contenttemplates:dexterity")
