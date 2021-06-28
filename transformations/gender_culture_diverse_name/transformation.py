import numpy as np
import spacy
from checklist.perturb import Perturb

from interfaces.SentenceOperation import SentenceOperation
from tasks.TaskTypes import TaskType

import os
import re
import json
import random
import itertools
from checklist.perturb import process_ret

class change_gender_culture_diverse_name:
    def __init__(self, data_path, retain_gender=False, retain_culture=False) -> None:

        self.retain_gender = retain_gender
        self.retain_culture = retain_culture
        with open(data_path, 'r') as f:
            self.names = json.load(f)
        self.countries = list(self.names.keys())
        self.genders = ['M', 'F']

        self.name_all = set()
        self.name2gender = {}
        self.name2country = {}

        for country in self.names.keys():
            for gender in ['M', 'F']:
                for name in self.names[country][gender]:
                    self.name_all.add(name)

                    if name not in self.name2gender.keys():
                        self.name2gender[name] = set([gender])
                    else:
                        self.name2gender[name].add(gender)
                    
                    if name not in self.name2country.keys():
                        self.name2country[name] = set([country])
                    else:
                        self.name2country[name].add(country)

    def apply(self, doc, meta=False, n=10, seed=None):
        """Replace names with another name, considering gender and cultural diversity

        Parameters
        ----------
        doc : spacy.token.Doc
            input
        meta : bool
            if True, will return list of (orig_name, new_name) as meta
        n : int
            number of names to replace original names with
        seed : int
            random seed

        Returns
        -------
        list(str)
            if meta=True, returns (list(str), list(tuple))
            Strings with names replaced.

        """

        if seed is not None:
            np.random.seed(seed)
        ents = [x.text for x in doc.ents if np.all([a.ent_type_ == 'PERSON' for a in x])]
        ret = []
        ret_m = []
        for x in ents:
            name = x.split()[0]
            capito = name[0].isupper() # pun intended, hint: Italian
            name = name.capitalize()
            if name in self.name_all:
                gender = self.name2gender[name]
                country = self.name2country[name]
                if self.retain_gender:
                    gender_choose_from = gender
                else:
                    gender_choose_from = self.genders
                if self.retain_culture:
                    country_choose_from = country
                else:
                    country_choose_from = self.countries
            
            new_countries = random.choices(country_choose_from, k=n)
            new_genders = random.choices(gender_choose_from, k=n)
            new_names = [random.choice(self.names[c][n]) for c,n in zip(new_countries, new_genders)]
            if not capito:
                new_names = [n.lower() for n in new_names]
            
            for new_name in new_names:
                ret.append(re.sub(r'\b%s\b' % re.escape(name), new_name, doc.text))
                ret_m.append((name, new_name))
        
        return process_ret(ret, ret_m=ret_m, n=n, meta=meta)
                


class gender_culture_diverse_name(SentenceOperation):
    tasks = [TaskType.TEXT_CLASSIFICATION, TaskType.TEXT_TO_TEXT_GENERATION]
    languages = ["en"]

    def __init__(self, n=1, seed=0, max_output=1, retain_gender=False, retain_culture=False, data_path=None):
        super().__init__(seed)
        self.nlp = spacy.load("en_core_web_sm")
        self.n = n
        self.max_output = max_output

        if data_path is None:
            self.changer = change_gender_culture_diverse_name(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json'),
                retain_gender, 
                retain_culture
            )
        else:
            self.changer = change_gender_culture_diverse_name(
                data_path,
                retain_gender, 
                retain_culture
            )

    def generate(self, sentence: str):
        np.random.seed(self.seed)
        perturbed = Perturb.perturb(
            [self.nlp(sentence)], 
            self.changer.apply, 
            nsamples=1
        )
        perturbed_texts = (
            perturbed.data[0][1 : self.max_output + 1]
            if len(perturbed.data) > 0
            else [sentence]
        )
        return perturbed_texts


test = gender_culture_diverse_name()
sentence = 'Rachel Green, a sheltered but friendly woman, flees her wedding day and wealthy yet unfulfilling life.'
p = test.generate(sentence)
print(p[0])