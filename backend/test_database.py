#!/usr/bin/env python3
"""
Test script to verify database connection and product data.
"""

import os
from dotenv import load_dotenv
from database import get_all_products_for_prompt, get_product_by_sku, get_product_by_name

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test the database connection and product data."""
    print("🔍 Testing database connection and product data...")
    print()
    
    try:
        # Test 1: Get all products
        print("📊 Test 1: Fetching all products...")
        all_products = get_all_products_for_prompt()
        print(f"✅ Found {len(all_products)} products in database")
        
        if len(all_products) > 0:
            print("📋 First 5 products:")
            for i, (sku, product) in enumerate(list(all_products.items())[:5]):
                print(f"   {i+1}. {sku}: {product['name']} - ${product['price']} (MOQ: {product['min_order_qty']}, Stock: {product['inventory']})")
        print()
        
        # Test 2: Test specific SKUs from sample email
        test_skus = ["DSK-0001", "DSK-0002", "DSK-0003", "DSK-0004"]
        print("🔍 Test 2: Testing specific SKUs from sample email...")
        
        for sku in test_skus:
            product = get_product_by_sku(sku)
            if product:
                print(f"✅ {sku}: FOUND - {product['name']} - ${product['price']} (MOQ: {product['min_order_qty']}, Stock: {product['inventory']})")
            else:
                print(f"❌ {sku}: NOT FOUND")
        print()
        
        # Test 3: Test product name search (new functionality)
        test_product_names = ["TRÄNHOLM 19", "NORDMARK 476", "VIKTSTA 642", "SNÖRSUND 966"]
        print("🔍 Test 3: Testing product name search...")
        
        for product_name in test_product_names:
            product = get_product_by_name(product_name)
            if product:
                print(f"✅ '{product_name}': FOUND - {product['name']} (SKU: {product['sku']}) - ${product['price']} (MOQ: {product['min_order_qty']}, Stock: {product['inventory']})")
            else:
                print(f"❌ '{product_name}': NOT FOUND")
        print()
        
        # Test 4: Test some random product names
        print("🔍 Test 4: Testing some random product names...")
        if all_products:
            sample_products = list(all_products.values())[:3]
            for product in sample_products:
                # Extract part of the name for testing
                name_part = product['name'].split()[1] if len(product['name'].split()) > 1 else product['name']
                found_product = get_product_by_name(name_part)
                if found_product:
                    print(f"✅ '{name_part}': FOUND - {found_product['name']} (SKU: {found_product['sku']})")
                else:
                    print(f"❌ '{name_part}': NOT FOUND")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection() 