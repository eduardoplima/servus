import os

import pandas as pd

from sqlalchemy import text, func, create_engine
from sqlalchemy.orm import create_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
from sqlalchemy.schema import Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import and_

from dotenv import load_dotenv

load_dotenv()

sql_usr = os.getenv('SQL_SERVER_USER')
sql_pass = os.getenv('SQL_SERVER_PASS')
sql_addr = os.getenv('SQL_SERVER_ADDR')
sql_port = os.getenv('SQL_SERVER_PORT')
sql_bdsiai = os.getenv('SQL_SERVER_BDSIAI')
sql_bdsiaidp = os.getenv('SQL_SERVER_BDSIAIDP')

Base = declarative_base()
str_siai = f'mssql+pyodbc://{sql_usr}:{sql_pass}@{sql_addr}:{sql_port}/{sql_bdsiai}?driver=FreeTDS'
engine_siai = create_engine(str_siai)

metadata_siai = MetaData(bind=engine_siai)
Session_siai = sessionmaker(bind=engine_siai)

'''
str_bdsiaidp = f'mssql+pyodbc://{sql_usr}:{sql_pass}@{sql_addr}:{sql_port}/{sql_bdsiaidp}?driver=FreeTDS'
engine_bdsiaidp = create_engine(str_bdsiaidp)
metadata_bdsiaidp = MetaData(bind=engine_bdsiaidp)
'''

class Empenho(Base):
    __table__ = Table(os.getenv('EMPENHO_TABLE'), metadata_siai, autoload=True)

class Liquidacao(Base):
    __table__ = Table(os.getenv('LIQUIDACAO_TABLE'), metadata_siai, autoload=True)

class Pagamento(Base):
    __table__ = Table(os.getenv('PAGAMENTO_TABLE'), metadata_siai, autoload=True)

class ArquivoLRF(Base):
    __table__ = Table(os.getenv('ARQUIVOLRF_TABLE'), metadata_siai, autoload=True)

class ArquivoXML(Base):
    __table__ = Table(os.getenv('ARQUIVOXML_TABLE'), metadata_siai, autoload=True)

class Orgao(Base):
    __table__ = Table(os.getenv('ORGAO_TABLE'), metadata_siai, autoload=True)
    __mapper_args__ = {
        'primary_key':[__table__.c.IdOrgao]
    }

# Interpreters

class Loader():
    def __init__(self, table:Base, query:Query, date_field:str, cpfcnpj_field:str):
        self.table = table
        self.query = query
        self.date_field = date_field
        self.cpfcnpj_field = cpfcnpj_field

    def add_orgao_filter(self, query_filter):
        self.query = self.query.filter(Orgao.IdOrgao.in_(query_filter))
    
    def add_tempo_filter(self, query_filter):
        if len(query_filter) == 1:
            self.query = self.query.filter(self.table.__getattribute__(self.table, self.date_field) >= query_filter[0])
        elif len(query_filter) == 2:
            self.query = self.query.filter(and_(self.table.__getattribute__(self.table, self.date_field) >= query_filter[0],
            self.table.__getattribute__(self.table, self.date_field) <= query_filter[1]))
        else:
            #Exception?
            pass

    def add_cpfcnpj_filter(self, query_filter):
        self.query = self.query.filter(self.table.__getattribute__(self.table, self.cpfcnpj_field).in_(query_filter))

    def get_query_dataframe(self):
        df = pd.read_sql(self.query.statement, self.query.session.bind)
        return df

class EmpenhoLoader(Loader):
    def __init__(self):
        self.session = Session_siai()
        table = Empenho
        query = self.session.query(Empenho.IdEmpenho,
        Orgao.NomeOrgao,
        Empenho.CPFCNPJCredor, 
        Empenho.NomeCredor,
        Empenho.Justificativa, 
        Empenho.DataEmpenho, 
        Empenho.ValorEmpenho,
        ).join(ArquivoLRF, isouter=True).join(ArquivoXML, isouter=True)\
            .join(Orgao, text("vw_Gen_Orgao.IdOrgao = COALESCE(Envio_ArquivoLRF.IdOrgao, Envio_ArquivoXML.IdUnidadeJurisdicionada)"))\
                .filter(text("(IdSituacaoArquivoLRF = 4 or IdSituacaoProcessamento = 4)"))

        super().__init__(table, query, 'DataEmpenho', 'CPFCNPJCredor')

class LiquidacaoLoader(Loader):
    def __init__(self):
        self.session = Session_siai()
        table = Liquidacao
        query = self.session.query(Pagamento).join(Liquidacao).join(Empenho)\
        .join(ArquivoLRF, isouter=True).join(ArquivoXML, isouter=True)\
            .join(Orgao, text("vw_Gen_Orgao.IdOrgao = COALESCE(Envio_ArquivoLRF.IdOrgao, Envio_ArquivoXML.IdUnidadeJurisdicionada)"))\
                .filter(text("(IdSituacaoArquivoLRF = 4 or IdSituacaoProcessamento = 4)"))

        super().__init__(table, query, 'DataLiquidacao', 'CPFCNPJCredor')
        
class PagamentoLoader(Loader):
    def __init__(self):
        self.session = Session_siai()
        table = Pagamento
        query = self.session.query(Pagamento).join(Liquidacao).join(Empenho)\
        .join(ArquivoLRF, isouter=True).join(ArquivoXML, isouter=True)\
            .join(Orgao, text("vw_Gen_Orgao.IdOrgao = COALESCE(Envio_ArquivoLRF.IdOrgao, Envio_ArquivoXML.IdUnidadeJurisdicionada)"))\
                .filter(text("(IdSituacaoArquivoLRF = 4 or IdSituacaoProcessamento = 4)"))

        super().__init__(table, query, 'DataPagamento', 'CPFCNPJCredor')