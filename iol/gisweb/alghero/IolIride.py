# -*- coding: utf-8 -*-
from zope.interface import Interface, implements, Attribute
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from zope.component import getUtility,adapts
from Products.CMFPlomino.interfaces import IPlominoDocument
import config
from .interfaces import IIolApp,IIolIride

# -*- coding: utf-8 -*-

from suds.client import Client
from datetime import datetime, date
from base64 import b64encode

from lxml import etree

from DateTime import DateTime

#from XmlDict import XmlDictConfig

# this url is good if you
# ssh siti.provincia.sp.it -L 3340:10.94.128.230:80 -p 2211 (or 2222)
#URL = 'http://127.0.0.1:3340/ulissetest/iride/web_services_20/WSProtocolloDM/WSProtocolloDM.asmx?WSDL'
# This one is good at Spezia
#URL = 'http://10.94.128.230/ulissetest/iride/web_services_20/WSProtocolloDM/WSProtocolloDM.asmx?WSDL'

UTENTE = 'AMMINISTRATORE'
RUOLO = "UO_220"
APPARTENENZA = 'DOCUMENTO'

def get_current_datetime_as_string():
    return datetime.now().isoformat()

def prepare_string(data, docid):
    """ """
    result = ["<DatiUtenteIn>"]
    for tablename, rows in data.items():
        result.append('<table name="%s">' % tablename)
        for i, row_original in enumerate(rows):
            row = dict(row_original,
                #IRIDE_DOCID=docid,
                #IRIDE_PROGR=i,
                #IRIDE_FONTE='GW',
                #IRIDE_DATINS=get_current_datetime_as_string(),
            )
            result.append('<row>')
            for keyvalue in row.items():
                result.append('<field name="%s">%s</field>' % keyvalue)
            result.append('</row>')
        result.append('</table>')
    result.append("</DatiUtenteIn>")
    return ''.join(result)

def prepare_string2(data, docid):
    root = etree.Element('DatiUtenteIn')
    doc = etree.ElementTree(root)
    for tablename, rows in data.items():
        locals()[tablename] = etree.SubElement(root, 'table', name=tablename)
        for i, row in enumerate(rows):
            # a quanto pare NON servono più
            #row.update(
                #dict(
                    #IRIDE_DOCID = docid,
                    #IRIDE_PROGR = i,
                    #IRIDE_FONTE = 'GW',
                    #IRIDE_DATINS = get_current_datetime_as_string(),
                #)
            #)
            locals()['row_%s' % i] = etree.SubElement(locals()[tablename], 'row')
            for key,value in row.items():
                locals()['%s_%s' % (key, i)] = etree.SubElement(locals()['row_%s' % i], 'field', name=key)
                locals()['%s_%s' % (key, i)].text = u"%s" % value
    return doc

def assign_value(obj, value, validator, transform):
    if value in ('', None, ):
        obj.text = ''
    else:
        assert validator(value), 'Errore di validazione del dato (%s: %s)' % (obj, value, )
        obj.text = transform(value)

xsi = '{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation'

def doc2xml(root, pprint=False):
    return etree.tostring(root, pretty_print=pprint)

