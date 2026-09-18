import Link from "next/link";

export default function Home() {
  return (
    <main className="max-w-4xl mx-auto px-6 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl md:text-4xl font-bold text-primary mb-3">
          Student Report Generator
        </h1>
        <p className="text-slate-600 text-lg">
          Generate professional, personalized student performance reports in
          seconds — no manual calculations, no repetitive writing.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 gap-6 mb-12">
        <Link
          href="/create"
          className="card p-8 hover:shadow-md transition-shadow text-center group"
        >
          <div className="text-4xl mb-3">📝</div>
          <h2 className="text-xl font-semibold mb-2 group-hover:text-primary">
            Create Report
          </h2>
          <p className="text-slate-500 text-sm">
            Enter one student&apos;s details through a simple form.
          </p>
        </Link>

        <Link
          href="/upload"
          className="card p-8 hover:shadow-md transition-shadow text-center group"
        >
          <div className="text-4xl mb-3">📊</div>
          <h2 className="text-xl font-semibold mb-2 group-hover:text-primary">
            Upload Excel
          </h2>
          <p className="text-slate-500 text-sm">
            Upload a class spreadsheet and generate reports for every
            student at once.
          </p>
        </Link>
      </div>

      <div className="card p-6">
        <h3 className="font-semibold mb-1">How it works</h3>
        <ol className="text-sm text-slate-600 list-decimal list-inside space-y-1 mt-2">
          <li>Enter marks and attendance, or upload an Excel file.</li>
          <li>
            Percentages, grades, strengths, and insights are calculated
            automatically.
          </li>
          <li>A personalized report paragraph is generated for you.</li>
          <li>Review and edit the remark if you&apos;d like.</li>
          <li>Download as PDF or Word — individually or in bulk.</li>
        </ol>
      </div>
    </main>
  );
}
