"use client";

import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";

type Step = "upload" | "sheet" | "mapping" | "subjects" | "review";

export default function ProfileBuilder() {
  const { user } = useAuth();
  const [step, setStep] = useState<Step>("upload");
  const [file, setFile] = useState<File | null>(null);
  const [inspection, setInspection] = useState<any>(null);
  const [selectedSheet, setSelectedSheet] = useState<string | null>(null);
  const [mappings, setMappings] = useState<Record<string, string>>({});

  if (!user || user.role !== "admin") {
    return <div className="p-8 text-center">Access Denied</div>;
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;
    setFile(selectedFile);

    const formData = new FormData();
    formData.append("file", selectedFile);

    const res = await fetch("/api/reports/inspect", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setInspection(data);
    setStep("sheet");
  };

  const nextStep = () => {
    if (step === "upload") setStep("sheet");
    else if (step === "sheet") setStep("mapping");
    else if (step === "mapping") setStep("subjects");
    else if (step === "subjects") setStep("review");
  };

  const prevStep = () => {
    if (step === "sheet") setStep("upload");
    else if (step === "mapping") setStep("sheet");
    else if (step === "subjects") setStep("mapping");
    else if (step === "review") setStep("subjects");
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Create Import Profile</h1>

      {/* Progress Stepper */}
      <div className="flex justify-between mb-12 relative">
        {["Upload", "Sheet", "Mapping", "Subjects", "Review"].map((label, i) => (
          <div key={label} className="flex flex-col items-center z-10">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center mb-2 ${
              (i === 0 && step === "upload") || (i === 1 && step === "sheet") ||
              (i === 2 && step === "mapping") || (i === 3 && step === "subjects") ||
              (i === 4 && step === "review") ? "bg-blue-600 text-white" : "bg-gray-200"
            }`}>
              {i + 1}
            </div>
            <span className="text-xs font-medium">{label}</span>
          </div>
        ))}
        <div className="absolute top-4 left-0 right-0 h-0.5 bg-gray-200 -z-0"></div>
      </div>

      <div className="bg-white shadow-lg rounded-xl p-8 min-h-[400px]">
        {step === "upload" && (
          <div className="text-center py-12">
            <div className="mb-6 text-gray-500">Upload a representative Excel workbook to start.</div>
            <input type="file" onChange={handleUpload} className="block mx-auto text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
          </div>
        )}

        {step === "sheet" && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Select Relevant Sheet</h2>
            <div className="grid grid-cols-2 gap-4">
              {inspection?.sheets.map((s: any) => (
                <div
                  key={s.sheet_name}
                  onClick={() => setSelectedSheet(s.sheet_name)}
                  className={`p-4 border rounded-lg cursor-pointer transition-all ${selectedSheet === s.sheet_name ? "border-blue-600 bg-blue-50 ring-2 ring-blue-600" : "hover:border-gray-400"}`}
                >
                  <div className="font-bold">{s.sheet_name}</div>
                  <div className="text-xs text-gray-500">{s.dimensions.rows} rows x {s.dimensions.cols} cols</div>
                </div>
              ))}
            </div>
            <button
              disabled={!selectedSheet}
              onClick={nextStep}
              className="mt-8 bg-blue-600 text-white px-6 py-2 rounded-lg disabled:bg-gray-300"
            >
              Continue to Mapping
            </button>
          </div>
        )}

        {step === "mapping" && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Map Fields</h2>
            <div className="space-y-4">
              {["Admission Number", "Student Name", "Class", "Section"].map(field => (
                <div key={field} className="flex items-center gap-4">
                  <span className="w-48 font-medium">{field}</span>
                  <select
                    className="flex-1 p-2 border rounded"
                    onChange={(e) => setMappings({...mappings, [field]: e.target.value})}
                  >
                    <option value="">Select Column...</option>
                    {inspection?.sheets.find((s: any) => s.sheet_name === selectedSheet)?.header_candidates[0].values.map((val: any, i: number) => (
                      <option key={i} value={i}>{val || `Column ${i+1}`}</option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
            <button onClick={nextStep} className="mt-8 bg-blue-600 text-white px-6 py-2 rounded-lg">
              Continue to Subjects
            </button>
          </div>
        )}

        {step === "subjects" && (
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold mb-4">Map Subjects & Assessments</h2>
            <p className="text-gray-500 mb-8">This step allows you to map workbook columns to specific subjects and assessment types.</p>
            <button onClick={nextStep} className="bg-blue-600 text-white px-6 py-2 rounded-lg">
              Continue to Review
            </button>
          </div>
        )}

        {step === "review" && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Review Profile</h2>
            <div className="bg-gray-50 p-4 rounded-lg space-y-2 mb-8">
              <div className="flex justify-between"><span>Sheet:</span> <b>{selectedSheet}</b></div>
              <div className="flex justify-between"><span>Mappings:</span> <b>{Object.keys(mappings).length} fields mapped</b></div>
            </div>
            <div className="flex gap-4">
              <button onClick={prevStep} className="px-6 py-2 border rounded-lg">Back</button>
              <button className="bg-green-600 text-white px-6 py-2 rounded-lg">Save Profile v1</button>
            </div>
          </div>
        )}
      </div>

      {step !== "upload" && (
        <div className="mt-4 flex justify-end">
          <button onClick={prevStep} className="text-gray-500 hover:text-gray-700">← Previous Step</button>
        </div>
      )}
    </div>
  );
}
