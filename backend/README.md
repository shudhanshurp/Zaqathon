# Flask Backend with Supabase Integration

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the backend directory with the following variables:

```
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase Database Configuration
SUPABASE_HOST=your_supabase_host_here
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=your_supabase_password_here
SUPABASE_PORT=5432
```

### 3. Database Schema
Ensure your Supabase database has a `products` table with the following structure:

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    min_order_qty INTEGER NOT NULL,
    inventory INTEGER NOT NULL
);
```

### 4. Run the Application
```bash
python app.py
```

The server will start on `http://localhost:5001`

## Features

- **Real-time Product Data**: Fetches product catalog from Supabase PostgreSQL database
- **AI-Powered Order Processing**: Uses Google Gemini to extract and validate orders from email content
- **Two-Layer Validation**: 
  - Initial AI validation based on catalog data
  - Server-side validation with latest database data
- **Robust Error Handling**: Comprehensive error handling for database and API failures

## API Endpoints

### POST /api/extract-order
Processes email content and extracts order details with validation.

**Request Body:**
```json
{
  "email_content": "I need 20 blue t-shirts and 5 hoodies..."
}
```

**Response:**
```json
{
  "validated_items": [
    {
      "sku": "TS-BL-LG",
      "quantity": 20,
      "name": "T-Shirt, Blue, Large"
    }
  ],
  "issues": [
    {
      "item_mentioned": "hoodies",
      "issue_type": "SKU_NOT_FOUND",
      "message": "Product not found in catalog",
      "suggestion": "Available: HD-BK-LG (Hoodie, Black, Large)"
    }
  ],
  "delivery_preference": "Standard shipping",
  "customer_notes": "Need by next week"
}
``` 