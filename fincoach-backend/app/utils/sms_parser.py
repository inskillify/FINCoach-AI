"""UPI SMS Parser for Indian Banks"""
import re
from typing import Optional, Dict
from datetime import datetime

class SMSParser:
    """Parse UPI transaction SMS from Indian banks"""
    
    # Bank patterns
    BANK_PATTERNS = {
        'HDFC': r'HDFC Bank|HDFC',
        'ICICI': r'ICICI Bank|ICICI',
        'SBI': r'State Bank|SBI',
        'Axis': r'Axis Bank|Axis',
        'Kotak': r'Kotak Bank|Kotak'
    }
    
    @staticmethod
    def parse_upi_sms(sms_text: str) -> Optional[Dict]:
        """
        Parse UPI transaction SMS
        
        Returns:
            Dict with transaction details or None if parsing fails
        """
        try:
            # Extract amount
            amount_match = re.search(r'Rs\.?\s*([0-9,]+(?:\.[0-9]{2})?)', sms_text)
            if not amount_match:
                return None
            
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Determine transaction type
            transaction_type = 'expense'
            if any(word in sms_text.lower() for word in ['credited', 'received', 'deposited']):
                transaction_type = 'income'
            
            # Extract description/merchant
            description = sms_text[:100]  # First 100 chars as description
            
            # Identify bank
            bank = 'Unknown'
            for bank_name, pattern in SMSParser.BANK_PATTERNS.items():
                if re.search(pattern, sms_text, re.IGNORECASE):
                    bank = bank_name
                    break
            
            return {
                'amount': amount,
                'type': transaction_type,
                'description': description,
                'bank': bank,
                'transaction_date': datetime.utcnow(),
                'category': 'other'
            }
        except Exception as e:
            print(f"Error parsing SMS: {e}")
            return None
    
    @staticmethod
    def categorize_transaction(description: str, amount: float) -> str:
        """Categorize transaction based on description"""
        description_lower = description.lower()
        
        categories = {
            'food': ['restaurant', 'cafe', 'food', 'pizza', 'burger', 'swiggy', 'zomato'],
            'transport': ['uber', 'ola', 'taxi', 'fuel', 'petrol', 'gas', 'parking'],
            'utilities': ['electricity', 'water', 'internet', 'phone', 'bill'],
            'entertainment': ['movie', 'cinema', 'game', 'spotify', 'netflix'],
            'shopping': ['amazon', 'flipkart', 'mall', 'store', 'shop'],
            'health': ['hospital', 'doctor', 'medicine', 'pharmacy', 'health'],
            'education': ['school', 'college', 'course', 'book', 'education'],
            'salary': ['salary', 'payment', 'transfer'],
            'investment': ['investment', 'mutual', 'stock', 'crypto'],
            'savings': ['savings', 'deposit', 'transfer']
        }
        
        for category, keywords in categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'other'
