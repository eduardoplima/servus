import torch, re, os
import numpy as np

from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import BertTokenizer, BertConfig

from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

from typing import List, Union

from dotenv import load_dotenv

nn_tags = ['B-CONTROLEEXTERNO',
'B-LOCAL',
'B-ORGANIZACAO',
'B-PESSOA',
'B-TEMPO',
'B-VALOR',
'I-CONTROLEEXTERNO',
'I-LOCAL',
'I-ORGANIZACAO',
'I-PESSOA',
'I-TEMPO',
'I-VALOR',
'O',
'PAD']

class EntitySource(object):
    def get_entities_dict(self, words:List[str], ents:List[str]) -> dict:
        ent_dict = {}
        for w, e in zip(words, ents):
            if e not in ent_dict.keys():
                ent_dict[e] = []
            ent_dict[e].append(w)
        return ent_dict

class NerNeuralNet(EntitySource):
    def __init__(self, tokenizer='neuralmind/bert-base-portuguese-cased'):
        load_dotenv()
        self.model = torch.load(os.getenv('MODEL_PATH'))
        self.tokenizer = BertTokenizer.from_pretrained(tokenizer, do_lower_case=False)

    def get_entities_lists(self, msg:str) -> Union[List, List]:
        tokenized_sentence = self.tokenizer.encode(msg)
        input_ids = torch.tensor([tokenized_sentence]).cuda()
        
        with torch.no_grad():
            output = self.model(input_ids)
        label_indices = np.argmax(output[0].to('cpu').numpy(), axis=2)
        
        tokens = self.tokenizer.convert_ids_to_tokens(input_ids.to('cpu').numpy()[0])
        new_tokens, new_labels = [], []
        for token, label_idx in zip(tokens, label_indices[0]):
            if token.startswith("##"):
                new_tokens[-1] = new_tokens[-1] + token[2:]
            else:
                new_labels.append(nn_tags[label_idx])
                new_tokens.append(token)
                
        zip_result = list(zip(new_labels, new_tokens))
        
        
        words = []
        ents = []
        for e in [r for r in zip_result if r[0] != 'O']:
            symb, t_ent = e[0].split('-')
            word = e[1]
            if symb == 'B':
                words.append(word)
                ents.append(t_ent)
            else:
                words[-1] += ' ' + word
            
        return words, ents
    
    def get_entities_dict(self, msg:str) -> dict:
        words, ents = self.get_entities_lists(msg)
        return super(NerNeuralNet, self).get_entities_dict(words, ents)


class NerRuleExtractor(EntitySource):
    def __init__(self):
        self.cpf_pattern = r'\b([0-9]{3}\.?[0-9]{3}\.?[0-9]{3}\-?[0-9]{2})\b'
        self.cnpj_pattern = r'\b([0-9]{2}\.?[0-9]{3}\.?[0-9]{3}\/?[0-9]{4}\-?[0-9]{2})\b'
        self.email_pattern = r'\b[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}\b'

    def get_entities_lists(self, msg:str) -> Union[List, List]:
        emails = re.findall(self.email_pattern, msg)
        cpfs = re.findall(self.cpf_pattern, msg)
        cnpjs = re.findall(self.cnpj_pattern, msg)

        words_ents = [(e,'EMAIL') for e in emails] + [(c,'CPF') for c in cpfs] + [(c,'CNPJ') for c in cnpjs]

        words = []
        ents = []
        for w,e in words_ents:
            words.append(w)
            ents.append(e)

        return words, ents

    def get_entities_dict(self, msg:str) -> dict:
        words, ents = self.get_entities_lists(msg)
        return super(NerRuleExtractor, self).get_entities_dict(words, ents)


class EntityExtractor(object):
    def __init__(self):        
        self.ner_nn = NerNeuralNet()
        self.ner_rule = NerRuleExtractor()

    def get_entities_dict(self, msg:str) -> dict:
        dict_nn = self.ner_nn.get_entities_dict(msg)
        dict_rule = self.ner_rule.get_entities_dict(msg)

        dict_nn.update(dict_rule)

        return dict_nn

    
    