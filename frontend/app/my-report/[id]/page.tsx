"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function MyReportPage() {
  const params = useParams();
  const { user } = useAuth();
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchReport() {
      try {
        const res = await fetch(`/api/reports/view/${params.id}`);
        if (!res.ok) throw new Error("Unauthorized or report not found");
        const data = await res.json();
        setReport(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    fetchReport();
  }, [params.id]);

  if (!user) {
    return <div className="p-8 text-center">Please login to view your report.</div>;
  }

  if (loading) return <div className="p-8 text-center">Loading your report...</div>;
  if (!report) return <div className="p-8 text-center">Report not found or access denied.</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="bg-white shadow-xl rounded-2xl p-12 border-t-8 border-blue-800">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-blue-900">STUDENT PROGRESS REPORT</h1>
          <p className="text-gray-600 uppercase tracking-widest mt-2">Academic Year 2026-27</p>
        </div>

        <div className="grid grid-cols-2 gap-8 mb-12 p-6 bg-gray-50 rounded-lg">
          <div>
            <p className="text-sm text-gray-500">Student Name</p>
            <p className="text-xl font-bold">{report.data.student}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Report ID</p>
            <p className="text-xl font-mono">{params.id}</p>
          </div>
        </div>

        <div className="flex justify-center gap-12 mb-12">
          <div className="text-center">
            <p className="text-sm text-gray-500">Overall Percentage</p>
            <p className="text-5xl font-black text-blue-700">{report.data.overall_percentage}%</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-500">Final Grade</p>
            <p className="text-5xl font-black text-blue-700">{report.data.grade}</p>
          </div>
        </div>

        <div className="text-center mt-16 border-t pt-8">
          <p className="text-gray-400 italic">This is an electronically generated report and does not require a physical signature.</p>
        </div>
      </div>
    </div>
  );
}