def prepare_xml_richiesta(dati_allegati=[], **kw):
    """
    doc url: http://projects.gisweb.it/projects/gisweb-irideworkflow/wiki/Wiki#Descrizione-degli-argomenti-wap

    Le chiavi per i vari sub-nodi sono uniche quindi ho previsto possano anche essere
    passate direttamente come parametri di richiesta. In alternativa possono essere
    passati 3/4 dizionari distinti (dati_richiedente, dati_titolare,
    dati_integrazione (opzionale) e dati_allegati) contenenti ognuno la valorizzazione
    dei rispettivi parametri.

    Per dettagli vedere xml_templates
    """

    root_attributes = {xsi: "C:\Documents and Settings\VitDe\Desktop\pratiche\wm_attiva_procedimento.xsd"}
    root = etree.Element('wm_attiva_procedimento', encoding='ISO-8859-1', **root_attributes)
    doc = etree.ElementTree(root)

    dati_procedimento = etree.SubElement(root, 'dati_procedimento')

    from xml_templates import titolare, richiedente, allegati, processo

    dati_processo = etree.SubElement(dati_procedimento, 'dati_processo')
    for el,v in processo.items():
        locals()[el] = etree.SubElement(dati_processo, el)
        if 'dati_processo' in kw and el in kw['dati_processo']:
            assign_value(locals()[el], kw['dati_processo'][el], *v)
        elif el in kw:
            assign_value(locals()[el], kw[el], *v)

    # almeno il titolare della richiesta è obbligatorio
    dati_titolare = etree.SubElement(dati_procedimento, 'dati_titolare')
    test = dict()
    for el,v in titolare.items():
        locals()[el] = etree.SubElement(dati_titolare, el)
        if 'dati_titolare' in kw and el in kw['dati_titolare']:
            assign_value(locals()[el], kw['dati_titolare'][el], *v)
        elif el in kw:
            assign_value(locals()[el], kw[el], *v)
            test[el] = kw[el]

    if 'dati_richiedente' in kw or any([i.startswith('ric_') for i in kw]):
        # se non viene fornita informazione riguardante il richiedente evito
        dati_richiedente = etree.SubElement(dati_procedimento, 'dati_richiedente')
        for el,v in richiedente.items():
            locals()[el] = etree.SubElement(dati_richiedente, el)
            if 'dati_richiedente' in kw and el in kw['dati_richiedente']:
                assign_value(locals()[el], kw['dati_richiedente'][el], *v)
            elif el in kw:
                assign_value(locals()[el], kw[el], *v)

    inc = 0
    for allnfo in dati_allegati:
        locals()['dati_allegati_%s' % inc] = etree.SubElement(dati_procedimento, 'dati_allegati')
        for knfo,vnfo in allnfo.items():
            locals()[knfo] = etree.SubElement(locals()['dati_allegati_%s' % inc], knfo)
            v = allegati[knfo]
            assign_value(locals()[knfo], vnfo, *v)
        inc += 1

    if any([i.startswith('int_') for i in kw]):
        from xml_templates import integrazione
        dati_integrazione = etree.SubElement(dati_procedimento, 'dati_integrazione')
        for el,v in integrazione.items():
            locals()[el] = etree.SubElement(dati_integrazione, el)
            if 'dati_integrazione' in kw and el in kw['dati_integrazione']:
                assign_value(locals()[el], kw['dati_integrazione'][el], *v)
            elif el in kw:
                assign_value(locals()[el], kw[el], *v)

    return doc

def prepare_dati_procedimento(**kw):
    """
    doc url: http://projects.gisweb.it/projects/gisweb-irideworkflow/wiki/Wiki#Descrizione-degli-argomenti-wap
    """

    root_attributes = {xsi: "http:www.cedaf.it\schema\dati_procedimento.xsd"}
    root = etree.Element('dati_procedimento', encoding='ISO-8859-1', **root_attributes)
    doc = etree.ElementTree(root)

    from xml_templates import procedimento
    for el,v in procedimento.items():
        locals()[el] = etree.SubElement(root, el)
        if el in kw: assign_value(locals()[el], kw[el], *v)

    return doc

def prepare_ls_oneri(**wk):
    """
    """

    root_attributes = {xsi: "http:www.cedaf.it\schema\dati_procedimento.xsd"}
    root = etree.Element('dati_procedimento', encoding='ISO-8859-1', **root_attributes)
    doc = etree.ElementTree(root)
    from xml_templates import oneri
    for el,v in oneri.items():
        locals()[el] = etree.SubElement(root, el)
        if el in kw: assign_value(locals()[el], kw[el], *v)

    return doc

