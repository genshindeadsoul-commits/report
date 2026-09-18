"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";

interface AcademicYear {
  name: string;
  start_date: string;
  end_date: string;
  status: string;
}

interface SchoolClass {
  name: string;
  display_order: number;
}

export default function ConfigPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("years");
  const [years, setYears] = useState<AcademicYear[]>([]);
  const [classes, setClasses] = useState<SchoolClass[]>([]);

  useEffect(() => {
    // Fetch initial data
    fetch("/api/config/years").then(res => res.json()).then(setYears);
    fetch("/api/config/classes").then(res => res.json()).then(setClasses);
  }, []);

  if (!user || user.role !== "admin") {
    return (
      <div className="p-8 text-center">
        <h1 className="text-2xl font-bold text-red-600">Access Denied</h1>
        <p>Only administrators can access the system configuration.</p>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">System Configuration</h1>

      <div className="flex gap-4 mb-8 border-b">
        {["years", "classes", "sections", "subjects"].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-2 px-4 capitalize ${activeTab === tab ? "border-b-2 border-blue-600 font-bold" : "text-gray-500"}`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        {activeTab === "years" && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Academic Years</h2>
            <table className="w-full text-left">
              <thead>
                <tr className="border-b">
                  <th className="py-2">Year Name</th>
                  <th className="py-2">Start Date</th>
                  <th className="py-2">End Date</th>
                  <th className="py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {years.map((y, i) => (
                  <tr key={i} className="border-b">
                    <td className="py-2">{y.name}</td>
                    <td className="py-2">{y.start_date}</td>
                    <td className="py-2">{y.end_date}</td>
                    <td className="py-2">{y.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <button className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              + Add Academic Year
            </button>
          </div>
        )}

        {activeTab === "classes" && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Classes</h2>
            <table className="w-full text-left">
              <thead>
                <tr className="border-b">
                  <th className="py-2">Class Name</th>
                  <th className="py-2">Display Order</th>
                </tr>
              </thead>
              <tbody>
                {classes.map((c, i) => (
                  <tr key={i} className="border-b">
                    <td className="py-2">{c.name}</td>
                    <td className="py-2">{c.display_order}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <button className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              + Add Class
            </button>
          </div>
        )}

        {activeTab === "sections" && (
          <div className="text-gray-500 italic">Section management coming soon...</div>
        )}
        {activeTab === "subjects" && (
          <div className="text-gray-500 italic">Subject management coming soon...</div>
        )}
      </div>
    </div>
  );
}
