import unittest

import sys, os

path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, path + '/../')

from sqlalchemy import text
from database import Loader, Empenho, Orgao, ArquivoLRF, ArquivoXML, Session_siai

from datetime import datetime

class TestDB(unittest.TestCase):
    @unittest.skip
    def test_loader(self):
        session = Session_siai()
        table = Empenho
        query = session.query(Empenho.IdEmpenho,
        Orgao.NomeOrgao,
        Empenho.CPFCNPJCredor, 
        Empenho.NomeCredor,
        Empenho.Justificativa, 
        Empenho.DataEmpenho, 
        Empenho.ValorEmpenho,
        ).join(ArquivoLRF, isouter=True).join(ArquivoXML, isouter=True)\
            .join(Orgao, text("vw_Gen_Orgao.IdOrgao = COALESCE(Envio_ArquivoLRF.IdOrgao, Envio_ArquivoXML.IdUnidadeJurisdicionada)"))\
                .filter(text("(IdSituacaoArquivoLRF = 4 or IdSituacaoProcessamento = 4)"))
        
        l = Loader(table, query, 'DataEmpenho', 'CPFCNPJCredor')

        dts = [datetime(day=1, month=3, year=2020), datetime(day=1, month=5, year=2020)]

        id = 426

        doc = '02620622000148'

        l.add_cpfcnpj_filter([doc])
        l.add_orgao_filter([id])
        l.add_tempo_filter(dts)

        df = l.get_query_dataframe()

        self.assertEqual(len(df.CPFCNPJCredor.unique()),1)
        self.assertEqual(len(df.NomeOrgao.unique()),1)

        d1 = sorted(df.DataEmpenho)[0] 
        d2 = sorted(df.DataEmpenho)[-1]

        self.assertLessEqual(d2, dts[1].date())
        self.assertGreaterEqual(d1, dts[0].date())


