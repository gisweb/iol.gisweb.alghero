from zope.interface import Interface, Attribute


class IIolApp(Interface):
    """
    marker interface for iol document
    """
    iol_app = Attribute("Application Name")


class IIolAppsLayer(Interface):
    """Marker interface for the Browserlayer
    """

class IIolIride(Interface):
    """
    marker interface for iol Iride
    """