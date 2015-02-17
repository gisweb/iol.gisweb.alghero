# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.dexterity.browser.view import DefaultView
from plone import api

from zope.component import getUtility
from iol.gisweb.alghero.IolIride import IolIride
from random import randint
from DateTime import DateTime

class protocollaInvia(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        doc = self.aq_parent
        prot = str(randint(1,500000)).zfill(8)
        
        wftool = getToolByName(doc, "portal_workflow")
        wftool.doActionFor(doc,'invia_domanda')

	doc.setItem('numero_protocollo',prot)
        doc.setItem('data_protocollo',DateTime())

        wftool.doActionFor(doc,'protocolla')
	
        doc.REQUEST.RESPONSE.redirect("%s" %doc.absolute_url())


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

class testWf(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        doc = self.aq_parent        
        iDoc = IolApp(doc)
        res = iDoc.testWf()
        return res


