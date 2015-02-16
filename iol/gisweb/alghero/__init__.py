# -*- coding: utf-8 -*-
from zope.i18nmessageid import MessageFactory
from AccessControl import allow_module
from zope import component
from .interfaces import IIolApp
from .applications.default import defaultApp
from .applications.scia import sciaApp
from .applications.dehor import dehorApp


allow_module("iol.gisweb.alghero.IolApp")
allow_module("iol.gisweb.alghero.IolIride")
MessageFactory = MessageFactory('iol.gisweb.alghero')

gsm = component.getGlobalSiteManager()

app = defaultApp()
gsm.registerUtility(app, IIolApp, 'default')

app = sciaApp()
gsm.registerUtility(app, IIolApp, 'scia')

app = dehorApp()
gsm.registerUtility(app, IIolApp, 'dehor')