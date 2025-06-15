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
      <div className="z-10 w-full max-w-4xl items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-2">
          Intelligent Order Processor
        </h1>
        <p className="text-center text-gray-500 mb-8">
          Paste an order email below to extract and validate the details.
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
          <div className="mt-6 w-full bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Extraction Result
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* User Friendly View */}
              <div>
                <h3 className="text-lg font-semibold border-b pb-2 mb-3">
                  Order Summary
                </h3>
                {orderData.validated_items.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-bold text-green-700">
                      Validated Items
                    </h4>
                    <ul className="list-disc list-inside text-gray-700">
                      {orderData.validated_items.map((item) => (
                        <li key={item.sku}>
                          {item.quantity} x {item.name} ({item.sku})
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {orderData.issues.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-bold text-yellow-700">
                      Action Required
                    </h4>
                    <ul className="list-disc list-inside text-gray-700">
                      {orderData.issues.map((issue, index) => (
                        <li key={index} className="mt-2">
                          <p>
                            <span className="font-semibold">Item:</span>{" "}
                            {issue.item_mentioned}
                          </p>
                          <p>
                            <span className="font-semibold">Issue:</span>{" "}
                            {issue.message}
                          </p>
                          <p className="text-blue-600">
                            <span className="font-semibold">Suggestion:</span>{" "}
                            {issue.suggestion}
                          </p>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <p>
                  <span className="font-semibold">Delivery:</span>{" "}
                  {orderData.delivery_preference}
                </p>
                <p>
                  <span className="font-semibold">Notes:</span>{" "}
                  {orderData.customer_notes}
                </p>
              </div>
              {/* Raw JSON View */}
              <div>
                <h3 className="text-lg font-semibold border-b pb-2 mb-3">
                  Raw JSON Output
                </h3>
                <pre className="bg-gray-900 text-white p-4 rounded-md text-xs overflow-x-auto">
                  {JSON.stringify(orderData, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}