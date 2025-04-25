from typing import List, Dict, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ProductRanker:
    def __init__(self):
        self.weights = {
            "similarity": 0.7,
            "price": 0.15,
            "popularity": 0.1,
            "business_rules": 0.05
        }

    def rerank(
            self,
            products: List[Dict],
            intent: Optional[Dict] = None,
            user_id: Optional[str] = None
    ) -> List[Dict]:
        try:
            if not products:
                return []

            # Apply scoring
            for product in products:
                product["_score"] = self._calculate_score(product, intent)

            # Sort by score
            ranked = sorted(products, key=lambda x: x["_score"], reverse=True)

            # Apply business rules (e.g., sponsored products)
            ranked = self._apply_business_rules(ranked)

            return ranked
        except Exception as e:
            logger.error(f"Ranking failed: {str(e)}")
            return products

    def _calculate_score(self, product: Dict, intent: Dict) -> float:
        base_score = product.get("similarity_score", 0)
        price_score = self._calculate_price_score(product, intent)
        popularity_score = product.get("rating", 0) / 5  # Normalize to 0-1

        return (
                self.weights["similarity"] * base_score +
                self.weights["price"] * price_score +
                self.weights["popularity"] * popularity_score
        )

    def _calculate_price_score(self, product: Dict, intent: Dict) -> float:
        if not intent or "price_range" not in intent.get("entities", {}):
            return 0.5  # Neutral score

        price = product.get("price", 0)
        max_price = intent["entities"]["price_range"].get("max")

        if max_price and price > max_price:
            return 0.1  # Penalty for exceeding max price
        return 1.0 - (0.9 * (price / max_price))  # Higher score for lower prices

    def _apply_business_rules(self, products: List[Dict]) -> List[Dict]:
        # Example: Boost sponsored products
        for product in products:
            if product.get("sponsored", False):
                product["_score"] *= 1.2
        return products


# Singleton instance
product_ranker = ProductRanker()


def rerank_results(products: List[Dict], intent: Dict, user_id: str = None):
    return product_ranker.rerank(products, intent, user_id)