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
from zope.component import getUtility,queryUtility
from .interfaces import IIolApp
import DateTime
import datetime
from iol.gisweb.utils.config import USER_CREDITABLE_FIELD,USER_UNIQUE_FIELD,IOL_APPS_FIELD,STATUS_FIELD,IOL_NUM_FIELD,APP_FIELD

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
    def creaElencoPagamenti(self,codici_pagamenti,codice_allegato,allegato=False):
        utils = getUtility(IIolApp,self.tipo_app)
        return utils.creaElencoPagamenti(self.document,codici_pagamenti,codice_allegato,allegato=False)

    security.declarePublic('ratePagamenti')
    def ratePagamenti(self,obj,codice_pagamento):
        utils = getUtility(IIolApp,self.tipo_app)
        return utils.ratePagamenti(self.document,codice_pagamento)

    security.declarePublic('creaElencoRate')
    def creaElencoRate(self,obj):
        utils = getUtility(IIolApp,self.tipo_app)
        return utils.creaElencoRate(self.document)

    security.declarePublic('gruppiPareri')
    def gruppiPareri(self):
        utils = getUtility(IIolApp,self.tipo_app)
        return utils.gruppiPareri(self.document) 

    security.declarePublic('getConvData')
    def getConvData(self,json_data):
        utils = getUtility(IIolApp,'default')
        return utils.getConvData(json_data)

    security.declarePublic('sendThisMail')
    def sendThisMail(self,ObjectId,sender='',debug=0,To='',password=''):        
        utils = getUtility(IIolApp,self.tipo_app)
        return utils.sendThisMail(self.document,ObjectId,sender,debug,To,password)  

    security.declarePublic('elenco_modelli')
    def elenco_modelli(self,sub_path):
        doc = self.document
        app = APP_FIELD
        nullchoice = 'Manca il modello, scegliere un modello di stampa per abilitare la funzione|'
        outlist = [nullchoice]
        url_info = doc.get_property('ws_listmodel_URL')
        try:
            proj = doc.get_property('project')['value']
        except:
            proj = ''
        def open_my_url(url, **args):
            uu = '%s?%s' %(url, urlencode(args))
            return json.loads(open_url(uu))
        modelli=json.loads(self.printModelli(doc.getParentDatabase().getId()))    
        if modelli['success']==1:
            outlist1=['%s|%s' %(models,modelli[models]['model']) for models in modelli.keys() if models!='success']
            outlist = outlist1 + outlist
        elif 'value' in url_info:
            outlist += open_my_url(url_info['value'], app=app, group=sub_path, project=proj)

        if doc.test_mode() and len(outlist)==1:
            outlist += ['test|test']


        return outlist

    security.declarePublic('testWf')
    def testWf(self,wfname=''):
        obj = self.document
        import pdb; pdb.set_trace()
        wftool = api.portal.get_tool(name='portal_workflow')
        chain = wftool.getChainFor(obj)
        wf = wftool.getWorkflowById(wfname)
        transition = wftool.getTransitionsFor(obj)
        # restituisce info di una variabile
        info = wf.getInfoFor(obj,'review_state',default='')
        var = wf.listObjectActions(info)
        catVars = wftool.getCatalogVariablesFor(obj)
            #if wf.isActionSupported(obj, tr):
        return catVars
        
    security.declarePublic('printModelli')
    def printModelli(self,db_name='',grp='autorizzazione',field='documenti_autorizzazione', folder='modelli'):
        doc = self.document
        db = db_name.split('_')[-1]
        for obj in doc.getParentDatabase().aq_parent.listFolderContents():
            if obj.getId()==folder:
                folder= obj 
        dizFile={}
        try:
            for i in folder.getFolderContents():
                obj=i.getObject()
                if db in obj.getId():                
                    sub_folders = obj.getFolderContents()                
                    pathFolder = [i.getObject().absolute_url() for i in sub_folders if grp in i.getObject().getId()][0]            
                    fileNames = [i.getObject().keys() for i in sub_folders if grp in i.getObject().getId()][0]   
                    
                    if len(fileNames)>0:                    
                        dizFile={}
                        for fileName in fileNames:
                            diz={}
                            pathModel= '%s/%s' %(pathFolder,fileName)
                            
                            diz['model']= pathModel
                            diz['field']=field                        
                            dizFile[fileName]=diz
                            dizFile['success']=1                          
                    else:
                       
                        dizFile['model']='test'
                        dizFile['field']=field
                        
                    return json.dumps(dizFile,default=DateTime.DateTime.ISO,use_decimal=True)
        except:
            dizFile['success']=0
            return json.dumps(dizFile,default=DateTime.DateTime.ISO,use_decimal=True)            
    
    security.declarePublic('translateListSource')
    def translateListSource(self,lista,form='',field=''):
        doc = self.document
        db=doc.getParentDatabase()
	form = db.getForm(form)
	fld = form.getFormField(field)
	elenco_fields = fld.getSettings().field_mapping    
	lista_fields = elenco_fields.split(',')

	diz_tot=[]
	for idx,itm in enumerate(lista):
	    diz = {}
	    for k,v in enumerate(lista_fields):
		diz[v] = lista[idx][k]
	    diz_tot.append(diz)
	return diz_tot

    

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

    security.declarePublic('acquisisciMittenti')
    def acquisisciMittenti(self):
        app = self.document.getItem(config.APP_FIELD,config.APP_FIELD_DEFAULT_VALUE)
        utils = queryUtility(IIolApp,name=app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'acquisisciMittenti' in dir(utils):
            utils = getUtility(IIolApp,config.APP_FIELD_DEFAULT_VALUE)
        return utils.acquisisciMittenti(self.document)

    security.declarePublic('acquisisciAllegati')
    def acquisisciAllegati(self):
        app = self.document.getItem(config.APP_FIELD,config.APP_FIELD_DEFAULT_VALUE)
        utils = queryUtility(IIolApp,name=app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'acquisisciAllegati' in dir(utils):
            utils = getUtility(IIolApp,config.APP_FIELD_DEFAULT_VALUE)
        return utils.acquisisciAllegati(self.document)

    security.declarePublic('protocolla')
    def protocolla(self,mittenti=[],allegati=[],tipodoc='',oggetto=''):
        app = self.document.getItem(config.APP_FIELD,config.APP_FIELD_DEFAULT_VALUE)
        utils = queryUtility(IIolApp,name=app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'protocolla' in dir(utils):
            utils = getUtility(IIolApp,config.APP_FIELD_DEFAULT_VALUE)
        return utils.protocolla(mittenti=mittenti,allegati=allegati,tipodoc=tipodoc,oggetto=oggetto)

InitializeClass(IolApp)


