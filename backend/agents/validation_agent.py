from database import get_product_by_name, get_all_products_for_prompt

class ValidationAgent:
    """
    Agent 2: Database Validation Bridge
    Non-AI, logic-driven component that validates extracted data against the database.
    Queries Supabase PostgreSQL for each item and applies business logic.
    """
    
    def __init__(self):
        pass
    
    def validate_order(self, raw_extraction_data):
        """
        Main validation function that takes raw extraction data and validates against database.
        
        Args:
            raw_extraction_data (dict): Raw JSON from Agent 1 containing items, delivery_preference, customer_notes
            
        Returns:
            dict: Validated order with validated_items and issues
        """
        print(f"🔍 VALIDATION AGENT: Starting validation with data: {raw_extraction_data}")
        
        # Initialize output structure
        validated_order = {
            "validated_items": [],
            "issues": [],
            "delivery_preference": raw_extraction_data.get("delivery_preference", ""),
            "customer_notes": raw_extraction_data.get("customer_notes", "")
        }
        
        # Get items from raw extraction data
        items = raw_extraction_data.get("items", [])
        print(f"🔍 VALIDATION AGENT: Processing {len(items)} items")
        
        # Debug: Get all available products to see what's in the database
        try:
            all_products = get_all_products_for_prompt()
            print(f"🔍 VALIDATION AGENT: Available products in database: {list(all_products.keys())[:10]}... (total: {len(all_products)})")
        except Exception as e:
            print(f"❌ VALIDATION AGENT: Error fetching all products: {e}")
            all_products = {}
        
        # Core validation loop
        for i, item in enumerate(items):
            print(f"🔍 VALIDATION AGENT: Processing item {i+1}: {item}")
            
            try:
                # Extract data from the item
                product_name_mentioned = item.get("product_name_mentioned", "")
                quantity_mentioned = item.get("quantity_mentioned", 0)
                item_description = item.get("item_description", "")
                
                print(f"🔍 VALIDATION AGENT: Looking for product name '{product_name_mentioned}' with quantity {quantity_mentioned}")
                
                # Query the database for this item by name
                product_data = get_product_by_name(product_name_mentioned)
                
                if product_data is None:
                    print(f"❌ VALIDATION AGENT: Product '{product_name_mentioned}' NOT FOUND in database")
                    # Product does not exist
                    validated_order["issues"].append({
                        "item_mentioned": product_name_mentioned,
                        "issue_type": "PRODUCT_NOT_FOUND",
                        "message": f"Product '{product_name_mentioned}' does not exist in our catalog",
                        "suggestion": f"Available products: {', '.join([p['name'] for p in list(all_products.values())[:3]])}...",
                        "item_description": item_description
                    })
                    
                else:
                    print(f"✅ VALIDATION AGENT: Product '{product_name_mentioned}' FOUND: {product_data}")
                    # Product exists - check business rules
                    if quantity_mentioned < product_data['min_order_qty']:
                        print(f"⚠️ VALIDATION AGENT: MOQ not met for {product_data['sku']}")
                        # Minimum order quantity not met
                        validated_order["issues"].append({
                            "item_mentioned": product_name_mentioned,
                            "issue_type": "MOQ_NOT_MET",
                            "message": f"Requested quantity ({quantity_mentioned}) is below minimum order quantity ({product_data['min_order_qty']})",
                            "suggestion": f"Minimum order quantity for {product_data['name']} is {product_data['min_order_qty']}",
                            "item_description": item_description
                        })
                        
                    elif quantity_mentioned > product_data['inventory']:
                        print(f"⚠️ VALIDATION AGENT: Insufficient inventory for {product_data['sku']}")
                        # Insufficient inventory
                        validated_order["issues"].append({
                            "item_mentioned": product_name_mentioned,
                            "issue_type": "INSUFFICIENT_INVENTORY",
                            "message": f"Requested quantity ({quantity_mentioned}) exceeds available inventory ({product_data['inventory']})",
                            "suggestion": f"Maximum available quantity for {product_data['name']} is {product_data['inventory']}",
                            "item_description": item_description
                        })
                        
                    else:
                        print(f"✅ VALIDATION AGENT: Item {product_data['sku']} is VALID")
                        # Item is fully valid
                        validated_order["validated_items"].append({
                            "sku": product_data['sku'],
                            "name": product_data['name'],
                            "quantity": quantity_mentioned,
                            "price": product_data['price'],
                            "item_description": item_description
                        })
                        
            except Exception as e:
                print(f"❌ VALIDATION AGENT: Error validating item '{item.get('product_name_mentioned', 'Unknown')}': {e}")
                # Database error during validation
                validated_order["issues"].append({
                    "item_mentioned": item.get("product_name_mentioned", "Unknown"),
                    "issue_type": "VALIDATION_ERROR",
                    "message": f"Error validating item: {str(e)}",
                    "suggestion": "Please try again or contact support",
                    "item_description": item.get("item_description", "")
                })
        
        print(f"🔍 VALIDATION AGENT: Validation complete. Validated: {len(validated_order['validated_items'])}, Issues: {len(validated_order['issues'])}")
        return validated_order 