def deep_normalize(d):
    """ Normalize content of object returned from functions and methods """
    if 'sudsobject' in str(d.__class__):
        d = deep_normalize(dict(d))
    elif isinstance(d, dict):
        for k,v in d.iteritems():
            if 'sudsobject' in str(v.__class__):
                #print k, v, '%s' % v.__class__
                r = deep_normalize(dict(v))
                d[k] = r
            elif isinstance(v, dict):
                r = deep_normalize(v)
                d[k] = r
            elif isinstance(v, (list, tuple, )):
                d[k] = [deep_normalize(i) for i in v]
            elif isinstance(v, datetime):
                # per problemi di permessi sugli oggetti datetime trasformo
                # in DateTime di Zope
                d[k] = DateTime(v.isoformat())
    elif isinstance(d, (list, tuple, )):
        d = [deep_normalize(i) for i in d]

    return d

class Iride():
    """ Base class for interfacing to Iride web services """
    HOST = 'http://srv-protocollo' # 'http://127.0.0.1:3340' #
    SPATH = 'ulisse/iride/web_services_20/wsprotocolloDM/'
    Utente = UTENTE
    Ruolo = RUOLO
    timeout = 180

    def __init__(self, testinfo=False, **kw):
        self.testinfo = testinfo
        for k,v in kw.items():
            setattr(self, k, v)
        url = '/'.join((self.HOST, self.SPATH, self.service))
        self.url = url
        self.client = Client(url, location=url, timeout=self.timeout)

    def _compile_xml_(self, xml, child_of='', **kw):
        """ Xml fields filling """
        for k,v in dict(xml).items():
            if v in (None, '', ):
                xml[k] = '' if not k in kw else kw[k]
            else:
                class_type = str(v.__class__)
                if class_type.startswith('suds.sudsobject'):
                    suds_type = class_type.split('.')[2]
                    if suds_type.startswith('ArrayOf'):
                        if k in kw:
                            for o in kw[k]:
                                newname = suds_type[7:]
                                parent = child_of + '.' + k # just for debug
                                newobj = self.build_xml(newname, child_of=parent, **o)
                                xml[k][xml[k].__keylist__[0]].append(newobj)
                    else:
                        pars = {} if not k in kw else kw[k]
                        parent = child_of + '.' + k # just for debug
                        xml[k] = self._compile_xml_(xml[k], child_of=parent, **pars)
        return xml

    def build_xml(self, name, **kw):
        """ Generic XML helper """
        plain_xml = self.client.factory.create(name)
        compiled_xml = self._compile_xml_(plain_xml, **kw)
        return compiled_xml

    def build_obj(self, name, **kw):
        """ Helper for getting a dictionary with keys loaded from the
        correspondent xml-like object
        """
        xml = self.client.factory.create(name)
        obj = dict()
        for k in dict(xml):
            obj[k] = kw.get(k) or ''
        return obj

    def build_mittente(self, **kw):
        """ XML helper for MittenteDestinatarioIn-like object creation """
        return self.build_xml('MittenteDestinatarioIn', **kw)

    def build_allegato(self, **kw):
        """ XML helper for AllegatoIn-like object creation """

        # Image parameter value is required to be base64 encoded
        # I don't know how to verify if it's already encoded so DO NOT ENCODE! I do.
        #if 'Image' in kw:
        #    kw['Image'] = b64encode(kw['Image'].data or '')

        return self.build_xml('AllegatoIn', **kw)

    def parse_response(self, res):
        """ Common response parsing """
        return deep_normalize(dict(res))

    def query_service(self, methodname, request, *other):
        """ Standardize the output """
        service = getattr(self.client.service, methodname)
        out = dict(success=0, service=methodname)
        if self.testinfo: t0 = datetime.now()
        try:
            if isinstance(request, dict):
                res = service(**request)
            else:
                res = service(request, *other)
        except Exception as err:
            out['message'] = '%s' % err
            # for debug purposes in case of exception reasons are in input data
            out['request'] = deep_normalize(dict(request))
            out['xml_received'] = str(self.client.last_sent())
        else:
            out['result'] = self.parse_response(res)

            fail_test = any([i in out['result'] for i in ('Errore', 'cod_err', )])

            if methodname == 'ModificaDocumento' and fail_test:
                out['result'] = self._SendAgainModificaDocumentoEAnagrafiche()

            if self.testinfo:
                out['second_attempt'] = fail_test

            fail_test = any([i in out['result'] for i in ('Errore', 'cod_err', )])

            if self.testinfo or fail_test:
                out['request'] = deep_normalize((dict(request), )+other)
                out['request_repr'] = '%s' % request
                out['xml_received'] = str(self.client.last_sent())
            if not fail_test:
                out['success'] = 1
            if self.testinfo:
                # for backward compatibility with python 2.6
                total_seconds = lambda x: x.seconds + x.microseconds*10**-6
                out['time_elapsed'] = total_seconds(datetime.now()-t0)

        return out

    def get_ProtocolloIn(self, mittenti=[], allegati=[], **kw):
        """ XML helper for ProtocolloIn-like object creation """

        defaults = dict(
            Utente = UTENTE,
            Ruolo = RUOLO,
            Origine = 'A',
            MittenteInterno = 'UO_140',
            Data = date.today().isoformat(),
            Classifica = '04.09'
        )

        request = self.build_xml('ProtocolloIn', **dict(defaults, **kw))

        for info in mittenti:
            mittente = self.build_mittente(**info)
            request.MittentiDestinatari.MittenteDestinatario.append(mittente)

        for info in allegati:
            allegato = self.build_allegato(**info)
            request.Allegati.Allegato.append(allegato)

        return request

