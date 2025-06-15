import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from dotenv import load_dotenv
from contextlib import contextmanager

# Load environment variables
load_dotenv()

# Global connection pool
_connection_pool = None

def initialize_connection_pool():
    """
    Initialize the database connection pool.
    Should be called once when the application starts.
    """
    global _connection_pool
    try:
        _connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.environ.get("HOST"),
            database=os.environ.get("DBNAME"),
            user=os.environ.get("USER"),
            password=os.environ.get("PASSWORD"),
            port=os.environ.get("PORT", "5432")
        )
        print("Database connection pool initialized successfully")
    except Exception as e:
        raise Exception(f"Failed to initialize connection pool: {str(e)}")

@contextmanager
def get_database_connection():
    """
    Context manager for database connections.
    Automatically handles connection borrowing and returning.
    """
    if _connection_pool is None:
        initialize_connection_pool()
    
    connection = None
    try:
        connection = _connection_pool.getconn()
        yield connection
    except Exception as e:
        if connection:
            connection.rollback()
        raise Exception(f"Database operation failed: {str(e)}")
    finally:
        if connection:
            _connection_pool.putconn(connection)

def get_all_products_for_prompt():
    """
    Fetches all products from the database and formats them for the AI prompt.
    Returns a dictionary keyed by SKU for easy lookup and JSON serialization.
    """
    try:
        with get_database_connection() as connection:
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
            return products
            
    except Exception as e:
        raise Exception(f"Failed to fetch products: {str(e)}")

def get_product_by_sku(sku):
    """
    Fetches a specific product by SKU from the database.
    Returns a dictionary with product details or None if not found.
    """
    try:
        with get_database_connection() as connection:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            query = "SELECT sku, name, price, min_order_qty, inventory FROM products WHERE sku = %s"
            cursor.execute(query, (sku,))
            
            row = cursor.fetchone()
            cursor.close()
            
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

def get_product_by_name(product_name):
    """
    Fetches a specific product by name from the database.
    Uses case-insensitive search and partial matching.
    Returns a dictionary with product details or None if not found.
    """
    try:
        with get_database_connection() as connection:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            # Use ILIKE for case-insensitive search and % for partial matching
            query = "SELECT sku, name, price, min_order_qty, inventory FROM products WHERE name ILIKE %s"
            cursor.execute(query, (f"%{product_name}%",))
            
            rows = cursor.fetchall()
            cursor.close()
            
            if rows:
                # Return the first match (most relevant)
                row = rows[0]
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
        raise Exception(f"Failed to fetch product by name '{product_name}': {str(e)}")

def close_connection_pool():
    """
    Close the database connection pool.
    Should be called when the application shuts down.
    """
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        print("Database connection pool closed") 