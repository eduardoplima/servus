import unittest

import sys, os

path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, path + '/../')

from extractors import NerRuleExtractor, NerNeuralNet, EntityExtractor

class TestNerMethods(unittest.TestCase):    
    @unittest.skip
    def test_nernn(self):
        msg_despesa_publica = """
        Gostaria de solicitar empenhos, licitações e contratos dos meses de janeiro a março de 2018 da Prefeitura 
        do Natal pagos a João da Silva (CPF 059.112.043-12) e para a empresa XXX (CNPJ 00.000.000/0001-91 )
        no valor de R$ 10.000,00.
        """
        msg_despesa_pessoal = """
        Quero saber a folha de pagaemto e os acúmulos de cargos na prefeitura de Mossoró também. Mande o resultado para fulano@tce.rn.gov.br. Folha de papel
        """
        msg_errada = """
        empenhs e pagumentos da prefeitura de caico
        """

        ner_nn = NerNeuralNet()

        dict_desp_publ = ner_nn.get_entities_dict(msg_despesa_publica)
        dict_desp_pess = ner_nn.get_entities_dict(msg_despesa_pessoal)
        dict_errada = ner_nn.get_entities_dict(msg_errada)

        print(dict_desp_pess)
        print(dict_desp_publ)
        print(dict_errada)

        self.assertIsNotNone(dict_desp_pess)
        self.assertIsNotNone(dict_desp_publ)
        self.assertIsNotNone(dict_errada)

    @unittest.skip
    def test_ner_rules(self):
        msg = """CPFS 05911205424 059.112.054-24 CNPJs 46.395.000/0001-39 46.395.000000139 eplima.cc@gmail.com"""

        ner_rule = NerRuleExtractor()
        dict_msg = ner_rule.get_entities_dict(msg)

        #print(dict_msg)

        self.assertIsNotNone(dict_msg)

    #@unittest.skip
    def test_extraction(self):
        msg_despesa_publica = """
        Gostaria de solicitar empenhos, licitacoes e contratos dos meses de janeiro a março de 2018 da Prefeitura 
        do Natal pagos a João da Silva (CPF 059.112.043-12) e para a empresa XXX (CNPJ 00.000.000/0001-91 )
        no valor de R$ 10.000,00. De 01/01/2019 a 31/12/2020! 1.1.2011 01-01-2010
        """

        ent_extractor = EntityExtractor()

        dict_pub = ent_extractor.get_entities_dict(msg_despesa_publica)

        print(dict_pub)

        self.assertIsNotNone(dict_pub)
