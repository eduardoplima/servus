import os, datetime, dateparser, locale, re
locale.setlocale(locale.LC_ALL, "pt_BR.utf8")

from abc import ABCMeta, abstractmethod

from functools import reduce
from itertools import zip_longest

from dotenv import load_dotenv
from fuzzywuzzy import fuzz, process

from database import EmpenhoLoader

def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)

class ServusParser(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def parse(self, ents):
        pass

class TempoParser(ServusParser):
    def __init__(self):
        self.months = ['janeiro'
                        ,'fevereiro'
                        ,'março'
                        ,'abril'
                        ,'maio'
                        ,'junho'
                        ,'julho'
                        ,'agosto'
                        ,'setembro'
                        ,'outubro'
                        ,'novembro'
                        ,'dezembro'
                        ,'jan'
                        ,'fev'
                        ,'mar'
                        ,'abr'
                        ,'mai'
                        ,'jun'
                        ,'jul'
                        ,'ago'
                        ,'set'
                        ,'out'
                        ,'nov'
                        ,'dez']

    def get_stack(self, ents):
        tempo_stack = []
        len_ents = len(ents)
        if not len_ents:
            return
        elif len_ents == 1:
            tokens = ents[0].split(" ")
        else:
            tokens = reduce(lambda x,y: x+y, list(map(lambda x:x.split(" "), ents)))
        for token in tokens:
            if token.isalpha() and token.lower() in self.months:
                ptoken = dateparser.parse(token)
                if ptoken:
                    #it's a month
                    tempo_stack.append(('MONTH', token))
            elif token.isnumeric():
                tempo_stack.append(('NUM', token))

        return tempo_stack
            
    def parse(self, ents):
        stck = self.get_stack(ents)
        tempo_expr = []
        parsed = []
        mode = ""
        for tp, vl in stck:
            if tp == "MONTH" and not tempo_expr:
                mode = "MONTH"
                tempo_expr.append(vl)
            elif tp == "MONTH" and mode == "MONTH":
                tempo_expr.append(vl)
            elif tp == "NUM" and mode == "MONTH":
                #create interval or month and empty expr
                for t in tempo_expr:
                    parsed.append(dateparser.parse("01 de %s %s" % (t, vl)))
                tempo_expr = []
                mode = ""


            elif tp == "NUM" and not tempo_expr:
                mode = "NUM"
                if int(vl) > 31:
                    if len(parsed):
                        try:
                            parsed[-1] = parsed[-1].replace(year=int(vl))
                        except:
                            pass
                    else:
                        #coming from num month num
                        tempo_expr.append(vl)
                else:
                    tempo_expr.append(vl)

            elif tp == "NUM" and mode == "NUM":
                # it's an year
                if int(vl) > 31:
                    if len(parsed):
                        try:
                            parsed[-1] = parsed[-1].replace(year=vl)
                        except:
                            pass
                    else:
                        #coming from num month num
                        tempo_expr.append(vl)
                else:
                    tempo_expr.append(vl)
                    #try to make date?
                if len(tempo_expr) == 2:
                    parsed.append(dateparser.parse("%s/%s" % (tempo_expr[0],tempo_expr[1])))
                    tempo_expr = []
                    mode = ""
                elif len(tempo_expr) == 3:
                    parsed.append(dateparser.parse("%s/%s/%s" % (tempo_expr[0],tempo_expr[1],tempo_expr[2])))
                    tempo_expr = []
                    mode = ""

            elif tp == "MONTH" and mode == "NUM":
                try:
                    m = datetime.datetime.strptime(vl, "%B").month
                except:
                    try:
                        m = datetime.datetime.strptime(vl, "%b").month
                    except:
                        m = 1
                tempo_expr.append(m)

        return parsed

class CNPJParser(ServusParser):
    def __init__(self):
        pass

    def parse(self, ents):
        return [re.sub(r'\D','',e) for e in ents]

class CPFParser(ServusParser):
    def __init__(self):
        pass

    def parse(self, ents):
        return [re.sub(r'\D','',e) for e in ents]

class OrgaoParser(ServusParser):
    def __init__(self):
        load_dotenv()
        self.orgaos_strs = []
        with open(os.getenv('ORGAOS_CSV_PATH'), 'r') as fp:
            for l in fp.readlines():
                self.orgaos_strs.append(tuple([x.strip() for x in l.split(",")]))

        self.orgaos_dict = dict(self.orgaos_strs)

        self.orgao_names, self.orgao_cods = zip(*self.orgaos_strs)
        
    def parse(self, ents):
        new_ents = []
        for e in ents:
            orgao, score = process.extractOne(e.upper(), self.orgao_names, scorer=fuzz.token_set_ratio)
            if score > 50:
                new_ents.append(orgao)
        return [int(self.orgaos_dict[e]) for e in new_ents]

        
class ControleExternoParser(ServusParser):
    def __init__(self):
        self.loader_dict = {
            'Empenho': EmpenhoLoader,
        }

    def parse(self, ents):
        loaders = []
        for e in ents:
            loader, score = process.extractOne(e.upper(), self.loader_dict.keys(), scorer=fuzz.token_set_ratio)
            if score > 50:
                loaders.append(self.loader_dict[loader])

        return loaders
        

