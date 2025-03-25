import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";

function SummaryView() {
  const [summaryData, setSummaryData] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const summaryString = params.get("summary");

  if (summaryString) {
    try {
      const decoded = decodeURIComponent(summaryString);  // decode ONCE
      const parsed = JSON.parse(decoded);                // parse AFTER decode
      setSummaryData(parsed);
    } catch (err) {
      console.error("❌ Failed to parse summary from URL:", err);
    }
  }
  }, []);

  if (!summaryData) {
    return <p>No summary data provided.</p>;
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-xl font-bold mb-2">{summaryData.title}</h1>

      {summaryData.clickbait_score !== undefined && (
        <p>Clickbait Score: ⭐{summaryData.clickbait_score}/5</p>
      )}

      <div className="mt-4 flex items-center gap-3">
        <button
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded shadow text-sm"
          onClick={() => {
            navigator.clipboard
              .writeText(summaryData.summary_markdown)
              .then(() => alert("✅ Summary copied to clipboard!"))
              .catch(() => alert("❌ Failed to copy!"));
          }}
        >
          📋 Copy Summary
        </button>
      </div>

      <div className="mt-4">
        <h2 className="font-semibold">AI-Generated Summary:</h2>
        <ReactMarkdown>{summaryData.summary_markdown}</ReactMarkdown>
      </div>
    </div>
  );
}

export default SummaryView;
