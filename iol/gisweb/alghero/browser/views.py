from Products.CMFCore.utils import getToolByName
from plone.dexterity.browser.view import DefaultView
from plone import api

from zope.component import getUtility
from iol.gisweb.alghero.IolApp import IolApp

class protocollaInvia(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        doc = self.aq_parent
        app = self.document.getItem(config.APP_FIELD,config.APP_FIELD_DEFAULT_VALUE)
        iDoc = IolApp(doc)
        return iDoc.protocollaInvia()
