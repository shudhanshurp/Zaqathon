# Flask Backend with Three-Agent Pipeline

## Architecture Overview

This application implements a sophisticated three-agent pipeline for intelligent order processing:

```
Email Text -> [Agent 1: Extractor] -> Raw JSON -> [Agent 2: DB Validator] -> Validated Order -> [Agent 3: Response Agent] -> Final Response
```

### Agent 1: Extractor
- **Purpose**: Uses AI (Google Gemini) to extract order details from unstructured email content
- **Input**: Raw email text
- **Output**: Structured JSON with items, quantities, delivery preferences, and customer notes
- **File**: `agents/extraction_agent.py`

### Agent 2: Database Validation Bridge
- **Purpose**: Non-AI, logic-driven component that validates extracted data against Supabase PostgreSQL
- **Input**: Raw extraction data from Agent 1
- **Output**: Validated order with confirmed items and identified issues
- **File**: `agents/validation_agent.py`

### Agent 3: Response Agent
- **Purpose**: Generates customer-friendly responses based on validated order data
- **Input**: Validated order from Agent 2
- **Output**: Professional email response and order summary
- **File**: `agents/response_agent.py`

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
HOST=your_supabase_host_here
DBNAME=postgres
USER=postgres
PASSWORD=your_supabase_password_here
PORT=5432
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

- **Three-Agent Pipeline**: Sophisticated processing with clear separation of concerns
- **Real-time Database Validation**: Live queries to Supabase PostgreSQL for accurate inventory and pricing
- **AI-Powered Extraction**: Intelligent parsing of unstructured email content
- **Professional Response Generation**: Customer-friendly email responses
- **Connection Pooling**: Efficient database connection management
- **Comprehensive Error Handling**: Robust error handling at each pipeline stage

## API Endpoints

### POST /api/extract-order
Processes email content through the three-agent pipeline.

**Request Body:**
```json
{
  "email_content": "I need 20 blue t-shirts and 5 hoodies..."
}
```

**Response:**
```json
{
  "email_response": "Dear Customer,\n\nThank you for your order...",
  "order_summary": {
    "validated_items": [
      {
        "sku": "TS-BL-LG",
        "name": "T-Shirt, Blue, Large",
        "quantity": 20,
        "price": 15.00
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
}
```

### GET /api/health
Health check endpoint to verify the application is running.

## Database Connection Pool

The application uses a connection pool for efficient database access:
- **Min connections**: 1
- **Max connections**: 10
- **Automatic cleanup**: Connections are automatically returned to the pool
- **Error handling**: Failed connections are properly handled and logged

## Error Handling

Each agent has comprehensive error handling:
- **Agent 1**: JSON parsing errors, AI API failures
- **Agent 2**: Database connection errors, validation failures
- **Agent 3**: Response generation errors

## Development

### Adding New Agents
1. Create a new agent class in the `agents/` directory
2. Implement the required interface
3. Add initialization in `app.py`
4. Update the pipeline orchestration

### Database Operations
- Use the `get_database_connection()` context manager for safe database access
- All database operations are automatically handled with proper error recovery 