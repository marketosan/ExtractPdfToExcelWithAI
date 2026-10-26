from enum import Enum


class ExtractionApproach(Enum):
    RULE_BASED = ("Rule-based", None)
    AI_MODEL = ("AI model", "llama3.2:3b")
    AI_EXTENDED_MODEL = ("AI extended model", "llama3.1:8b")

    def __init__(self, label, model_name):
        self.label = label
        self.model_name = model_name
