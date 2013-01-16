# -*- coding: utf-8 -*-
import json

class CapsuleParse:

    def __init__(self):
        pass

    def parse_srcadvalorem(self, img):
        slash = img.rfind('/') + 1
        advalorem = img[slash:]
        advalorem = advalorem.split('.')
        advalorem = advalorem[0]
        return advalorem

    def parse_code(self, code):
        code = code.strip()
        code = code.replace('.', '')
        return code

    def complete_code(self,code):
        code = self.parse_code(code)
        if len(code) == 4:
            code = code + "000000"
        if len(code) == 6:
            code = code + "0000"
        if len(code) == 8:
            code = code + "00"
        return code

    def parse_description(self, description):
        description = description.strip()
        description = description.replace('-', '')
        return description

    def read_jason(self, ruta):
        file_name = open(ruta).read()
        output_file = json.loads(file_name)
        return output_file

    def parse_dumping(self, dumping):
        dumping = dumping.strip()
        if dumping.find('There are no Trade Defence measures for this product') >= 0:
            return dumping
        else :
            import pdb;pdb.set_trace()

    def parse_advalorem(self,advalorem):
        advalorem = advalorem.strip()
        AdValorem = {
                    'currency': '%',
                    'percentage': advalorem,
                    'description': 'Ad / Valorem',
                    'targetValue' : 'CIF',
                     }

        return AdValorem

    def parse_general(self, general):
        General = []
        general = general.strip()
        Tax = ['General Sales Tax', 'Municipal Promotion Tax']
        #import pdb;pdb.set_trace()
        if general.find('Goods falling under this subheading are exempted from general sales tax') >= 0:
            #No tiene
            pass
        else :
            #Exceptions feature
            if general.find('other than those') >= 0:
                #Codigo de parseo
                Data = general.split('.')
                max = Data[2].rfind(',')
                feature = Data[2][:max]
                temp = {
                        'currency' : '%',
                        'percentage': '0',
                        'description': Tax[0],
                        'targetValue' : 'CIF',
                        'feature': feature
                        }
                General.append(temp)
                temp = {
                        'currency' : '%',
                        'percentage': '0',
                        'description': Tax[1],
                        'targetValue' : 'CIF',
                        'feature': feature
                        }
                General.append(temp)
            else:
                Data = general.split('%')
                tariff = []
                for data in Data:  
                    max = len(data)
                    min = data.rfind(' ')
                    temp = data[min:max]
                    tariff.append(temp)
                #Calculate Igv
                igv = float(tariff[0]) - float(tariff[1])
                temp = {
                        'currency' : '%',
                        'percentage': igv,
                        'description': Tax[0],
                        'targetValue' : 'CIF'
                        }
                General.append(temp)
                temp = {
                        'currency' : '%',
                        'percentage': tariff[1],
                        'description': Tax[1],
                        'targetValue' : 'CIF'
                        }
                #Register General / Municipal
                General.append(temp)
        return General

    def parse_insurance(self, insurange):
        insurange = insurange.strip()
        Data = insurange.split('%')
        max = len(Data[0])
        min = Data[0].rfind(' ')
        insurange = Data[0][min:max]
        Insurange = {
                    'currency': '%',
                    'percentage': insurange,
                    'description': 'Insurance',
                    'targetValue' : 'CIF'
                    }
        return Insurange