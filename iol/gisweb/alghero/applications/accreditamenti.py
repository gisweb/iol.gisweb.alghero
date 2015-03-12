# -*- coding: utf-8 -*-
from zope.interface import implements
from iol.gisweb.alghero.interfaces import IIolApp
from iol.gisweb.alghero.IolApp import IolApp
from zope import component
from AccessControl import ClassSecurityInfo
from plone import api

from gisweb.iol.permissions import IOL_READ_PERMISSION, IOL_EDIT_PERMISSION, IOL_REMOVE_PERMISSION
from gisweb.utils import  addToDate
from iol.gisweb.utils.config import USER_CREDITABLE_FIELD,USER_UNIQUE_FIELD,IOL_APPS_FIELD,STATUS_FIELD,IOL_NUM_FIELD
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from Products.CMFPlomino.PlominoUtils import DateToString, Now, StringToDate
from iol.gisweb.utils.IolDocument import IolDocument

class accreditamentiApp(object):
    implements(IIolApp)
    security = ClassSecurityInfo()
    def __init__(self):
        pass
    def __call__(self, *args, **kwargs):
        pass
    

    security.declarePublic('sendThisMail')
    def sendThisMail(self,obj,ObjectId, sender='', debug=0,To='',password=''):
        doc = obj
        db = doc.getParentDatabase()
        iDoc = IolApp(doc)
        diz_mail = iDoc.getConvData('mail_%s' %('accreditamento'))
        
        msg_info = dict(nome_app_richiesta = doc.getItem('nome_app_richiesta'))
        args = dict(To = doc.getItem('fisica_email') if To == '' else To,From = sender,as_script = debug)
        custom_args = dict()
        
        if not args['To']:

            plone_tools = getToolByName(doc.getParentDatabase().aq_inner, 'plone_utils')
            msg = ''''ATTENZIONE! Non e' stato possibile inviare la mail perche' non esiste nessun destinatario'''
            plone_tools.addPortalMessage(msg, request=doc.REQUEST)
            
        attach_list = doc.getFilenames()
        
        if ObjectId in diz_mail.keys():
            
            if diz_mail[ObjectId].get('attach') != "":                
                msg_info.update(dict(attach = diz_mail[ObjectId].get('attach')))

                custom_args = dict(Object = diz_mail[ObjectId].get('object') % msg_info,
                msg = doc.mime_file(file = '' if not msg_info.get('attach') in attach_list else doc[msg_info['attach']], text = diz_mail[ObjectId].get('text') % msg_info, nomefile = diz_mail[ObjectId].get('nomefile')) % msg_info)
            else:                
                custom_args = dict(Object = diz_mail[ObjectId].get('object') % msg_info,
                msg = diz_mail[ObjectId].get('text') % msg_info)      
        if custom_args:            
            args.update(custom_args)
            
            return IolDocument(doc).sendMail(**args)