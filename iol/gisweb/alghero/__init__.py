# -*- coding: utf-8 -*-
from zope.i18nmessageid import MessageFactory
from AccessControl import allow_module
from zope import component
from .interfaces import IIolApp
from .applications.default import defaultApp
from applications.scia import sciaApp


allow_module("iol.gisweb.alghero.IolApp")
MessageFactory = MessageFactory('iol.gisweb.alghero')

gsm = component.getGlobalSiteManager()

app = defaultApp()
gsm.registerUtility(app, IIolApp, 'default')

#app = sciaApp()
#gsm.registerUtility(app, IIolApp, 'scia')