from ftw.contenttemplates.interfaces import IFreshOutOfTheFactory
from zExceptions import Redirect
from zope.interface import noLongerProvides
import pkg_resources
import transaction


try:
    pkg_resources.get_distribution('plone.dexterity')
except pkg_resources.DistributionNotFound:
    HAS_DEXTERITY = False
else:
    HAS_DEXTERITY = True
    from plone.dexterity.interfaces import IDexterityContent


def delete_object_on_cancel(event):
    obj = event.object
    is_fresh_out_of_the_factory = IFreshOutOfTheFactory.providedBy(obj)
    if is_fresh_out_of_the_factory:
        parent = obj.aq_parent

        parent.manage_delObjects([obj.getId()])
        transaction.commit()

        if HAS_DEXTERITY and IDexterityContent.providedBy(obj):
            # Hitting the cancel button on a DX edit form will redirect
            # to the object (which no longer exists). We need to redirect
            # to the parent instead.
            raise Redirect(parent.absolute_url())


def remove_marker_interface_on_edit(event):
    obj = event.object
    is_fresh_out_of_the_factory = IFreshOutOfTheFactory.providedBy(obj)
    if is_fresh_out_of_the_factory:
        noLongerProvides(obj, IFreshOutOfTheFactory)
