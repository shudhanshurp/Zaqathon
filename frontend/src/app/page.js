"use client";

import { useState } from "react";

export default function Home() {
  const [emailContent, setEmailContent] = useState("");
  const [orderData, setOrderData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleProcessEmail = async () => {
    if (!emailContent.trim()) {
      setError("Email content cannot be empty.");
      return;
    }
    setIsLoading(true);
    setError(null);
    setOrderData(null);

    try {
      const response = await fetch("http://127.0.0.1:5001/api/extract-order", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email_content: emailContent }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "An unknown error occurred.");
      }

      const data = await response.json();
      setOrderData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Example email text to pre-populate the textarea
  const sampleEmail = `
Hi team,

I'd like to place an order for the following items:
- 50 of the large blue t-shirts (TS-BL-LG)
- 5 of the black hoodies, large. The SKU is HD-BK-LG
- 15 of the green caps (CP-GR-OS)
- 25 of the TS-YL-SM (yellow shirts)

Please have this delivered by next Friday if possible. Also, can you confirm if you offer bulk discounts?

Thanks,
Alex
  `.trim();

  return (
    <main className="flex min-h-screen flex-col items-center p-12 bg-gray-50">
      <div className="z-10 w-full max-w-6xl items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-2">
          Intelligent Order Processor
        </h1>
        <p className="text-center text-gray-500 mb-8">
          Three-Agent Pipeline: Extract, Validate, and Respond to Order Emails
        </p>

        <div className="w-full bg-white p-6 rounded-lg shadow-md">
          <label
            htmlFor="email-input"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Email Content
          </label>
          <textarea
            id="email-input"
            rows={10}
            className="w-full p-3 text-gray-800 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
            value={emailContent}
            onChange={(e) => setEmailContent(e.target.value)}
            placeholder="Paste customer email here..."
          />
          <div className="mt-4 flex justify-between items-center">
            <button
              type="button"
              onClick={() => setEmailContent(sampleEmail)}
              className="text-sm text-blue-600 hover:underline"
            >
              Load Sample Email
            </button>
            <button
              onClick={handleProcessEmail}
              disabled={isLoading}
              className="px-6 py-2 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? "Processing..." : "Process Email"}
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-6 w-full bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md">
            <strong className="font-bold">Error: </strong>
            <span>{error}</span>
          </div>
        )}

        {orderData && (
          <div className="mt-6 w-full space-y-6">
            {/* AI Generated Email Response */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                AI Generated Response
              </h2>
              <div className="bg-gray-50 p-4 rounded-md border-l-4 border-blue-500">
                <div className="whitespace-pre-wrap text-gray-800 font-medium">
                  {orderData.email_response}
                </div>
              </div>
            </div>

            {/* Order Summary */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                Order Summary
              </h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Validated Items */}
                <div>
                  <h3 className="text-lg font-semibold border-b pb-2 mb-3 text-green-700">
                    ✅ Validated Items
                  </h3>
                  {orderData.order_summary.validated_items.length > 0 ? (
                    <div className="space-y-2">
                      {orderData.order_summary.validated_items.map((item, index) => (
                        <div key={index} className="bg-green-50 p-3 rounded-md border border-green-200">
                          <div className="flex justify-between items-center">
                            <div>
                              <span className="font-semibold text-green-800">
                                {item.quantity} x {item.name}
                              </span>
                              <div className="text-sm text-gray-600">SKU: {item.sku}</div>
                            </div>
                            <div className="text-right">
                              <div className="font-semibold text-green-800">
                                ${(item.price * item.quantity).toFixed(2)}
                              </div>
                              <div className="text-sm text-gray-600">
                                ${item.price.toFixed(2)} each
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 italic">No items were successfully validated.</p>
                  )}
                </div>

                {/* Issues */}
                <div>
                  <h3 className="text-lg font-semibold border-b pb-2 mb-3 text-yellow-700">
                    ⚠️ Issues Found
                  </h3>
                  {orderData.order_summary.issues.length > 0 ? (
                    <div className="space-y-3">
                      {orderData.order_summary.issues.map((issue, index) => (
                        <div key={index} className="bg-yellow-50 p-3 rounded-md border border-yellow-200">
                          <div className="mb-2">
                            <span className="font-semibold text-yellow-800">
                              {issue.item_mentioned}
                            </span>
                            <span className="ml-2 px-2 py-1 bg-yellow-200 text-yellow-800 text-xs rounded-full">
                              {issue.issue_type}
                            </span>
                          </div>
                          <p className="text-sm text-gray-700 mb-2">{issue.message}</p>
                          <p className="text-sm text-blue-600 font-medium">
                            💡 {issue.suggestion}
                          </p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 italic">No issues found.</p>
                  )}
                </div>
              </div>

              {/* Additional Information */}
              <div className="mt-6 pt-4 border-t border-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <span className="font-semibold text-gray-700">Delivery Preference:</span>
                    <p className="text-gray-600 mt-1">
                      {orderData.order_summary.delivery_preference || "Not specified"}
                    </p>
                  </div>
                  <div>
                    <span className="font-semibold text-gray-700">Customer Notes:</span>
                    <p className="text-gray-600 mt-1">
                      {orderData.order_summary.customer_notes || "No additional notes"}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Raw JSON View */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold border-b pb-2 mb-3">
                Raw JSON Output
              </h3>
              <pre className="bg-gray-900 text-white p-4 rounded-md text-xs overflow-x-auto">
                {JSON.stringify(orderData, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}