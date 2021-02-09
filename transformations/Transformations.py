from transformations.BackTranslation import BackTranslation
from transformations.ButterFingersPerturbation import ButterFingersPerturbation
from transformations.ChangeNamedEntities import ChangeNamedEntities
from transformations.SentenceTransformation import SentenceTransformation
from transformations.WithoutPunctuation import WithoutPunctuation
from transformations.CorefSwap import CorefSwap


class TransformationsList(SentenceTransformation):

    def __init__(self):
        transformations = []
        transformations.append(ButterFingersPerturbation())
        transformations.append(WithoutPunctuation())
        transformations.append(ChangeNamedEntities())
        transformations.append(BackTranslation())
        transformations.append(CorefSwap())
        self.transformations = transformations

    def generate(self, sentence: str):
        print(f"Original Input : {sentence}")
        generations = {"Original": sentence}
        for transformation in self.transformations:
            generations[transformation.name()] = transformation.generate(sentence)
        return generations
