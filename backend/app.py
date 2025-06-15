import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from database import initialize_connection_pool, close_connection_pool
from agents.extraction_agent import ExtractionAgent
from agents.validation_agent import ValidationAgent
from agents.response_agent import ResponseAgent

# Load environment variables from .env file
load_dotenv()

# --- Application Setup ---
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) for our frontend
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Global variables for agents and model
model = None
extraction_agent = None
validation_agent = None
response_agent = None

def initialize_agents():
    """
    Initialize all agents and the Gemini model.
    """
    global model, extraction_agent, validation_agent, response_agent
    
    try:
        # Configure Gemini API
        api_key = os.environ["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Initialize agents
        extraction_agent = ExtractionAgent(model)
        validation_agent = ValidationAgent()
        response_agent = ResponseAgent(model)
        
        print("All agents initialized successfully")
        
    except KeyError:
        print("ERROR: GEMINI_API_KEY not found in .env file.")
        exit()
    except Exception as e:
        print(f"ERROR initializing agents: {e}")
        exit()

# --- API Endpoint ---
@app.route("/api/extract-order", methods=["POST"])
def extract_order_details():
    """
    Main API endpoint that orchestrates the three-agent pipeline:
    Email Text -> [Agent 1: Extractor] -> Raw JSON -> [Agent 2: DB Validator] -> Validated Order -> [Agent 3: Response Agent] -> Final Response
    """
    try:
        data = request.get_json()
        
        if not data or "email_content" not in data:
            return jsonify({"error": "Missing 'email_content' in request"}), 400
        
        email_content = data["email_content"]
        
        # Step 1: Agent 1 - Extract raw order details
        print("Step 1: Agent 1 (Extractor) processing...")
        raw_extraction_data = extraction_agent.extract_details(email_content)
        print(f"Agent 1 completed. Extracted {len(raw_extraction_data.get('items', []))} items")
        
        # Step 2: Agent 2 - Database validation
        print("Step 2: Agent 2 (DB Validator) processing...")
        validated_order = validation_agent.validate_order(raw_extraction_data)
        print(f"Agent 2 completed. Validated: {len(validated_order.get('validated_items', []))} items, Issues: {len(validated_order.get('issues', []))}")
        
        # Step 3: Agent 3 - Generate customer response
        print("Step 3: Agent 3 (Response Agent) processing...")
        final_response = response_agent.generate_customer_response(validated_order)
        print("Agent 3 completed. Response generated.")
        
        # Return the complete response
        return jsonify(final_response), 200
        
    except json.JSONDecodeError as json_error:
        return jsonify({"error": "Invalid JSON response from AI model", "details": str(json_error)}), 500
        
    except Exception as e:
        return jsonify({"error": "Failed to process request", "details": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Health check endpoint to verify the application is running.
    """
    return jsonify({"status": "healthy", "message": "Three-agent pipeline is operational"}), 200

if __name__ == "__main__":
    # Initialize database connection pool
    print("Initializing database connection pool...")
    initialize_connection_pool()
    
    # Initialize agents
    print("Initializing agents...")
    initialize_agents()
    
    # Start the Flask application
    print("Starting Flask application...")
    app.run(debug=True, port=5001)
    
    # Cleanup on shutdown
    print("Shutting down...")
    close_connection_pool()