class IrideProtocollo(Iride):
    """
    Class for interfacing to Iride WSProtocolloDM web service
    """
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    service = 'wsProtocollodm/wsprotocollodm.asmx?WSDL'

    def __init__(self, **kw):
        Iride.__init__(self, **kw)

    def check(self):
        """ Check whether the connection is up """
        out = self.LeggiDocumento('000')
        if 'success' in out and 'result' in out:
            out.pop('result')
        else:
            out.pop('request')
        return out

    def LeggiDocumento(self, IdDocumento, **kw):
        """ Restituisce i dati di un documento eventualmente protocollato a
        partire da IdDocumento.

        IdDocumento { string }: identificativo del documento
        """

        defaults = dict(
            Utente = UTENTE,
            Ruolo = RUOLO,
        )
        defaults.update(kw)

        request = self.build_xml('LeggiDocumento',
            IdDocumento = IdDocumento,
            **defaults
        )

        return self.query_service('LeggiDocumento', request)

    security.declarePublic('InserisciProtocollo')
    def InserisciProtocollo(self, mittenti=[], allegati=[], **kw):
        """ Inserisce un documento protocollato e le anagrafiche (max 100)
        ed eventualmente esegue l'avvio dell'iter.

        mittenti e allegati: liste di dizionari delle informazioni per la
            costruzione di oggetti xml MittenteDestinatarioIn-like e AllegatoIn-like
            attraverso i rispettivi metodi build_mittente e buil_allegato.
        """

        defaults = dict(
            Utente = UTENTE,
            Ruolo = RUOLO,
            Origine = 'A',
            #MittenteInterno = 'PROTO02',
            Data = date.today().isoformat(),
            Classifica = '04.09',
            AggiornaAnagrafiche='S'
        )

        request = self.build_xml('ProtocolloIn', **dict(defaults, **kw))

        for info in mittenti:
            mittente = self.build_mittente(**info)
            request.MittentiDestinatari.MittenteDestinatario.append(mittente)

        for info in allegati:
            allegato = self.build_allegato(**info)
            request.Allegati.Allegato.append(allegato)

        return self.query_service('InserisciProtocollo', request)

    def InserisciDatiUtente(self, Identificativo, DatiUtente, **kw):
        """ Inserisce i dati utente associati a un documento, un soggetto o un'attivita'

        Identificativo: identificativo del documento (str);
        DatiUtente: dizionario delle informazioni per costruire un oggetto xml
                    contenente oggetti di DatiUtenteIn-like usando la funzione
                    prepare_string;
        """

        defaults = dict(
            Utente = UTENTE,
            Ruolo = RUOLO,
            Appartenenza = APPARTENENZA,
            CodiceAmministrazione = '',
            CodiceAOO = ''
        )

        request = self.build_obj('InserisciDatiUtente',
            Identificativo = Identificativo,
            DatiUtente = doc2xml(prepare_string2(DatiUtente, Identificativo)),
            **dict(defaults, **kw)
        )

        return self.query_service('InserisciDatiUtente', request)

    def InserisciDocumentoEAnagrafiche(self, mittenti=[], allegati=[], **kw):
        """
        Inserisce un documento non protocollato e le anagrafiche (max 100) ed
        eventualmente esegue l'avvio dell'iter
        """

        request = self.get_ProtocolloIn(mittenti=mittenti, allegati=allegati, **kw)

        return self.query_service('InserisciDocumento', request)

    def RicercaPerCodiceFiscale(self, CodiceFiscale, SoloProtocollo=False, **kw):
        """ Restituisce gli estremi dei documenti per codice fiscale
        dell'intestatario (eventualmente solo i protocollati).
        """

        defaults = dict(
            Utente = UTENTE,
            Ruolo = RUOLO,
            CodiceFiscale=CodiceFiscale,
            SoloProtocollo=SoloProtocollo
        )

        request = self.build_xml('RicercaPerCodiceFiscale', **dict(defaults, **kw))

        return self.query_service('RicercaPerCodiceFiscale', request)

    def _SendAgainModificaDocumentoEAnagrafiche(self):
        """ DEPRECATED """
        # 1. recupero il documento appena inviato
        bad_xml_request = str(self.client.last_sent())

        # 2. apporto le modifiche cablate
        from lxml import etree
        root = etree.fromstring(bad_xml_request)
        root[1][0].append(root[1][0][0][-2])
        root[1][0].append(root[1][0][0][-1])
        root[1][0][0] = root[1][0][0][0]
        good_xml_request = etree.tostring(root)

        # 3. mando di nuovo il documento
        import urllib2
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8',
            'Host': self.HOST[7:],
            'Content-Type': 'text/xml; charset=utf-8',
            'Content-Length': len(good_xml_request),
            'SOAPAction': "http://tempuri.org/ModificaDocumentoEAnagrafiche"
        }
        auth_handler = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)

        req = urllib2.Request(self.url, good_xml_request, headers)
        response = urllib2.urlopen(req)

        # 4. preparo la risposta
        def getTag(tag):
            """ Elimino eventuale name space (es. {http://tempuri.org/}) """
            if '}' in tag:
                return tag[tag.index('}')+1:]
            else:
                return tag

        the_page = response.read()
        resp = etree.fromstring(the_page)
        dresp = dict([(getTag(i.tag), i.text) for i in resp[0][0][0]])
        return dresp


    def ModificaDocumentoEAnagrafiche(self, **kw):
        """ Partendo dal docid, o in sua assenza dall'anno e numero protocollo,
        il sistema provvederà a recuperare il documento e ad aggiornarlo con le
        informazioni presenti nell'xml di richiesta.
        """

        defaults = dict(
            Utente = UTENTE,
            Ruolo = RUOLO,
            Origine = 'A',
        )

        #request = self.build_xml('ModificaDocumentoEAnagrafiche', ProtoIn=dict(defaults, **kw))
        request = self.build_xml('ModificaProtocolloIn', **dict(defaults, **kw))

        return self.query_service('ModificaDocumento', request, '', '')


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

