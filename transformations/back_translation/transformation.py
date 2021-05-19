from interfaces.SentenceTransformation import SentenceTransformation
import torch
from tasks.TaskTypes import TaskType


class BackTranslation(SentenceTransformation):
    tasks = [TaskType.TEXT_CLASSIFICATION, TaskType.TEXT_TO_TEXT_GENERATION]
    locales = ["en"]

    def __init__(self):
        super().__init__()
        print("Starting to load English to German Translation Model:")
        self.en2de = torch.hub.load('pytorch/fairseq', 'transformer.wmt16.en-de', tokenizer='moses', bpe='subword_nmt')
        print("Completed loading English to German Translation Model.\n")
        print("Starting to load German to English Translation Model:")
        self.de2en = torch.hub.load('pytorch/fairseq', 'transformer.wmt19.de-en.single_model', tokenizer='moses',
                                    bpe='fastbpe')
        print("Completed loading German to English Translation Model.\n")

    def back_translate(self, en: str):
        try:
            de = self.en2de.translate(en)
            en_new = self.de2en.translate(de)
        except Exception:
            print("Returning Default due to Run Time Exception")
            en_new = en
        return en_new

    def generate(self, sentence: str):
        pertubed = self.back_translate(sentence)
        print(f"Perturbed Input from {self.name()} : {pertubed}")
        return pertubed
