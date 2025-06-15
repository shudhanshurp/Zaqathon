import json
import google.generativeai as genai
from database import get_all_products_for_prompt

class ExtractionAgent:
    """
    Agent 1: Extractor
    Uses AI to extract order details from unstructured email content.
    Returns raw JSON data that will be validated by Agent 2.
    """
    
    def __init__(self, model):
        self.model = model
    
    def create_prompt(self, email_content, catalog):
        """
        Creates the prompt for the AI to extract order details.
        """
        catalog_str = json.dumps(catalog, indent=2)
        
        return f"""
        You are an expert order processing assistant. Your task is to extract order details from an unstructured email and generate a structured JSON output.

        **Product Catalog for Reference:**
        ```json
        {catalog_str}
        ```

        **Email Content:**
        ---
        {email_content}
        ---

        **Instructions:**
        1. **Extract Items:** Identify all requested items and their quantities from the email.
        2. **Extract Delivery Info:** Identify any notes about delivery preferences or deadlines.
        3. **Extract Customer Notes:** Capture any other relevant customer comments or questions.
        4. **Output JSON:** Structure your findings into a single JSON object.

        **JSON Output Format:**
        ```json
        {{
          "items": [
            {{
              "product_name_mentioned": "string (the product name mentioned in the email)",
              "quantity_mentioned": "integer (the quantity requested)",
              "item_description": "string (how the item was described in the email)"
            }}
          ],
          "delivery_preference": "string",
          "customer_notes": "string"
        }}
        ```

        **Important:** 
        - Extract the product names as mentioned in the email (e.g., "desk TRÄNHOLM 19", "black hoodies")
        - Do not validate against the catalog - just extract what the customer mentioned
        - Focus on identifying what they want, not whether it's available or valid
        - If a SKU is mentioned, include it in the item_description but use the product name for product_name_mentioned
        """
    
    def extract_details(self, email_content):
        """
        Main extraction function that processes email content and returns raw JSON data.
        """
        try:
            print(f"🔍 EXTRACTION AGENT: Processing email content: {email_content[:200]}...")
            
            # Fetch product catalog for context
            product_catalog = get_all_products_for_prompt()
            print(f"🔍 EXTRACTION AGENT: Fetched {len(product_catalog)} products for context")
            
            # Create prompt
            prompt = self.create_prompt(email_content, product_catalog)
            
            # Get AI response
            print("🔍 EXTRACTION AGENT: Calling Gemini AI...")
            response = self.model.generate_content(prompt)
            
            # Clean and parse response
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            print(f"🔍 EXTRACTION AGENT: Raw AI response: {cleaned_response}")
            
            raw_extraction_data = json.loads(cleaned_response)
            print(f"🔍 EXTRACTION AGENT: Parsed extraction data: {raw_extraction_data}")
            
            return raw_extraction_data
            
        except Exception as e:
            print(f"❌ EXTRACTION AGENT: Extraction failed: {e}")
            raise Exception(f"Extraction failed: {str(e)}") 