import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_connection():
    """
    Establishes a connection to the Supabase PostgreSQL database.
    Returns a connection object or raises an exception if connection fails.
    """
    try:
        connection = psycopg2.connect(
            host=os.environ.get("HOST"),
            database=os.environ.get("DBNAME"),
            user=os.environ.get("USER"),
            password=os.environ.get("PASSWORD"),
            port=os.environ.get("PORT", "5432")
        )
        return connection
    except Exception as e:
        raise Exception(f"Failed to connect to database: {str(e)}")

def get_all_products_for_prompt():
    """
    Fetches all products from the database and formats them for the AI prompt.
    Returns a dictionary keyed by SKU for easy lookup and JSON serialization.
    """
    try:
        connection = get_database_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        query = "SELECT sku, name, price, min_order_qty, inventory FROM products"
        cursor.execute(query)
        
        products = {}
        for row in cursor.fetchall():
            products[row['sku']] = {
                "name": row['name'],
                "price": float(row['price']),
                "min_order_qty": row['min_order_qty'],
                "inventory": row['inventory']
            }
        
        cursor.close()
        connection.close()
        
        return products
        
    except Exception as e:
        raise Exception(f"Failed to fetch products: {str(e)}")

def get_product_by_sku(sku):
    """
    Fetches a specific product by SKU from the database.
    Returns a dictionary with product details or None if not found.
    """
    try:
        connection = get_database_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        query = "SELECT sku, name, price, min_order_qty, inventory FROM products WHERE sku = %s"
        cursor.execute(query, (sku,))
        
        row = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if row:
            return {
                "sku": row['sku'],
                "name": row['name'],
                "price": float(row['price']),
                "min_order_qty": row['min_order_qty'],
                "inventory": row['inventory']
            }
        else:
            return None
            
    except Exception as e:
        raise Exception(f"Failed to fetch product {sku}: {str(e)}") 