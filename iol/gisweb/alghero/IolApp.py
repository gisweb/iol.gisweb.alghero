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

    security.declarePublic('creaElencoPagamenti')
    def creaElencoPagamenti(self,codici_pagamenti,codice_allegato='',allegato=False):
        utils = getUtility(IIolApp,self.tipo_app)
        return utils.creaElencoPagamenti(self.document,codici_pagamenti,codice_allegato='',allegato=False)

    security.declarePublic('ratePagamenti')
    def ratePagamenti(self,obj,codice_pagamento):
        utils = getUtility(IIolApp,self.tipo_app)
        return utils.ratePagamenti(self.document,codice_pagamento)

    security.declarePublic('creaElencoRate')
    def creaElencoRate(self,obj):
        utils = getUtility(IIolApp,self.tipo_app)
        return utils.creaElencoRate(self.document)

    security.declarePublic('translateListToDiz')
    def translateListToDiz(self,form='',field=''):
        doc = self.document
        db=doc.getParentDatabase()
        form = db.getForm(form)
        fld = form.getFormField(field)
        elenco_fields = fld.getSettings().field_mapping    
        lista_fields = elenco_fields.split(',')


        diz_tot=[]
        for idx,itm in enumerate(doc.getItem(field)):
            diz = {}
            for k,v in enumerate(lista_fields):
                diz[v] = doc.getItem(field)[idx][k]
            diz_tot.append(diz)
        return diz_tot

    security.declarePublic('translateDizToList')
    def translateDizToList(self,form='',field='',diz_dg_elements=[]):
        doc = self.document
        db=doc.getParentDatabase()
        form = db.getForm(form)
        fld = form.getFormField(field)
        elenco_fields = fld.getSettings().field_mapping    
        lista_fields = elenco_fields.split(',')
        dg=[]
        for diz_element in diz_dg_elements:
            diz_pos = {}
            dg_element = []
            for key in diz_element.keys():
                if key in lista_fields:        
                    pos = lista_fields.index(key)
                    diz_pos[pos]=key        
            for i in range(len(diz_pos)):        
                k = diz_pos[i]
                dg_element.append(diz_element[k])
            dg.append(dg_element)
        return dg

    security.declarePublic('confrontaDiz')
    # confronta 2 dizionari e restituisce un booleano, True: sono uguali, False: i due diz sono diversi
    def confrontaDiz(self,diz,diz_temp):
        for d in diz.keys():
            if d in diz_temp.keys():
                sub_diz = diz[d]         

                for sub_diz_k in sub_diz.keys():                
                    if sub_diz[sub_diz_k] != diz_temp[d][sub_diz_k]:
                        return False
        return True     
    security.declarePublic('createMapPagamenti')
    def createMapPagamenti(self,codici_pagamenti):
        doc = self.document

        if len(codici_pagamenti)>0:
            cod_pagamenti = codici_pagamenti[0]

            db=doc.getParentDatabase()
            lista_codici_pagamenti = cod_pagamenti.keys()
            
            list_codici = map(lambda codice: 'pagamenti-' + str(codice) ,lista_codici_pagamenti)    
            diz_pagamenti = dict()
            for codice in list_codici:
                diz_pagamento = dict()
                for v in db.get_property(codice)['value'].replace('\n','').split(','):
                    # cod_lista es.'007' 
                    cod_lista = codice.split('-')[1]
                    key = v.split(':')[0]
                    value = v.split(':')[1]         

                    if key == 'importo_sub_pagamento' and cod_pagamenti[cod_lista] == '':
                        diz_pagamento[key]=value
                    elif key == 'importo_sub_pagamento':
                        diz_pagamento[key]=cod_pagamenti[cod_lista]    
                    else:    
                        diz_pagamento[key]=value

                diz_pagamenti[codice.split('-')[1]]=diz_pagamento   
            return diz_pagamenti
        else:
            return dict()
       

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
