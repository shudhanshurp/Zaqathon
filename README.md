# Intelligent Inventory Order Processor

## Purpose of the Project

This project is an intelligent web application designed to automate the initial, most time-consuming steps of processing customer orders received via email. Its core purpose is to read unstructured email requests, understand the customer's intent, and transform that information into a structured, validated, and actionable order summary.

The system acts as an intelligent assistant for an inventory or sales team, presenting them with a clear breakdown of what can be fulfilled immediately and what requires further attention, complete with a pre-written, professional email response ready to be sent to the customer.

---

## Why This Project Exists

In many businesses, the order fulfillment process begins with a significant manual bottleneck: an employee must read through customer emails, decipher requests, and manually enter SKUs and quantities into an inventory system. This process is not only slow but also highly susceptible to human error.

This project exists to solve these specific problems:

*   **To Eliminate Manual Data Entry:** It automates the tedious task of translating conversational language into precise order data, freeing up valuable employee time for more critical tasks.
*   **To Reduce Human Error:** By systematically extracting and validating information against a central database, it drastically reduces costly mistakes like shipping the wrong product, incorrect quantities, or accepting orders for out-of-stock items.
*   **To Accelerate Order Fulfillment:** It provides an instant, validated summary of an order request, allowing the fulfillment team to act immediately rather than waiting for manual verification.
*   **To Improve Customer Communication:** It standardizes and professionalizes customer interactions by generating clear, consistent, and context-aware email responses that address all parts of a customer's original request.

---

## Technology Stack

*   **Frontend:** Next.js, JavaScript (with TypeScript), Tailwind CSS
*   **Backend:** Flask (Python)
*   **Database:** Supabase (PostgreSQL)
*   **Artificial Intelligence:** Google Gemini Large Language Model

---

## Architecture: The Specialist Agent Pipeline

To achieve its goal, the application employs a sophisticated multi-agent backend architecture. Instead of a single, monolithic process, the task is broken down and handled by a sequence of three specialized agents, each with a distinct responsibility.

### **Agent 1: The Extraction Agent**

This is the first point of contact with the raw email content. Its sole purpose is to read the unstructured text and perform an initial interpretation. It identifies potential product codes (SKUs), requested quantities, and any other customer notes or questions. It makes an educated "guess" about the customer's intent and structures this raw data for the next agent in the pipeline.

### **Agent 2: The Database Validation Agent**

This agent acts as the system's connection to reality. It is a purely logical, non-AI component that takes the raw extracted data from Agent 1 and rigorously validates it against the live Supabase database. For every item requested, it performs a series of checks:

1.  Does the SKU exist in the product catalog?
2.  Is the requested quantity available in stock?
3.  Does the request meet the Minimum Order Quantity (MOQ) for that product?

This agent sorts the request into two categories: items that are fully validated and ready for processing, and items that have issues. It is the critical bridge between the AI's interpretation and the factual state of the business inventory.

### **Agent 3: The Customer Service Agent**

The final agent in the pipeline receives the structured, fact-checked order data from the Validator. Its role is that of a professional communicator. Using this structured data as context, it generates a helpful, polite, and comprehensive email response. The email confirms the validated parts of the order and clearly explains any issues found (e.g., an item being out of stock or an invalid product code), presenting the system-generated suggestions to resolve them. The final output is a ready-to-send email that is both empathetic and factually accurate.
