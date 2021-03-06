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
from iol.gisweb.alghero.IolIride import IrideProtocollo
from base64 import b64encode

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

    security.declarePublic('sendThisMail')
    def sendThisMail(self,obj,ObjectId, sender='', debug=0,To='',password=''):
        doc = obj
        db = doc.getParentDatabase()
        iDoc = IolApp(doc)
        diz_mail = iDoc.getConvData('mail_%s' %('dehor'))
        
        msg_info = dict(numero_pratica = doc.getItem('numero_pratica'),titolo = doc.Title(),
        now = DateTime().strftime('%d/%m/%Y'),istruttore = doc.getItem('istruttore'),numero_protocollo = doc.getItem('numero_protocollo'),
        link_pratica = doc.absolute_url(), data_pratica = doc.getItem('data_pratica'), istruttoria_motivo_sospensione = doc.getItem('istruttoria_motivo_sospensione'))
        args = dict(To = doc.getItem('fisica_email') if To == '' else To,From = sender,as_script = debug)
        custom_args = dict()
        
        if not args['To']:

            plone_tools = getToolByName(doc.getParentDatabase().aq_inner, 'plone_utils')
            msg = ''''ATTENZIONE! Non e' stato possibile inviare la mail perche' non esiste nessun destinatario'''
            plone_tools.addPortalMessage(msg, request=doc.REQUEST)
            
        attach_list = doc.getFilenames()
        
        if ObjectId in diz_mail.keys():
            
            if diz_mail[ObjectId].get('attach') != "":
                msg_info.update(dict(documenti_autorizzazione = doc.getItem('documenti_autorizzazione')))                 
                msg_info.update(dict(attach = diz_mail[ObjectId].get('attach')))

                custom_args = dict(Object = diz_mail[ObjectId].get('object') % msg_info,
                msg = doc.mime_file(file = '' if not msg_info.get('attach') in attach_list else doc[msg_info['attach']], text = diz_mail[ObjectId].get('text') % msg_info, nomefile = diz_mail[ObjectId].get('nomefile')) % msg_info)
            else:                
                custom_args = dict(Object = diz_mail[ObjectId].get('object') % msg_info,
                msg = diz_mail[ObjectId].get('text') % msg_info)      
        if custom_args:            
            args.update(custom_args)
            
            return IolDocument(doc).sendMail(**args)

    # restituisce il tipo di parere
    security.declarePublic('gruppiPareri')
    def gruppiPareri(self,obj):
        
        doc = obj
        current_member = doc.getParentDatabase().getCurrentUserId()
        groups_tool = getToolByName(doc, 'portal_groups')        

        pareri_richiesti = doc.getItem('req_parere','').split(',')
        gruppi = [grp.getId() for grp in groups_tool.getGroupsByUserId(current_member) if grp.getId().startswith('istruttori-pareri-')]
        if len(gruppi)>0:
            return gruppi[0].split('-')[-1]



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
                    diz_exist_pagamenti[codice]['stato_pagamento'] = stato_pagamento
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
        
        allegato_pagamento = [x for x in [i for i in doc.getItems() if i.startswith('ricevuta_pagamento')] if doc.getItem(x)!={}]
        allegato_rate = [x for x in [i for i in doc.getItems() if i.startswith('rate_pagamento_ricevuta')] if doc.getItem(x)!={}]

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
                if doc.getItem('numero_rate_allegate') == 0:
                    update = updateDizPagamenti(diz_pagamenti,diz_exist_pagamenti,'in attesa di verifica',codice_allegato=codice_allegato)                
                elif doc.getItem('numero_rate_allegate') >= 1 and len(allegato_rate) > 0:
                    
		    update = updateDizPagamenti(diz_pagamenti,diz_exist_pagamenti,'in attesa di verifica',codice_allegato=codice_allegato)                
                    dg = iDoc.translateDizToList('sub_elenco_pagamenti','elenco_pagamenti_temp',update)
                    doc.setItem('elenco_pagamenti_temp',dg)
                    return dg                 
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

    security.declarePublic('ratePagamenti')
    def ratePagamenti(self,obj,codice_pagamento=''):
        doc = obj
        iDoc = IolApp(doc)
        db = doc.getParentDatabase()
        pagamenti = doc.getItem('elenco_pagamenti','')
        
        list_rata = [v for v in pagamenti if codice_pagamento in v[0]][0]
        importo = list_rata[1]
        rata = float(importo)/4
        list_rata[1]=round(rata,2)
        list_rata[4]='non pagato'
        k= list_rata[0][:-2]
        del list_rata[0]
        diz={}
        # crea dizionario con chiavi i codici delle rate
        for i in range(4):
            key = '%s0%s' %(k,i+1)
            diz[key]=list_rata

        fine = doc.getItem('autorizzata_al')
        inizio = doc.getItem('autorizzata_dal')
        tipo_occupazione = doc.getItem('durata_occupazione')
        def scadenzaRate(diz,date_scadenza):
            n_diz = dict()
            anno = DateToString(fine,'%Y')
            diz_ord = diz.keys()
            diz_ord.sort()
            
            res = dict()
           
            for idx,rata in enumerate(diz_ord):        
                num_rata = rata[-1]
                alist = list()
                if int(idx) + 1 == int(num_rata):            
                    l_rata = diz[rata]
                    if date_scadenza[idx]!='':            
                        data_scad = '%s/%s' %(date_scadenza[idx],anno)
                        l_rata[5] = data_scad
                        n_diz[rata] = l_rata
                    for i in l_rata:
                        alist.append(i)
                    res[rata]=alist
             
            return res
        def calcolaPeriodoIntermedio(inizio,fine):
            intermedio = []
            durata = int(fine - inizio)/3    
            intermedio.append(DateToString(addToDate(inizio, durata , units='days'),'%d/%m'))
            intermedio.append(DateToString(addToDate(inizio, durata*2 , units='days'),'%d/%m'))
            return intermedio  
        if fine < addToDate(inizio, 8, units='months'):
            # inferiore a 8 - 4 mesi
            scadenza_rate_inf4 = [0,0,0,0] 
                  
                       
            scadenza_rate_inf4[0] = ''
            scadenza_rate_inf4[1] = calcolaPeriodoIntermedio(inizio,fine)[0]
            scadenza_rate_inf4[2] = calcolaPeriodoIntermedio(inizio,fine)[1]
            scadenza_rate_inf4[3] = DateToString(fine,'%d/%m')
            diz_scadenze = scadenzaRate(diz,scadenza_rate_inf4)
            
        # anno solare intero        
        else:
            diz_scadenze = scadenzaRate(diz,['','30/04','31/07','31/10'])      
        # gestione dei fields associati al datagrid    
        form = db.getForm('sub_elenco_pagamenti')
        fld = form.getFormField('elenco_rate_pagamenti')
        elenco_fields = fld.getSettings().field_mapping    
        lista_fields = elenco_fields.split(',')    

        dg=[]
        for v in diz_scadenze.keys():
            lista=[v]
            ll=[i for i in diz_scadenze[v]]
            lista = lista +ll
            if len(lista) < len(lista_fields):
                diff_fields = len(lista_fields) -len(lista)
                # add empty element to list
                for i in range(diff_fields):            
                    lista.insert(len(lista),'')
            dg.append(lista)
        dg.sort()
        return dg

    security.declarePublic('creaElencoRate')
    def creaElencoRate(self,obj):
        doc = obj
        iDoc = IolApp(doc)
        db=doc.getParentDatabase()
        if doc.getItem('elenco_rate_pagamenti',''):
            rate= iDoc.translateListToDiz('sub_elenco_pagamenti','elenco_rate_pagamenti')
        else:
            rate = []
        if doc.getItem('elenco_rate_pagamenti_temp',''):
            pagamenti_temp = iDoc.translateListToDiz('sub_elenco_pagamenti','elenco_rate_pagamenti_temp')
        else:
            pagamenti_temp = []
        form = db.getForm('sub_elenco_pagamenti')
        fld = form.getFormField('elenco_rate_pagamenti')
        # genera un dizionario di dizionari con chiavi, i codici dei pagamenti
        def dizKeyCod(listDiz):
            d={}
            for diz in listDiz:    
                d[diz['codice_sub_pagamento']]=diz        
            return d
        rate_richieste = doc.getItem('permesso_rate_opt')

        if not isinstance(rate_richieste,list) and rate_richieste:    
            rate_richieste = [rate_richieste]
         
        # crea il dg delle rate
        if not doc.getItem('elenco_rate_pagamenti'):
            
            if len(rate_richieste) > 0:                
                dg_rate = self.ratePagamenti(doc,rate_richieste[0])
                return dg_rate
                doc.setItem('elenco_rate_pagamenti_temp',dg_rate)
                return dg_rate
        else:
            if iDoc.confrontaDiz(dizKeyCod(rate),dizKeyCod(pagamenti_temp)) == True:
                # i dizionari  non sono cambiati quindi non è stato aggiornato manualmente il dg
                if len(rate_richieste) > 0:      
                    dg_rate = self.ratePagamenti(doc,rate_richieste[0])
                    doc.setItem('elenco_rate_pagamenti_temp',dg_rate)
                    return dg_rate


    security.declarePublic('acquisisciMittente')
    def acquisisciMittenti(self,obj):
        doc = obj
        res = dict(
            CodiceFiscale="%s" %doc.getItem('fisica_cf',''),
            CognomeNome="%s %s" % (doc.getItem('fisica_cognome',''),doc.getItem('fisica_nome','')),
            Nome="%s" %doc.getItem('fisica_nome','')
        )
        return [res]

    security.declarePublic('acquisisciAllegati')
    def acquisisciAllegati(self,obj):
        doc = obj
        try:
        	file = doc.restrictedTraverse('@@wkpdf').get_pdf_file()
        except:
        	file = ""
        res = dict(
            TipoFile="PDF",
            Image=b64encode(file)
        )
        return [res]

    security.declarePublic('protocolla')
    def protocolla(self,mittenti,allegati,tipodoc,oggetto):
        ws = IrideProtocollo(service='wsprotocollodm.asmx?WSDL')
        res = ws.InserisciProtocollo(mittenti=mittenti,allegati=allegati,TipoDocumento='DG',Oggetto=oggetto)
        return res
