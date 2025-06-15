import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from database import get_all_products_for_prompt, get_product_by_sku

# Load environment variables from .env file
load_dotenv()

# --- Application Setup ---
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) for our frontend
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# --- Configure Gemini API ---
try:
    api_key = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
except KeyError:
    print("ERROR: GEMINI_API_KEY not found in .env file.")
    exit()
except Exception as e:
    print(f"ERROR configuring Gemini API: {e}")
    exit()

# --- Prompt Engineering ---
def create_prompt(email_content, catalog):
    # Convert the catalog to a string for the prompt
    catalog_str = json.dumps(catalog, indent=2)

    return f"""
    You are an expert order processing assistant. Your task is to extract order details from an unstructured email, validate them against the provided product catalog, and generate a structured JSON output.

    **Product Catalog for Validation:**
    ```json
    {catalog_str}
    ```

    **Email Content:**
    ---
    {email_content}
    ---

    **Instructions:**
    1.  **Extract Items:** Identify all requested Stock Keeping Units (SKUs) and their quantities from the email.
    2.  **Extract Delivery Info:** Identify any notes about delivery preferences or deadlines.
    3.  **Extract Customer Notes:** Capture any other relevant customer comments or questions.
    4.  **Output JSON:** Structure your findings into a single JSON object. Do not add any text before or after the JSON object.
    5.  **Handle Issues:**
        *   If a SKU from the email does not exist in the catalog, add it to an `issues` array in the JSON. In the `suggestion` field for that issue, suggest a valid SKU from the catalog that seems like a close match (e.g., different size or color of the same item type).
        *   If the requested quantity for a valid SKU is below its `min_order_qty`, add it to the `issues` array. In the `suggestion`, state the minimum required quantity.
        *   If the requested quantity for a valid SKU exceeds the `inventory`, add it to the `issues` array. In the `suggestion`, state the available stock.
        *   If an item is valid (exists, meets MOQ, in stock), add it to the `validated_items` array.

    **JSON Output Format:**
    ```json
    {{
      "validated_items": [
        {{
          "sku": "string",
          "quantity": "integer",
          "name": "string"
        }}
      ],
      "issues": [
        {{
          "item_mentioned": "string (what the user wrote)",
          "issue_type": "SKU_NOT_FOUND | MOQ_NOT_MET | INSUFFICIENT_INVENTORY",
          "message": "string (a clear description of the problem)",
          "suggestion": "string (a helpful suggestion to resolve the issue)"
        }}
      ],
      "delivery_preference": "string",
      "customer_notes": "string"
    }}
    ```
    """

def perform_server_side_validation(validated_items):
    """
    Performs definitive server-side validation of items returned by the AI.
    Returns a tuple of (final_validated_items, additional_issues)
    """
    final_validated_items = []
    additional_issues = []
    
    for item in validated_items:
        try:
            # Fetch latest product data from database
            product = get_product_by_sku(item['sku'])
            
            if not product:
                # Product no longer exists
                additional_issues.append({
                    "item_mentioned": item['sku'],
                    "issue_type": "SKU_NOT_FOUND_ON_CONFIRM",
                    "message": f"Product {item['sku']} no longer exists in our catalog",
                    "suggestion": "Please check the product catalog for available items"
                })
                continue
            
            # Check inventory
            if item['quantity'] > product['inventory']:
                additional_issues.append({
                    "item_mentioned": item['sku'],
                    "issue_type": "INSUFFICIENT_INVENTORY_ON_CONFIRM",
                    "message": f"Insufficient inventory for {item['sku']}. Requested: {item['quantity']}, Available: {product['inventory']}",
                    "suggestion": f"Maximum available quantity: {product['inventory']}"
                })
                continue
            
            # Check minimum order quantity
            if item['quantity'] < product['min_order_qty']:
                additional_issues.append({
                    "item_mentioned": item['sku'],
                    "issue_type": "MOQ_NOT_MET_ON_CONFIRM",
                    "message": f"Minimum order quantity not met for {item['sku']}. Requested: {item['quantity']}, Required: {product['min_order_qty']}",
                    "suggestion": f"Minimum order quantity: {product['min_order_qty']}"
                })
                continue
            
            # Item passes all validations
            final_validated_items.append(item)
            
        except Exception as e:
            # Database error during validation
            additional_issues.append({
                "item_mentioned": item['sku'],
                "issue_type": "VALIDATION_ERROR",
                "message": f"Error validating {item['sku']}: {str(e)}",
                "suggestion": "Please try again or contact support"
            })
    
    return final_validated_items, additional_issues

# --- API Endpoint ---
@app.route("/api/extract-order", methods=["POST"])
def extract_order_details():
    try:
        data = request.get_json()
        
        if not data or "email_content" not in data:
            return jsonify({"error": "Missing 'email_content' in request"}), 400
        
        email_content = data["email_content"]
        
        # Fetch live product catalog from database
        product_catalog = get_all_products_for_prompt()
        
        prompt = create_prompt(email_content, product_catalog)
        
        response = model.generate_content(prompt)
        
        # Clean up the response to get pure JSON
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        order_data = json.loads(cleaned_response)
        
        # Perform server-side validation
        final_validated_items, additional_issues = perform_server_side_validation(
            order_data.get('validated_items', [])
        )
        
        # Update the response with final validation results
        order_data['validated_items'] = final_validated_items
        order_data['issues'].extend(additional_issues)
        
        return jsonify(order_data), 200
        
    except json.JSONDecodeError as json_error:
        return jsonify({"error": "Invalid JSON response from AI model", "details": str(json_error)}), 500
        
    except Exception as e:
        return jsonify({"error": "Failed to process request", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)