import unittest

import sys, os

path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, path + '/../')

from parsers import TempoParser

class TestParserMethods(unittest.TestCase):
    
    @unittest.skip
    def test_num(self):
        t = TempoParser()
        tempo = ['01', '/', '01', '/ 2019', '31', '/', '12', '/ 2020']
        stc = t.get_stack(tempo)
        prs = t.parse(tempo)
        print(stc)
        print(prs)
        assert(len(stc) > 1)

    def test_alpha(self):
        t = TempoParser()
        tempo = ['janeiro a', 'março de 2018', '01', '/', '01', '/', '2019', '31', '/', '12 / 2020', '1', '.', '1', '.', '2011', '01', '-', '01', '-', '2010']
        #tempo2 = ['janeiro de 2015 a março a 2020']
        #tempo3 = ['01 de janeiro de 2018 a 22 de junho de 2019']

        prs = t.parse(tempo)
        #prs2 = t.parse(tempo2)
        #prs3 = t.parse(tempo3)
        
        print(prs)
        #print(prs2)
        #print(prs3)
        