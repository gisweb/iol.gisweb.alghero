# -*- coding: utf-8 -*-
from zope.interface import implements
from iol.gisweb.alghero.interfaces import IIolApp
from zope import component
from AccessControl import ClassSecurityInfo
from plone import api

from gisweb.iol.permissions import IOL_READ_PERMISSION, IOL_EDIT_PERMISSION, IOL_REMOVE_PERMISSION
import simplejson as json
from iol.gisweb.utils.config import USER_CREDITABLE_FIELD,USER_UNIQUE_FIELD,IOL_APPS_FIELD,STATUS_FIELD,IOL_NUM_FIELD,APP_FIELD
from Products.CMFCore.utils import getToolByName
from gisweb.utils import sendMail
import os

class defaultApp(object):
    implements(IIolApp)
    security = ClassSecurityInfo()
    def __init__(self):
        pass
    def __call__(self, *args, **kwargs):
        pass
    #Returns dict with all roles->users/groups defined in Iol application
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
    security.declarePublic('ratepagamenti')
    def ratepagamenti(self,obj,codice_pagamento):
        pass

    security.declarePublic('creaElencoRate')
    def creaElencoRate(self,obj):
        pass

    def getConvData(self,json_file):
        fName = "%s/mapping/%s.json" %(os.path.dirname(os.path.abspath(__file__)),json_file)
        
        if os.path.isfile(fName):
            json_data=open(fName)

            try:
                data = json.load(json_data)

            except ValueError, e:
                data = str(e)
                json_data.close()
               
        else:
            return fName
            data = dict()
        return data      

    

    


    security.declarePublic('creaElencoPagamenti')
    def creaElencoPagamenti(self,obj,codici_pagamenti,codice_allegato='',allegato=False):
        doc = obj
        iDoc = IolApp(doc)
        wf = getToolByName(doc, 'portal_workflow')
        db=doc.getParentDatabase()
        if doc.getItem('elenco_pagamenti'):    
            pagamenti= iDoc.translateListToDiz('sub_elenco_pagamenti','elenco_pagamenti')
        else:
            pagamenti = []
        if doc.getItem('elenco_rate_pagamenti',''):
            rate= iDoc.translateListToDiz('sub_elenco_pagamenti','elenco_rate_pagamenti')
        else:
            rate = []
        if doc.getItem('elenco_pagamenti_temp',''):
            pagamenti_temp = iDoc.translateListToDiz('sub_elenco_pagamenti','elenco_pagamenti_temp')
        else:
            pagamenti_temp = []
        form = db.getForm('sub_elenco_pagamenti')
        fld = form.getFormField('elenco_pagamenti')
        diz_pagamenti = iDoc.createMapPagamenti(codici_pagamenti)
        elenco_fields = fld.getSettings().field_mapping.split(',')
        def insertFieldAbsent(form,field,diz,elenco_field):
            for key in diz:        
                for i in elenco_fields:            
                    if i not in diz[key].keys():                
                        diz[key][i]=''
            return diz

        def createDizPagamenti(diz_pagamenti,stato_pagamento):
            lista_codici = diz_pagamenti.keys()
            elenco_dg = {}
            for codice in lista_codici:
                diz_pagamenti[codice]['stato_pagamento']= stato_pagamento
                diz_pagamenti[codice]['data_sub_pagamento']= DateToString(Now(),'%d/%m/%Y')    
            elenco_diz = [diz_pagamenti[codice] for codice in lista_codici]
            return elenco_diz


        def updateDizPagamenti(diz_pagamenti,diz_exist_pagamenti,stato_pagamento,codice_allegato):
            codici = [codice_allegato]
            for codice in diz_exist_pagamenti.keys():
                diz_exist_pagamenti[codice]['importo_sub_pagamento']=diz_pagamenti[codice]['importo_sub_pagamento']
                if codice in codici:
                    
                    diz_exist_pagamenti[codice]['stato_pagamento']=stato_pagamento
            lista = []        
            for k in diz_exist_pagamenti.keys():
                
                lista.append(diz_exist_pagamenti[k])
            return lista  

        # genera un dizionario di dizionari con chiavi, i codici dei pagamenti
        def dizKeyCod(listDiz):
            d={}
            for diz in listDiz:    
                d[diz['codice_sub_pagamento']]=diz        
            return d
        
        allegato_pagamento = [x for x in [i for i in doc.getItems() if i.startswith('ricevuta_pagamento')] if context.getItem(x)!={}]
        if not doc.getItem('elenco_pagamenti'):
    
            if len(allegato_pagamento) > 0:
                wf.doActionFor(doc, 'effettua_pagamento')
                dg_create = createDizPagamenti(insertFieldAbsent(form,fld,diz_pagamenti,elenco_fields),'in attesa di verifica')
                dg = iDoc.translateDizToList('sub_elenco_pagamenti','elenco_pagamenti_temp',dg_create)
                
                doc.setItem('elenco_pagamenti_temp',dg)
                #context.setItem('elenco_pagamenti',dg)
                return dg
                
            else:               
                dg_create = createDizPagamenti(insertFieldAbsent(form,fld,diz_pagamenti,elenco_fields),'non pagato')                
                dg = iDoc.translateDizToList('sub_elenco_pagamenti','elenco_pagamenti_temp',dg_create)                
                doc.setItem('elenco_pagamenti_temp',dg)
                return dg
        elif iDoc.confrontaDiz(dizKeyCod(pagamenti),dizKeyCod(pagamenti_temp)) == True:
            # i dizionari non sono cambiati quindi non è stato aggiornato manualmente il dg 
            
            if doc.wf_getInfoFor('wf_ricevuta_pagamento',wf_id='pagamenti_allegati') == True or doc.wf_getInfoFor('wf_ricevuta_pagamento',wf_id='pagamenti_allegati')=='true':
                
                #if doc.wf_getInfoFor('wf_effettuato_pagamento',wf_id='pagamenti_allegati') == True:            
                    #if doc.wf_getInfoFor('review_state',wf_id='pagamenti_allegati')=='pagamenti':
                        #wf.doActionFor(doc, 'effettua_pagamento')
                        
                diz_exist_pagamenti = dizKeyCod(pagamenti)
                
                update = updateDizPagamenti(diz_pagamenti,diz_exist_pagamenti,'in attesa di verifica',codice_allegato=codice_allegato)
                
                dg = iDoc.translateDizToList('sub_elenco_pagamenti','elenco_pagamenti_temp',update)
                doc.setItem('elenco_pagamenti_temp',dg)
                return dg
                #doc.setItem('elenco_pagamenti',dg)
            else:
                
                diz_exist_pagamenti = dizKeyCod(pagamenti)            
                
                update = updateDizPagamenti(diz_pagamenti,diz_exist_pagamenti,'non pagato',codice_allegato=codice_allegato)
                
                dg = iDoc.translateDizToList('sub_elenco_pagamenti','elenco_pagamenti_temp',update)
                
                doc.setItem('elenco_pagamenti_temp',dg)
                return dg
                #doc.setItem('elenco_pagamenti',dg)
        else:

            if allegato:
                diz_exist_pagamenti = dizKeyCod(pagamenti)
                update = updateDizPagamenti(diz_pagamenti,diz_exist_pagamenti,'in attesa di verifica',codice_allegato=codice_allegato)
                dg = iDoc.translateDizToList('sub_elenco_pagamenti','elenco_pagamenti',update)
                return dg
                
    def acquisisciMittenti(self,obj):
        return []

    def acquisciAllegati(selfself,obj):
        return []

    security.declarePublic('protocolla')
    def protocolla(self,mittenti,allegati,tipodoc,oggetto):
        return dict(
            result=dict(
                NumeroProtocollo = None
            )
        )



