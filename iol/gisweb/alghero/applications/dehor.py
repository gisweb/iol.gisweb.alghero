# -*- coding: utf-8 -*-
from zope.interface import implements
from iol.gisweb.alghero.interfaces import IIolApp
from iol.gisweb.alghero.IolApp import IolApp
from zope import component
from AccessControl import ClassSecurityInfo
from plone import api

from gisweb.iol.permissions import IOL_READ_PERMISSION, IOL_EDIT_PERMISSION, IOL_REMOVE_PERMISSION

from iol.gisweb.utils.config import USER_CREDITABLE_FIELD,USER_UNIQUE_FIELD,IOL_APPS_FIELD,STATUS_FIELD,IOL_NUM_FIELD
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime



class dehorApp(object):
    implements(IIolApp)
    security = ClassSecurityInfo()
    def __init__(self):
        pass
    def __call__(self, *args, **kwargs):
        pass
    #Ritorna in nuovo numero di pratica definito come sequenziale
    security.declarePublic('NuovoNumeroPratica')
    def NuovoNumeroPratica(self,obj):
        idx = obj.getParentDatabase().getIndex()
        query = dict(IOL_NUM_FIELD = dict(query=0, range='min'))

        brains = idx.dbsearch(query, sortindex=IOL_NUM_FIELD, reverse=1, only_allowed=False)
        if not brains:
            nuovoNumero = 1
        else:
            nuovoNumero = (brains[0].getObject().getItem(IOL_NUM_FIELD,0) or 0) +1

        return nuovoNumero


    #Ritorna il nuovo munero di protocollo preso da iride
    security.declarePublic('richiediProtocollo')
    def richiediProtocollo(self,obj):
        doc = obj
        iDoc = IolApp(doc)
        jsonData = iDoc.loadJsonData('dehor.richiediProtocollo')
        res = dict()
        for k,v in jsonData.items():
            res[k] = irideConvert(doc)(v)
        return res

class irideConvert(object):
    def __init__(self,obj):
        self.document = obj
    def __call__(self, v):
        if not (isinstance(v,dict) and "type" in v.keys()):
            return "undefined"
        else:
            t = v["type"]
            if t == "const":
                return self.const(self,v)
            elif t == "item":
                return self.item(self,v)
            elif t == "function":
                pass

    def const(self,v):
        if 'value' in v.keys():
            return v['value']
        else:
            return 'error - 1'

    def item(self,v):
        if 'value' in v.keys():
            return self.document.getItem(v['value'],'')
        else:
            return 'error - 2'

    def dateToString(self,v):
        if isinstance(v,DateTime):
            return v.strftime("%d/%m/%Y")
        else:
            return 'error - 4'

    def function(self,v):
        if 'value' in v.keys() and 'name' in v.keys():
            val = self.document.getItem(v['value'],'')
            if hasattr(self.__class__, key) and callable(getattr(self.__class__, key)):
                return self[key](val)
            else:
                return 'error - 3'
        else:
            return 'error - 2'
