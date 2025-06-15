import os
import csv
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# --- Configuration ---
CSV_FILE_PATH = "./product_data/Product Catalog.csv"

# --- Database Connection ---
# Establish a connection to the PostgreSQL database.
# The connection is managed in a try...finally block to ensure it's always closed.
conn = None
try:
    print("Connecting to the PostgreSQL database...")
    conn = psycopg2.connect(
        host=os.environ.get("HOST"),
        dbname=os.environ.get("DBNAME"),
        user=os.environ.get("USER"),
        password=os.environ.get("PASSWORD"),
        port=os.environ.get("PORT"),
    )
    print("Database connection successful.")

    # --- Data Processing and Upload ---
    with conn.cursor() as cur:
        with open(CSV_FILE_PATH, mode="r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            products_to_upload = []

            print(f"Reading data from {CSV_FILE_PATH}...")
            for row in reader:
                try:
                    # Create a tuple of values in the correct order for insertion
                    products_to_upload.append(
                        (
                            row["Product_Code"],
                            row["Product_Name"],
                            float(row["Price"]),
                            int(row["Available_in_Stock"]),
                            int(row["Min_Order_Quantity"]),
                            row["Description"],
                        )
                    )
                except (ValueError, KeyError) as e:
                    print(f"Skipping row due to data error: {row}. Error: {e}")
                    continue

            if not products_to_upload:
                print("No valid products found to upload.")
                exit()

            print(
                f"Found {len(products_to_upload)} products. "
                "Upserting into the database..."
            )

            # Define the SQL query for batch upsert
            # ON CONFLICT(sku) tells PostgreSQL what to do if a row with a
            # conflicting 'sku' (the primary key) already exists.
            # DO UPDATE SET ... specifies which columns to update.
            # 'EXCLUDED' refers to the values from the new data being inserted.
            upsert_query = """
                INSERT INTO public.products (sku, name, price, inventory, min_order_qty, description)
                VALUES %s
                ON CONFLICT (sku) DO UPDATE SET
                    name = EXCLUDED.name,
                    price = EXCLUDED.price,
                    inventory = EXCLUDED.inventory,
                    min_order_qty = EXCLUDED.min_order_qty,
                    description = EXCLUDED.description;
            """

            # Use execute_values for efficient batch upserting
            psycopg2.extras.execute_values(
                cur, upsert_query, products_to_upload
            )

            # Commit the transaction to make the changes permanent
            conn.commit()
            print("Successfully upserted all products!")

except FileNotFoundError:
    print(f"Error: The file {CSV_FILE_PATH} was not found.")
except psycopg2.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    # Ensure the database connection is closed
    if conn is not None:
        conn.close()
        print("Database connection closed.")