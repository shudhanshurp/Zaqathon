import json
import google.generativeai as genai

class ResponseAgent:
    """
    Agent 3: Response Agent
    Generates customer-friendly responses based on validated order data.
    """
    
    def __init__(self, model):
        self.model = model
    
    def create_prompt(self, validated_order):
        """
        Creates the prompt for generating a customer response.
        """
        validated_items_str = json.dumps(validated_order.get("validated_items", []), indent=2)
        issues_str = json.dumps(validated_order.get("issues", []), indent=2)
        
        return f"""
        You are a professional customer service representative. Generate a friendly, helpful response to a customer's order request based on the validated order data.

        **Validated Order Data:**
        ```json
        {{
          "validated_items": {validated_items_str},
          "issues": {issues_str},
          "delivery_preference": "{validated_order.get('delivery_preference', '')}",
          "customer_notes": "{validated_order.get('customer_notes', '')}"
        }}
        ```

        **Instructions:**
        1. **Acknowledge the order** - Thank the customer for their order
        2. **Confirm valid items** - List all items that can be fulfilled with quantities and prices
        3. **Address issues** - Politely explain any problems and provide helpful suggestions
        4. **Delivery information** - Address any delivery preferences mentioned
        5. **Additional notes** - Respond to any customer questions or comments
        6. **Next steps** - Provide clear next steps (order confirmation, payment, etc.)

        **Tone:** Professional, friendly, helpful, and solution-oriented
        **Length:** 2-4 paragraphs
        **Format:** Plain text email response
        """
    
    def generate_customer_response(self, validated_order):
        """
        Generates a customer-friendly response based on validated order data.
        
        Args:
            validated_order (dict): Validated order data from Agent 2
            
        Returns:
            dict: Response with email content and order summary
        """
        try:
            # Create prompt
            prompt = self.create_prompt(validated_order)
            
            # Get AI response
            response = self.model.generate_content(prompt)
            
            # Return structured response
            return {
                "email_response": response.text.strip(),
                "order_summary": {
                    "validated_items": validated_order.get("validated_items", []),
                    "issues": validated_order.get("issues", []),
                    "delivery_preference": validated_order.get("delivery_preference", ""),
                    "customer_notes": validated_order.get("customer_notes", "")
                }
            }
            
        except Exception as e:
            raise Exception(f"Response generation failed: {str(e)}") 