# encoding=utf-8
import json
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.http import FormRequest, Request
from hts_peru.items import Hts
import sys
### Kludge to set default encoding to utf-8
reload(sys)
sys.setdefaultencoding('utf-8')


class HtsListSpider (BaseSpider):
    name = "hts-list"
    start_urls = [
        'http://www.aduanet.gob.pe/itarancel/arancelS01Alias?accion=buscarPartida&esframe=1'
    ]
    detail_urls = [
        'http://www.aduanet.gob.pe/itarancel/JSPListadoPartidaArancel.jsp',
        'http://www.aduanet.gob.pe/itarancel/JSPDetallePartidaArancel.jsp',
        'http://www.aduanet.gob.pe/itarancel/arancelS01Alias?accion=consultarUnidadMedida&cod_partida={0}',
        'http://www.aduanet.gob.pe/itarancel/arancelS01Alias?accion=consultarConvenio&cod_partida={0}'
    ]

    def parse(self, response):

        parser = HtmlXPathSelector(response)
        rows = parser.select('//form/table/tr[position()>1]')
        form_requests = []
        for row in rows:
            code = row.select('.//td[1]/a/font/text()').extract()
            name = row.select('.//td[2]/font/text()').extract()
            if len(code) > 0 and len(name) > 0:
                hts = Hts()
                hts['code'] = self.parse_hts_data(code[0])
                hts['name'] = self.parse_hts_data(name[0])
                hts['country'] = 'PE'
                form_request = FormRequest(url=self.start_urls[0],
                                           formdata={'cod_partida':hts["code"]},
                                           callback=self.hts_detail,
                                           meta={ 'hts': hts })

                form_requests.append(form_request)
        return form_requests

    def hts_detail(self, response):
        hts = response.meta['hts']
        return FormRequest(url=self.detail_urls[1],
                           formdata={'cod_partida': hts['code']},
                           callback=self.hts_percent_detail,
                           meta={'hts' : hts})

    def hts_percent_detail(self, response):
        hts = response.meta['hts']
        ley = {}
        parser = HtmlXPathSelector(response)
        table = parser.select('//div/center')
        title = parser.select('//div/table/tr[1]/td[2]/font/text()').extract()

        i = 1
        for title in title:
            ley = {i:title}
            i = i + 1

        value_detail = {}
        i = 1
        try :
            for table in table:
                rows = parser.select('//div/center/table['+str(i)+']/tr[position()>1]')
                for row in rows:
                    value = {}
                    description = row.select('.//td[1]/font/text()').extract()
                    percentage  = row.select('.//td[2]/font/text()').extract()
                    if len(description) > 0 and len(percentage) > 0:
                        description = self.parse_hts_data(description[0])
                        if self.validate_description(description):
                            value = { ley[i] : {
                            'description' : description.replace(' ',''),
                            'percentage'  : self.parse_hts_data(percentage[0]).replace(' ','').replace('%',''),
                            'currency' : '%',
                            'targetValue' : 'CIF'}
                            }
                            value_detail.update(value)
                i = i + 1
            hts['tariff_all'] = value_detail
        except:
            pass

        return Request(url=self.detail_urls[2].format(hts['code']),
                       callback=self.hts_quantity_detail,
                       meta={ 'hts':hts })

    def parse_hts_data(self, data):
        data = data.replace('\t','').replace('\n','').replace('\r','')
        data = data.replace('.','').replace(' - ','')
        #.replace('\u00f3','ó')
        #data = data.replace('\u00e1','á').replace('\u00bb','ú').replace('\u00ed','í')

        return data

    def validate_description(self, description):
        if description == u'Derecho Específicos '\
        or description == u'Derecho Antidumping':
            return False
        return True

    def is_quantity(self, description):
        if description != u'Unidad de Medida':
            return True
        return False

    def hts_quantity_detail(self, response):
        '''
        Peticion usada para capturar las unidades metricas
        que maneja cada HTS (ejemplo: KG, LT, MTS)
        '''
        hts = response.meta['hts']
        parser = HtmlXPathSelector(response)
        count = len(parser.select('//center[2]/table/tr'))

        father_code = hts['code']
        if count == 5: hts['hs'] = father_code[-4]
        if count == 6: hts['hs'] = father_code[-2]

        rows = parser.select('//center[3]/table/tbody/tr[1]')
        hts['quantity'] = []
        for row in rows:
            hts['quantity'].append(self.parse_hts_data(row.select('td[3]/div/font/text()').extract()[0]).replace(' ',''))

        return Request(url=self.detail_urls[3].format(hts['code']),
                       callback=self.hts_member_detail,
                       meta={ 'hts':hts })

    def hts_member_detail(self, response):
        '''
        Peticion usada para capturar las tarifas que se manejan
        con los paises a considerar en la aplicacion, dentro del HTS (EEUU, China, Singapur, Colombia)
        '''
        hts = response.meta['hts']
        tariffs = {}
        detail_tariff={}
        parser = HtmlXPathSelector(response)
        rows = parser.select('//center[3]/table/tr[position()>1]')
        for row in rows:
            country = self.parse_hts_data(row.select('td[1]/center/text()').extract()[0])
            if self.is_valid_country(country):
                tariff = {self.get_country_alias(country) : {
                    'value': self.parse_hts_data(row.select('td[7]/center/text()').extract()[0]).replace('%',''),
                    'value2': self.parse_hts_data(row.select('td[6]/center/text()').extract()[0]).replace('%',''),
                    'currency': '%',
                    'targetValue': 'CIF'}
                }
                detail_tariff.update(tariff)

        hts['tariff'] = detail_tariff
        return hts

    def is_valid_country(self, country):
        if country == 'EEUU' or \
           country == 'CHINA':
            return True
        return False

    def get_country_alias(self, country):
        if country == 'EEUU':   return 'US'
        if country == 'CHINA':    return 'CN'

