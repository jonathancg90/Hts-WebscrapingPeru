# -*- coding: utf-8 -*-

from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.http import FormRequest, Request

from hts_peru.utilities.CapsuleParse import CapsuleParse
from hts_peru.items import Hts
from hts_peru.items import Hs
from hts_peru.items import Hts_tariff

import json


class HtsSpider (BaseSpider):
    name = "hts"
    start_urls = [
        'http://madb.europa.eu/madb/datasetPreviewFormATpubli.htm?datacat_id=AT&from=publi'        
    ]
    detail_urls = [
        'http://madb.europa.eu/madb/atDutyOverviewPubli.htm',
        'http://madb.europa.eu/madb/atDutyOverviewPubli.htm?',
        'http://madb.europa.eu/madb/atDutyDetailPubli.htm',
        'http://madb.europa.eu/madb/atDutyDetailPubli.htm?'
    ]

    def parse(self, response):
        cap = CapsuleParse()
        Codes = cap.read_jason('code.json')
        formRequests = []
        self.formDetail = []
        form_data = {
                    'countries': 'PE',
                    'country': 'all',
                    'countryid': '',
                    'datacat_id': 'AT',
                    'display': '20',
                    'hscode': '0101',
                    'langId': 'en',
                    'language': 'all',
                    'option': '1',
                    'sector': 'all',
                    'showregimes': '',
                    'submit': 'Search',
                    'license': 'Accept',
                    'year1': '',
                    'year2': ''
                    }

        for codes in Codes:
            hts = Hts()
            #hs = Hs()
            form_data['hscode'] = codes['codigo']
            hts['code'] = codes['codigo']
            formRequest = FormRequest(method='GET',
                                   url=self.detail_urls[0],
                                   formdata=form_data,
                                   callback=self.hts_list,
                                   meta={'hts':hts}
                                )
            formRequests.append(formRequest)
        return formRequests

    def hts_list(self, response):
        try:
            form_requests = []
            cap = CapsuleParse()
            hts = response.meta['hts']
            #print "CODIGO ENVIADO: " + str(hts)
            parser = HtmlXPathSelector(response)
            rows = parser.select('//div[4]/div[1]/div[1]/div[2]/div[1]/table/tr[position()>2]')
            for row in rows:
                code = row.select('.//td[1]/text()').extract()
                if(len(code) < 1):
                    code = row.select('.//td[1]/a/text()').extract()
                description = row.select('.//td[2]/text()').extract()
                print "CODIGO A ANALISAR: " + str(code) 
                if(len(code) > 0 and  len(description) > 0):
                    code = cap.parse_code(code[0])
                    url = row.select('.//td[1]/a/@href').extract()
                    #Para codios hs
                    #if(len(code) > 0 and  len(description) > 0):
                    #    if len(code) <= 6:
                        #    yield Hs(code=cap.parse_code(code[0]), name=cap.parse_description(description[0]))
                    #Verificar si contiene un link y si el codigo es mayor a 5 cifras
                    if len(url) > 0 and len(code) > 5:
                        #Solo codigos refenrentes al hs del json
                        if code.find(hts['code']) >= 0:
                            hts_tariff = Hts_tariff()
                            advalorem = row.select('.//td[3]/img/@src').extract()
                            advalorem = cap.parse_srcadvalorem(advalorem[0])
                            if(len(code) == 6):
                                hts_tariff['code'] = cap.parse_code(code + "0000")
                            else:
                                hts_tariff['code'] = cap.parse_code(code)
                            hts_tariff['name'] = cap.parse_description(description[0])
                            hts_tariff['hs'] = cap.parse_code(code)[:6]
                            hts_tariff['tariff_all'] = advalorem
                            print "CODIGO VALIDO: " +hts_tariff['code']                            

                            form_data = {
                                         'datasetid':'MAAT-PE12-05v001',
                                         'hscode': hts_tariff['code'],
                                         'countries':'PE',
                                         'datacat_id':'AT',
                                         'keyword':'',
                                         'submit':'',
                                         'showall':'T',
                                         'pathtoimage':'http://madb.europa.eu/at/images/&showall=T'
                                         }
                            form_request = FormRequest(
                                              method='GET',
                                              url=self.detail_urls[2],
                                              formdata=form_data,
                                              callback=self.hts_tariff,
                                              meta={'hts':hts_tariff}
                                              )
                            form_requests.append(form_request) 
            return form_requests
        except Exception,e:
            import pdb;pdb.set_trace()

    def hts_tariff(self, response):
        cap = CapsuleParse()
        hts = response.meta['hts']
        parse = HtmlXPathSelector(response)
        dumping = parse.select("//*[@id='col-2']/div[3]/div[1]/p/text()").extract()
        General = parse.select("//*[@id='col-2']/div[3]/div[2]/p[2]").extract()
        Insurance = parse.select("//*[@id='col-2']/div[3]/div[2]/p[4]").extract()

        AdValoren = hts['tariff_all']

        AdValoren = cap.parse_advalorem(AdValoren)
        Dumping = cap.parse_dumping(dumping[0])
        General = cap.parse_general(General[0])
        insurance = cap.parse_insurance(Insurance[0])

        tariff = []
        #tarrif.append(dumping)
        for general in General:
            tariff.append(general)
        tariff.append(insurance)
        tariff.append(AdValoren)
        hts['tariff_all'] = tariff
        return hts

