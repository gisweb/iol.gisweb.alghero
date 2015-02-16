# -*- coding: utf-8 -*-
from zope.interface import Interface, implements, Attribute
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.CMFPlomino.interfaces import IPlominoDocument
from .interfaces import IIolIride


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

    def inserisciProtocollo(self):

        return

InitializeClass(IolIride)