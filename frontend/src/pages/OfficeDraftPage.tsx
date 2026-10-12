import React, { useState } from "react";

type DraftInput = {
  pageReference: string;
  documentDetails: string;
  context: string;
};

const initialInput: DraftInput = {
  pageReference: "",
  documentDetails: "",
  context: "",
};

export default function OfficeDraftPage() {
  const [form, setForm] = useState<DraftInput>(initialInput);
  const [draft, setDraft] = useState("");
  const [copied, setCopied] = useState(false);

  const updateField = (field: keyof DraftInput, value: string) => {
    setForm((previous) => ({ ...previous, [field]: value }));
  };

  const generateDraft = () => {
    const page = form.pageReference.trim();
    const details = form.documentDetails.trim();
    const context = form.context.trim();

    if (!page || !details || !context) {
      window.alert("Please fill in all three fields.");
      return;
    }

    const result = [
      `The letter regarding ${context} is placed at ${page} for kind perusal.`,
      "",
      `Submitted for kind perusal and approval for further necessary action, please.`,
    ];

    setDraft(result.join("\n"));
    setCopied(false);
  };

  const copyDraft = async () => {
    try {
      await navigator.clipboard.writeText(draft);
      setCopied(true);
    } catch {
      window.alert(
        "Copy is unavailable in this browser. Please select and copy the draft manually."
      );
    }
  };

  const resetForm = () => {
    setForm(initialInput);
    setDraft("");
    setCopied(false);
  };

  return (
    <div
      style={{
        maxWidth: 900,
        margin: "0 auto",
        padding: 20,
        color: "var(--foreground, #1f2937)",
      }}
    >
      <header style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 26, marginBottom: 8 }}>
          Office Draft Generator
        </h1>
        <p style={{ margin: 0, lineHeight: 1.6 }}>
          Prepare short and simple official English note sheets.
        </p>
      </header>

      <section
        style={{
          border: "1px solid #d1d5db",
          borderRadius: 12,
          padding: 18,
          marginBottom: 20,
        }}
      >
        <h2 style={{ fontSize: 19, marginTop: 0 }}>
          Note Sheet Details
        </h2>

        <label
          htmlFor="pageReference"
          style={{ display: "block", fontWeight: 600, marginBottom: 6 }}
        >
          Page Number / Reference
        </label>

        <input
          id="pageReference"
          value={form.pageReference}
          onChange={(event) =>
            updateField("pageReference", event.target.value)
          }
          placeholder="Example: Pg. 19/c to 20/c"
          style={inputStyle}
        />

        <label
          htmlFor="documentDetails"
          style={{ display: "block", fontWeight: 600, marginBottom: 6 }}
        >
          Document Details
        </label>

        <input
          id="documentDetails"
          value={form.documentDetails}
          onChange={(event) =>
            updateField("documentDetails", event.target.value)
          }
          placeholder="Example: Letter received from Circle Office"
          style={inputStyle}
        />

        <label
          htmlFor="context"
          style={{ display: "block", fontWeight: 600, marginBottom: 6 }}
        >
          Brief Context
        </label>

        <textarea
          id="context"
          value={form.context}
          onChange={(event) => updateField("context", event.target.value)}
          placeholder="Example: verification of PLI policies"
          rows={3}
          style={{
            ...inputStyle,
            resize: "vertical",
            fontFamily: "inherit",
          }}
        />

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 10,
            marginTop: 16,
          }}
        >
          <button onClick={generateDraft} style={primaryButton}>
            Generate Note Sheet
          </button>

          <button onClick={resetForm} style={secondaryButton}>
            Clear Form
          </button>
        </div>
      </section>

      {draft && (
        <section
          style={{
            border: "1px solid #d1d5db",
            borderRadius: 12,
            padding: 18,
          }}
        >
          <h2 style={{ fontSize: 19, marginTop: 0 }}>
            Generated Note Sheet
          </h2>

          <textarea
            aria-label="Generated note sheet"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            rows={5}
            style={{
              ...inputStyle,
              fontFamily: "inherit",
              lineHeight: 1.8,
              resize: "vertical",
            }}
          />

          <button onClick={copyDraft} style={primaryButton}>
            {copied ? "Copied" : "Copy Text"}
          </button>

          <p style={{ fontSize: 13, lineHeight: 1.5 }}>
            This is a template-based draft. Check the wording and references
            before official use.
          </p>
        </section>
      )}
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  display: "block",
  boxSizing: "border-box",
  width: "100%",
  padding: "11px 12px",
  marginBottom: 16,
  border: "1px solid #9ca3af",
  borderRadius: 7,
  fontSize: 15,
  background: "var(--input-background, #ffffff)",
  color: "var(--foreground, #111827)",
};

const primaryButton: React.CSSProperties = {
  padding: "11px 16px",
  border: "none",
  borderRadius: 7,
  background: "#166534",
  color: "#ffffff",
  fontSize: 15,
  fontWeight: 600,
  cursor: "pointer",
};

const secondaryButton: React.CSSProperties = {
  padding: "11px 16px",
  border: "1px solid #9ca3af",
  borderRadius: 7,
  background: "transparent",
  color: "inherit",
  fontSize: 15,
  cursor: "pointer",
};