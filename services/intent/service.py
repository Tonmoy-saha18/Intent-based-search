from transformers import pipeline
from typing import Dict, Any
import numpy as np
import os


class IntentClassifier:
    def __init__(self):
        model_path = os.getenv("INTENT_MODEL_PATH", "distilbert-base-uncased")
        self.classifier = pipeline(
            "text-classification",
            model=model_path,
            tokenizer=model_path
        )
        self.entity_recognizer = pipeline(
            "ner",
            model=os.getenv("NER_MODEL_PATH", "dslim/bert-base-NER")
        )

    def classify(self, query: str) -> Dict[str, Any]:
        # Classify intent
        intent_result = self.classifier(query)

        # Extract entities
        entities = self._extract_entities(query)

        return {
            "intent": intent_result[0]["label"],
            "confidence": intent_result[0]["score"],
            "entities": entities
        }

    def _extract_entities(self, query: str) -> Dict[str, Any]:
        ner_results = self.entity_recognizer(query)
        entities = {
            "price_range": {"min": None, "max": None},
            "demographics": [],
            "features": []
        }

        # Process NER results
        for entity in ner_results:
            if entity["entity"] == "MONEY":
                amount = float(entity["word"].replace("$", ""))
                if "max" not in entities["price_range"] or amount > entities["price_range"]["max"]:
                    entities["price_range"]["max"] = amount
            elif entity["entity"] == "AGE":
                entities["demographics"].append(entity["word"])
            elif entity["entity"] == "FEATURE":
                entities["features"].append(entity["word"])

        return entities


# Singleton instance
intent_classifier = IntentClassifier()


def classify_intent(query: str):
    return intent_classifier.classify(query)