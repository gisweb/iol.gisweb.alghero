# -*- coding: utf-8 -*-
import os
import simplejson as json
from zope.interface import Interface, implements, Attribute
from zope.component import adapts
from plone import api
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFPlomino.interfaces import IPlominoDocument, IPlominoForm
from zope.component import getGlobalSiteManager
from iol.gisweb.utils import config
from zope.component import getUtility
from .interfaces import IIolApp


class IolApp(object):
    implements(IIolApp)
    adapts(IPlominoForm,IPlominoDocument)
    tipo_app = u""
    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self,obj):
        self.document = obj
        self.tipo_app = self.document.getItem(config.APP_FIELD,config.APP_FIELD_DEFAULT_VALUE)

    security.declarePublic('NuovoNumeroPratica')
    def NuovoNumeroPratica(self):
        utils = getUtility(IIolApp,self.tipo_app)
        return utils.NuovoNumeroPratica(self.document)

    security.declarePublic('translateListToDiz')
    def translateListToDiz(self):
        return dict(pippo=1)

    #Legge un file json dalla cartella mapping
    def loadJsonData(self,json_file):
        fName = "%s/applications/json/%s.json" %(os.path.dirname(os.path.abspath(__file__)),json_file)

        if os.path.isfile(fName):
            json_data=open(fName)
            try:
                data = json.load(json_data)
            except ValueError, e:
                data = dict()
                json_data.close()
        else:
            return fName
            data = dict()
        return data
InitializeClass(IolApp)