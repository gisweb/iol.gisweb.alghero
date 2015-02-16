# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.dexterity.browser.view import DefaultView
from plone import api

from zope.component import getUtility
from iol.gisweb.alghero.IolIride import IolIride

class protocollaInvia(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        doc = self.aq_parent
        doc.REQUEST.RESPONSE.redirect("%s/EditDocument" %doc.absolute_url())


class protocollaInvia1(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        doc = self.aq_parent
        prms = dict(host="",user="",role="")
        iDoc = IolIride(doc,prms)
        res = iDoc.richiediProtocollo()
        return res

