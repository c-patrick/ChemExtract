import { useState, useEffect } from "react";
import type { DocumentResponse, ReactionResponse } from "./types";

const API_BASE = "http://localhost:8000";
const PAGE_SIZE = 25;

function App() {
  const [text, setText] = useState("");
  const [document, setDocument] = useState<DocumentResponse | null>(null);
  const [reaction, setReaction] = useState<ReactionResponse | null>(null);
  const [selectedReaction, setSelectedReaction] = useState<ReactionResponse | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
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
    setSelectedReaction(null);

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
      fetchDocuments(page);
    }, 1000);

    return () => clearInterval(interval);
  }, [document, page]);

  // Fetch reaction for newly parsed document
  useEffect(() => {
    if (!document || document.status !== "parsed") return;

    fetch(`${API_BASE}/documents/${document.id}/reaction`)
      .then((res) => res.json())
      .then(setReaction)
      .catch(() => setError("Failed to fetch reaction"));
  }, [document]);

  // Fetch detailed reaction for history click
  const fetchReactionDetails = async (documentId: number) => {
    try {
      const res = await fetch(
        `${API_BASE}/documents/${documentId}/reaction/details`
      );
      if (!res.ok) {
        throw new Error("Failed to fetch reaction details");
      }
      const data = await res.json();
      setSelectedReaction(data);
      setIsModalOpen(true);
    } catch {
      setError("Failed to load reaction details");
    }
  };

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

      {document && (
        <p>
          Status: <strong>{document.status}</strong>
        </p>
      )}

      {reaction && (
        <div style={{ marginTop: "1rem" }}>
          <h3>Latest Parsed Reaction</h3>
          <p>{reaction.summary}</p>
          <p>Confidence: {reaction.confidence_score}</p>
        </div>
      )}

      <h2 style={{ marginTop: "2rem" }}>Document History</h2>

      <ul>
        {documents.map((doc) => (
          <li key={doc.id} style={{ marginBottom: "0.5rem" }}>
            <span
              style={{
                cursor: doc.status === "parsed" ? "pointer" : "default",
                textDecoration: doc.status === "parsed" ? "underline" : "none",
              }}
              onClick={() => {
                if (doc.status === "parsed") {
                  fetchReactionDetails(doc.id);
                }
              }}
            >
              Document #{doc.id} — <strong>{doc.status}</strong>
            </span>

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

      {/* Pagination */}
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

      {/* Modal for reaction details */}
      {isModalOpen && selectedReaction && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 1000,
          }}
          onClick={() => setIsModalOpen(false)}
        >
          <div
            style={{
              backgroundColor: "white",
              padding: "2rem",
              borderRadius: "8px",
              maxWidth: "600px",
              maxHeight: "80vh",
              overflowY: "auto",
              position: "relative",
              color: "black",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              style={{
                position: "absolute",
                top: "10px",
                right: "10px",
                background: "none",
                border: "none",
                fontSize: "1.5rem",
                cursor: "pointer",
              }}
              onClick={() => setIsModalOpen(false)}
            >
              ×
            </button>
            <h3>Reaction Details</h3>
            <p><strong>Summary:</strong> {selectedReaction.summary}</p>
            <p><strong>Confidence:</strong> {selectedReaction.confidence_score}</p>
            <p><strong>Yield:</strong> {selectedReaction.yield_percentage ?? "N/A"}</p>

            <p><strong>Reagents:</strong></p>
            <ul>
              {selectedReaction.reagents?.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>

            <p><strong>Solvents:</strong></p>
            <ul>
              {selectedReaction.solvents?.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>

            <p><strong>Conditions:</strong></p>
            <ul>
              {Object.entries(selectedReaction.conditions ?? {}).map(
                ([key, value]) => (
                  <li key={key}>
                    {key}: {value}
                  </li>
                )
              )}
            </ul>

            <p><em>Parser version: {selectedReaction.parser_version}</em></p>
            <button
              style={{ marginTop: "1rem" }}
              onClick={() => setIsModalOpen(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default App;
