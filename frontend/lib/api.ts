const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

export interface StudentInput {
  name: string;
  class: string;
  section: string;
  roll_number: string;
  academic_year: string;
  subject_marks: Record<string, number>;
  subject_max_marks?: Record<string, number>;
  working_days: number;
  present_days: number;
  academic_performance: string;
  class_participation: string;
  behaviour: string;
  homework: string;
  communication?: string;
  teacher_remark?: string;
  previous_percentage?: number;
}

export interface ReportData {
  student: {
    name: string;
    class_: string;
    section: string;
    roll_number: string;
    academic_year: string;
  };
  summary: {
    total_marks: number;
    max_marks: number;
    percentage: number;
    grade: string;
    performance: string;
  };
  subjects: Array<{
    subject: string;
    marks: number;
    max_marks: number;
    percentage: number;
    grade: string;
    performance: string;
  }>;
  insights: {
    strongest_subject: { subject: string; percentage: number };
    focus_subject: { subject: string; percentage: number };
    overall_performance: string;
    attendance_analysis: string;
    improvement: {
      previous_percentage: number;
      current_percentage: number;
      difference: number;
      status: string;
    } | null;
  };
  attendance: {
    working_days: number;
    present_days: number;
    absent_days: number;
    percentage: number;
  };
  assessment: Record<string, string>;
  observation: string;
  editable_remark: string;
  config: { school_name: string; academic_year: string };
}

async function handleError(res: Response): Promise<never> {
  let detail = `Request failed with status ${res.status}`;
  try {
    const data = await res.json();
    detail = data.detail || data.error || detail;
  } catch {
    // response wasn't JSON; keep the generic message
  }
  throw new Error(detail);
}

async function fetchWithAuth(url: string, options: RequestInit = {}, token?: string) {
  const headers = new Headers(options.headers);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(url, { ...options, headers });
  if (!res.ok) return handleError(res);
  return res;
}

export async function previewReport(
  student: StudentInput,
  useAi = false,
  token?: string
): Promise<ReportData> {
  const res = await fetchWithAuth(
    `${API_BASE}/reports/preview?use_ai=${useAi}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(student),
    },
    token
  );
  return res.json();
}

async function downloadFile(
  path: string,
  body: unknown,
  filenameFallback: string,
  token?: string
) {
  const res = await fetchWithAuth(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }, token);

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filenameFallback;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export function generateDocx(student: StudentInput, observationOverride?: string, token?: string) {
  return downloadFile(
    "/reports/generate/docx",
    { ...student, observation_override: observationOverride },
    `${student.name.replace(/\s+/g, "_")}.docx`,
    token
  );
}

export function generatePdf(student: StudentInput, observationOverride?: string, token?: string) {
  return downloadFile(
    "/reports/generate/pdf",
    { ...student, observation_override: observationOverride },
    `${student.name.replace(/\s+/g, "_")}.pdf`,
    token
  );
}

export async function uploadExcel(file: File, token?: string) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetchWithAuth(`${API_BASE}/reports/upload`, {
    method: "POST",
    body: formData,
  }, token);
  return res.json();
}

export function downloadTemplate(token?: string) {
  // For simple redirects, we might need to use a temporary token or a different method
  // since window.location.href doesn't support headers.
  // In a real app, we'd fetch the file and create a blob.
  return downloadFile("/reports/template", {}, "student_report_template.xlsx", token);
}

export function generateBulkZip(students: StudentInput[], token?: string) {
  return downloadFile("/reports/bulk/zip", students, "student_reports.zip", token);
}

export function generateCombinedPdf(students: StudentInput[], token?: string) {
  return downloadFile(
    "/reports/bulk/combined-pdf",
    students,
    "all_students_combined.pdf",
    token
  );
}
