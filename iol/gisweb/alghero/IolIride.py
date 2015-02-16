# -*- coding: utf-8 -*-
from zope.interface import Interface, implements, Attribute
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from zope.component import getUtility,adapts
from Products.CMFPlomino.interfaces import IPlominoDocument
import config
from .interfaces import IIolApp,IIolIride


class IolIride(object):
    implements(IIolIride)
    adapts(IPlominoDocument)
    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self,obj,params):
        self.document = obj
        self.host = params['host']
        self.user = params['user']
        self.role = params['role']

    security.declarePublic('richiediProtocollo')
    def richiediProtocollo(self):
        app = self.document.getItem(config.APP_FIELD,config.APP_FIELD_DEFAULT_VALUE)
        utils = getUtility(IIolApp,app)
        return utils.richiediProtocollo(self.document)

InitializeClass(IolIride)

