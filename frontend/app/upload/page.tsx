"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import {
  uploadExcel,
  downloadTemplate,
  generateBulkZip,
  generateCombinedPdf,
  generatePdf,
  StudentInput,
} from "@/lib/api";

interface ValidationIssue {
  row?: number;
  student_name?: string;
  field: string;
  message: string;
}

export default function UploadPage() {
  const fileRef = useRef<HTMLInputElement>(null);
  const [students, setStudents] = useState<StudentInput[]>([]);
  const [issues, setIssues] = useState<ValidationIssue[]>([]);
  const [totalRows, setTotalRows] = useState(0);
  const [error, setError] = useState("");
  const [missingColumns, setMissingColumns] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError("");
    setMissingColumns([]);
    setLoading(true);
    try {
      const result = await uploadExcel(file);
      setStudents(result.valid_students);
      setIssues(result.errors);
      setTotalRows(result.total_rows);
    } catch (e: any) {
      setError(e.message);
      setMissingColumns(e.missingColumns || []);
    } finally {
      setLoading(false);
    }
  }

  async function handleBulk(kind: "zip" | "combined") {
    setGenerating(true);
    setError("");
    try {
      if (kind === "zip") await generateBulkZip(students);
      else await generateCombinedPdf(students);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setGenerating(false);
    }
  }

  return (
    <main className="max-w-4xl mx-auto px-6 py-10">
      <Link href="/" className="text-sm text-primary hover:underline">
        ← Back
      </Link>
      <h1 className="text-2xl font-bold mt-2 mb-2">Upload Excel</h1>
      <p className="text-slate-600 mb-6">
        Upload a class spreadsheet to generate reports for every student at
        once.
      </p>

      <div className="card p-6 mb-6">
        <div className="flex flex-wrap items-center gap-3">
          <button className="btn-primary" onClick={() => fileRef.current?.click()}>
            {loading ? "Uploading…" : "Choose Excel File"}
          </button>
          <input
            ref={fileRef}
            type="file"
            accept=".xlsx,.xls"
            className="hidden"
            onChange={handleFile}
          />
          <button className="btn-secondary" onClick={() => downloadTemplate()}>
            Download Excel Template
          </button>
        </div>

        {error && (
          <div className="mt-4 p-4 rounded-lg bg-red-50 text-red-700 text-sm">
            <p className="font-medium mb-1">Upload Error</p>
            <p>{error}</p>
            {missingColumns.length > 0 && (
              <ul className="mt-2 list-disc list-inside">
                {missingColumns.map((c) => (
                  <li key={c}>✗ {c}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>

      {students.length > 0 && (
        <>
          <div className="card p-6 mb-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-lg font-semibold">
                  {totalRows} Students Found
                </p>
                <p className="text-sm text-slate-500">
                  ✓ {students.length} processed &nbsp; ⚠ {issues.length} flagged rows
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  className="btn-primary"
                  disabled={generating}
                  onClick={() => handleBulk("zip")}
                >
                  Download All (ZIP)
                </button>
                <button
                  className="btn-secondary"
                  disabled={generating}
                  onClick={() => handleBulk("combined")}
                >
                  Combined PDF
                </button>
              </div>
            </div>

            {issues.length > 0 && (
              <div className="mt-4 p-3 rounded-lg bg-amber-50 text-amber-800 text-sm">
                <p className="font-medium mb-1">
                  Some rows needed auto-correction — please double check:
                </p>
                <ul className="list-disc list-inside space-y-0.5 max-h-40 overflow-y-auto">
                  {issues.map((iss, i) => (
                    <li key={i}>
                      Row {iss.row} ({iss.student_name || "—"}): {iss.message}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="card divide-y divide-slate-100">
            {students.map((s, i) => (
              <div
                key={i}
                className="p-4 flex items-center justify-between gap-4"
              >
                <div>
                  <p className="font-medium">{s.name}</p>
                  <p className="text-xs text-slate-500">
                    Class {s.class}-{s.section} · Roll {s.roll_number}
                  </p>
                </div>
                <button
                  className="text-sm text-primary hover:underline"
                  onClick={() => generatePdf(s)}
                >
                  Download PDF
                </button>
              </div>
            ))}
          </div>
        </>
      )}
    </main>
  );
}
