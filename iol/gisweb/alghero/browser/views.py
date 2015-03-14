# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.dexterity.browser.view import DefaultView
from plone import api
from iol.gisweb.alghero.IolApp import IolApp
from zope.component import getUtility
from iol.gisweb.alghero.IolIride import IolIride, IrideProtocollo
from random import randint
from DateTime import DateTime
import simplejson as json
from base64 import b64encode

class protocollaInvia(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        doc = self.aq_parent
        state = api.content.transition(doc,'protocolla')
        state = api.content.transition(doc,'invia_domanda')
        prot = doc.getItem('numero_protocollo','')
        if prot:
            api.portal.show_message(message=u"La richiesta è stata inviata correttamente.E' stata acquisita agli atti con protocollo n. %s" %prot,request=self.request,type='message')
        else:
            api.portal.show_message(message=u"La richiesta è stata inviata.Sono occorsi errori durante la protocollazione del documento" %prot,request=self.request,type='error')

        self.request.RESPONSE.redirect(doc.absolute_url())
        return

class testWf(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        doc = self.aq_parent        
        iDoc = IolApp(doc)
        res = iDoc.testWf()
        return res

class searchCodFis(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, codfis='IT02101040547'):
        ws = IrideProtocollo(service='wsprotocollodm.asmx?WSDL')
        res = ws.RicercaPerCodiceFiscale(CodiceFiscale=codfis,SoloProtocollo=True)
        self.request.RESPONSE.headers['Content-Type'] = 'application/json'
        return json.dumps(res, default=DateTime.ISO)

class findDoc(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, id):
        ws = IrideProtocollo(service='wsprotocollodm.asmx?WSDL')
        res = ws.LeggiDocumento(IdDocumento=id)
        self.request.RESPONSE.headers['Content-Type'] = 'application/json'
        return json.dumps(res,default=DateTime.ISO)
        #return res['result']
class gruppiPareri(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def __call__(self):
        doc = self.aq_parent        
        iDoc = IolApp(doc)
        res = iDoc.gruppiPareri()
        return res    




