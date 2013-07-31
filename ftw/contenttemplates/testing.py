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


CONTENT_TEMPLATES_TAGS_FIXTURE = ContentTemplatesLayer()
CONTENT_TEMPLATES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(CONTENT_TEMPLATES_TAGS_FIXTURE,),
    name="ftw.contenttemplates:integration")
CONTENT_TEMPLATES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(CONTENT_TEMPLATES_TAGS_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.contenttemplates:functional")
