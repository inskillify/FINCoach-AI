"""Transaction Categorizer - ML module for automatic categorization"""
from typing import Dict, List

class TransactionCategorizer:
    """Machine Learning module for automatic transaction categorization"""
    
    # Keywords mapping for categories
    CATEGORY_KEYWORDS = {
        "food": ["restaurant", "cafe", "pizza", "burger", "food", "grocery", "supermarket", "market", "bakery", "diner", "bistro", "eatery"],
        "transportation": ["uber", "taxi", "bus", "train", "metro", "fuel", "petrol", "gas", "parking", "toll", "auto", "bike"],
        "entertainment": ["movie", "cinema", "theater", "game", "gaming", "concert", "show", "netflix", "spotify", "disney", "hulu"],
        "utilities": ["electricity", "water", "gas", "internet", "phone", "mobile", "broadband", "wifi", "power"],
        "shopping": ["mall", "store", "shop", "amazon", "flipkart", "ebay", "retail", "clothing", "apparel", "fashion"],
        "health": ["hospital", "doctor", "pharmacy", "medicine", "clinic", "health", "medical", "dental", "gym", "fitness"],
        "education": ["school", "college", "university", "course", "training", "tuition", "book", "education"],
        "finance": ["bank", "loan", "credit", "insurance", "investment", "stock", "mutual", "fund"],
        "personal": ["salon", "spa", "haircut", "beauty", "cosmetics", "personal care"],
        "rent": ["rent", "landlord", "lease", "housing", "apartment", "flat"],
        "salary": ["salary", "wage", "paycheck", "income", "bonus", "commission"],
        "investment": ["investment", "stock", "mutual fund", "crypto", "bitcoin", "ethereum"]
    }
    
    def categorize_transaction(self, description: str, amount: float = None) -> Dict:
        """Categorize a transaction based on description"""
        description_lower = description.lower()
        
        # Find matching category
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return {
                        "status": "success",
                        "category": category,
                        "confidence": 0.85,
                        "matched_keyword": keyword
                    }
        
        # Default category if no match
        return {
            "status": "success",
            "category": "other",
            "confidence": 0.0,
            "matched_keyword": None
        }
    
    def batch_categorize(self, transactions: List[Dict]) -> List[Dict]:
        """Categorize multiple transactions"""
        results = []
        for transaction in transactions:
            description = transaction.get("description", "")
            amount = transaction.get("amount")
            
            categorization = self.categorize_transaction(description, amount)
            categorization["transaction_id"] = transaction.get("id")
            results.append(categorization)
        
        return results
    
    def get_category_suggestions(self, description: str) -> List[Dict]:
        """Get multiple category suggestions for a transaction"""
        description_lower = description.lower()
        suggestions = []
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            confidence = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in description_lower:
                    confidence += 0.1
                    matched_keywords.append(keyword)
            
            if confidence > 0:
                suggestions.append({
                    "category": category,
                    "confidence": min(confidence, 1.0),
                    "matched_keywords": matched_keywords
                })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def add_custom_category_rule(self, keyword: str, category: str) -> Dict:
        """Add custom categorization rule"""
        if category not in self.CATEGORY_KEYWORDS:
            self.CATEGORY_KEYWORDS[category] = []
        
        if keyword not in self.CATEGORY_KEYWORDS[category]:
            self.CATEGORY_KEYWORDS[category].append(keyword.lower())
        
        return {
            "status": "success",
            "message": f"Added '{keyword}' to '{category}' category"
        }
