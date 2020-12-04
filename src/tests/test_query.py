import unittest

import sys, os

path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, path + '/../')

from query import QueryBuilder

class TestParserMethods(unittest.TestCase):
    def test_query(self):
        qb = QueryBuilder()
        msg = "Solicito empenhos da Câmara de Natal entre janeiro e março de 2020 para a empresa CLIP PRODUCOES LTDA, cnpj 05557413000195"
        query = qb.query(msg)
        print("Mensagem do usuário: \n{}\n".format(msg))
        print("Entidades identificadas: \n{}\n".format(str(qb.ents)))
        print("Entidades processadas:\n{}\n".format(str(qb.parsed_ents)))
        print("Dados recuperados:\n{}\n".format(str(query)))