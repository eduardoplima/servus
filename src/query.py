from parsers import TempoParser, CNPJParser, CPFParser, OrgaoParser, ControleExternoParser

from extractors import EntityExtractor

class QueryBuilder(object):
    def __init__(self):
        self.ent = EntityExtractor()
        self.tempo_parser = TempoParser()
        self.cnpj_parser = CNPJParser()
        self.cpf_parser = CNPJParser()
        self.orgao_parser = OrgaoParser()
        self.ce_parser = ControleExternoParser()

        self.parser_dict = {
            'TEMPO' : self.tempo_parser,
            'CNPJ' : self.cnpj_parser,
            'CPF' : self.cnpj_parser,
            'ORGANIZACAO' : self.orgao_parser,
            'CONTROLEEXTERNO' : self.ce_parser
        }

    def build_query(self, query_dict):
        if not 'CONTROLEEXTERNO' in query_dict.keys():
            return

        loaders_cls = query_dict['CONTROLEEXTERNO']
        loaders = []

        query_dict.pop('CONTROLEEXTERNO')

        for L in loaders_cls:
            loader = L()
            for k,v in query_dict.items():
                if k == 'TEMPO' and v:
                    loader.add_tempo_filter(v)
                elif (k == 'CPF' or k == 'CNPJ') and v:
                    loader.add_cpfcnpj_filter(v)
                elif k == 'ORGANIZACAO' and v:
                    loader.add_orgao_filter(v)
            loaders.append(loader)

        return loaders

    def query(self, msg:str):
        self.ents = self.ent.get_entities_dict(msg)
        self.parsed_ents = []
        query = {}
        for k, v in self.ents.items():
            if k in self.parser_dict.keys():
                parser = self.parser_dict[k]
                p = parser.parse(v)
                self.parsed_ents.append(p)
                query[k] = p

        loaders = self.build_query(query)

        '''
        print(query)

        print([str(l.query) for l in loaders])
'''

        return [l.get_query_dataframe() for l in loaders]    



