#!/usr/bin/env python3
"""
Database setup script for the three-agent pipeline.
This script creates the products table and populates it with sample data.
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_products_table():
    """Create the products table if it doesn't exist."""
    try:
        conn = psycopg2.connect(
            host=os.environ.get("HOST"),
            database=os.environ.get("DBNAME"),
            user=os.environ.get("USER"),
            password=os.environ.get("PASSWORD"),
            port=os.environ.get("PORT", "5432")
        )
        
        with conn.cursor() as cur:
            # Create products table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                sku VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                min_order_qty INTEGER NOT NULL,
                inventory INTEGER NOT NULL,
                description TEXT
            );
            """
            cur.execute(create_table_query)
            conn.commit()
            print("✅ Products table created successfully!")
            
    except Exception as e:
        print(f"❌ Error creating table: {e}")
    finally:
        if conn:
            conn.close()

def check_database_connection():
    """Test the database connection."""
    try:
        conn = psycopg2.connect(
            host=os.environ.get("HOST"),
            database=os.environ.get("DBNAME"),
            user=os.environ.get("USER"),
            password=os.environ.get("PASSWORD"),
            port=os.environ.get("PORT", "5432")
        )
        print("✅ Database connection successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_products_data():
    """Check if products data exists in the database."""
    try:
        conn = psycopg2.connect(
            host=os.environ.get("HOST"),
            database=os.environ.get("DBNAME"),
            user=os.environ.get("USER"),
            password=os.environ.get("PASSWORD"),
            port=os.environ.get("PORT", "5432")
        )
        
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM products;")
            count = cur.fetchone()[0]
            print(f"📊 Found {count} products in the database")
            
            if count > 0:
                # Show some sample products
                cur.execute("SELECT sku, name, price FROM products LIMIT 5;")
                products = cur.fetchall()
                print("📋 Sample products:")
                for sku, name, price in products:
                    print(f"   - {sku}: {name} (${price})")
            
        conn.close()
        return count > 0
        
    except Exception as e:
        print(f"❌ Error checking products: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up database for three-agent pipeline...")
    print()
    
    # Check environment variables
    required_vars = ["HOST", "DBNAME", "USER", "PASSWORD"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set up your .env file with the required database credentials.")
        exit(1)
    
    # Test connection
    if not check_database_connection():
        exit(1)
    
    # Create table
    create_products_table()
    
    # Check if data exists
    has_data = check_products_data()
    
    if not has_data:
        print()
        print("📝 No products found in database.")
        print("To populate the database with sample data, run:")
        print("   python product_data_insert.py")
        print()
        print("Or manually insert some test products using SQL:")
        print("""
        INSERT INTO products (sku, name, price, min_order_qty, inventory) VALUES
        ('DSK-0001', 'Desk TRÄNHOLM 19', 902.78, 2, 31),
        ('DSK-0002', 'Desk NORDMARK 476', 167.87, 1, 94),
        ('DSK-0003', 'Desk VIKTSTA 642', 84.27, 2, 27),
        ('DSK-0004', 'Desk SNÖRSUND 966', 278.66, 10, 83);
        """)
    else:
        print()
        print("✅ Database is ready for the three-agent pipeline!")
        print("You can now run: python app.py") 