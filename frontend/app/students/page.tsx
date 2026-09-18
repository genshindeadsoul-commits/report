"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";

interface StudentRecord {
  admission_number: string;
  full_name: string;
  email?: string;
  status: string;
}

export default function StudentsPage() {
  const { user } = useAuth();
  const [students, setStudents] = useState<StudentRecord[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch("/api/students").then(res => res.json()).then(setStudents);
  }, []);

  const filteredStudents = students.filter(s =>
    s.full_name.toLowerCase().includes(search.toLowerCase()) ||
    s.admission_number.toLowerCase().includes(search.toLowerCase())
  );

  if (!user || (user.role !== "admin" && user.role !== "teacher")) {
    return (
      <div className="p-8 text-center">
        <h1 className="text-2xl font-bold text-red-600">Access Denied</h1>
        <p>You do not have permission to view student records.</p>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Students</h1>
        {user.role === "admin" && (
          <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            + Add Student
          </button>
        )}
      </div>

      <div className="mb-6">
        <input
          type="text"
          placeholder="Search by name or admission number..."
          className="w-full p-2 border rounded-lg"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="p-4 font-semibold">Admission No</th>
              <th className="p-4 font-semibold">Full Name</th>
              <th className="p-4 font-semibold">Email</th>
              <th className="p-4 font-semibold">Status</th>
              <th className="p-4 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredStudents.map((s, i) => (
              <tr key={i} className="border-b hover:bg-gray-50">
                <td className="p-4">{s.admission_number}</td>
                <td className="p-4">{s.full_name}</td>
                <td className="p-4">{s.email || "N/A"}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs ${s.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {s.status}
                  </span>
                </td>
                <td className="p-4">
                  <button className="text-blue-600 hover:underline mr-4">Edit</button>
                  <button className="text-gray-600 hover:underline">Enroll</button>
                </td>
              </tr>
            ))}
            {filteredStudents.length === 0 && (
              <tr>
                <td colSpan={5} className="p-8 text-center text-gray-500 italic">
                  No students found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
