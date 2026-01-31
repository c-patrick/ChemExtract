import { useState, useEffect } from "react";
import type { DocumentResponse, ReactionResponse } from "./types";

const API_BASE = "http://localhost:8000";
const PAGE_SIZE = 25;

function App() {
  const [text, setText] = useState("");
  const [document, setDocument] = useState<DocumentResponse | null>(null);
  const [reaction, setReaction] = useState<ReactionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [page, setPage] = useState(1);
  const [totalDocuments, setTotalDocuments] = useState(0);

  const totalPages = Math.ceil(totalDocuments / PAGE_SIZE);

  // Fetch documents for a given page
  const fetchDocuments = async (pageNum = 1) => {
    try {
      const res = await fetch(
        `${API_BASE}/documents/?page=${pageNum}&page_size=${PAGE_SIZE}`
      );
      const data = await res.json();

      setDocuments(data.items ?? []);
      setTotalDocuments(data.total ?? 0);
    } catch {
      setError("Failed to fetch documents");
    }
  };

  useEffect(() => {
    fetchDocuments(page);
  }, [page]);

  // Submit new document
  const submitDocument = async () => {
    setError(null);
    setReaction(null);

    const res = await fetch(`${API_BASE}/documents/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source_type: "text",
        original_text: text,
      }),
    });

    const data = await res.json();
    setDocument(data);

    // Reload first page after submission
    setPage(1);
    fetchDocuments(1);
  };

  // Poll document status
  useEffect(() => {
    if (!document || document.status === "parsed" || document.status === "failed") {
      return;
    }

    const interval = setInterval(async () => {
      const res = await fetch(`${API_BASE}/documents/${document.id}`);
      const data = await res.json();
      setDocument(data);
    }, 1000);

    return () => clearInterval(interval);
  }, [document]);

  // Fetch reaction when parsed
  useEffect(() => {
    if (!document || document.status !== "parsed") return;

    fetch(`${API_BASE}/documents/${document.id}/reaction`)
      .then((res) => res.json())
      .then(setReaction)
      .catch(() => setError("Failed to fetch reaction"));
  }, [document]);

  return (
    <div style={{ padding: "2rem", maxWidth: "800px" }}>
      <h1>Chemical Reaction Parser</h1>

      <textarea
        rows={6}
        style={{ width: "100%" }}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste experimental write-up here..."
      />

      <button onClick={submitDocument} style={{ marginTop: "1rem" }}>
        Parse Reaction
      </button>

      <h2 style={{ marginTop: "2rem" }}>Document History</h2>

      <ul>
        {documents.map((doc) => (
          <li key={doc.id}>
            Document #{doc.id} — <strong>{doc.status}</strong>

            {doc.status === "failed" && (
              <button
                style={{ marginLeft: "1rem" }}
                onClick={async () => {
                  await fetch(
                    `${API_BASE}/documents/${doc.id}/reprocess`,
                    { method: "POST" }
                  );
                  fetchDocuments(page);
                }}
              >
                Retry
              </button>
            )}
          </li>
        ))}
      </ul>

      {/* Pagination controls */}
      <div style={{ marginTop: "1rem" }}>
        <button
          disabled={page === 1}
          onClick={() => setPage((p) => Math.max(1, p - 1))}
        >
          Previous
        </button>

        <span style={{ margin: "0 1rem" }}>
          Page {page} of {totalPages || 1}
        </span>

        <button
          disabled={page >= totalPages}
          onClick={() => setPage((p) => p + 1)}
        >
          Next
        </button>
      </div>

      {document && (
        <p>
          Status: <strong>{document.status}</strong>
        </p>
      )}

      {reaction && (
        <div style={{ marginTop: "1rem" }}>
          <h3>Parsed Reaction</h3>
          <p>{reaction.summary}</p>
          <p>Confidence: {reaction.confidence_score}</p>
        </div>
      )}

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default App;
