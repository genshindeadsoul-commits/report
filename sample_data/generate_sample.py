"""
Generates sample_data/students.xlsx — 10 fictional students with
deliberately varied performance so the report generator visibly produces
different reports for different students (per spec section 25).

Run: python generate_sample.py
"""

import pandas as pd
import os

STUDENTS = [
    # Excellent, high-attendance student
    dict(name="Aarav Sharma", cls="8", section="A", roll="801", year="2026-27",
         english=78, maths=91, science=86, social=82, hindi=88,
         working=180, present=170, perf="Very Good", part="Active",
         behaviour="Excellent", hw="Consistent",
         remark="Good student, improve written English."),
    # Outstanding across the board
    dict(name="Diya Patel", cls="8", section="A", roll="802", year="2026-27",
         english=95, maths=97, science=94, social=93, hindi=90,
         working=180, present=178, perf="Outstanding", part="Very Active",
         behaviour="Excellent", hw="Consistent", remark="Exemplary student."),
    # Average / satisfactory student
    dict(name="Rahul Kumar", cls="8", section="B", roll="803", year="2026-27",
         english=62, maths=58, science=64, social=60, hindi=66,
         working=180, present=160, perf="Satisfactory", part="Moderate",
         behaviour="Good", hw="Usually Complete", remark=""),
    # Poor attendance, otherwise decent marks
    dict(name="Ananya Iyer", cls="8", section="B", roll="804", year="2026-27",
         english=74, maths=70, science=76, social=72, hindi=78,
         working=180, present=128, perf="Good", part="Active",
         behaviour="Good", hw="Usually Complete",
         remark="Frequent absences are affecting continuity."),
    # Significantly improving student
    dict(name="Kabir Singh", cls="8", section="A", roll="805", year="2026-27",
         english=68, maths=75, science=72, social=70, hindi=74,
         working=180, present=172, perf="Good", part="Active",
         behaviour="Good", hw="Usually Complete",
         remark="Marked improvement since last term."),
    # One strong subject, weak elsewhere
    dict(name="Meera Nair", cls="8", section="B", roll="806", year="2026-27",
         english=55, maths=96, science=58, social=52, hindi=60,
         working=180, present=165, perf="Satisfactory", part="Moderate",
         behaviour="Satisfactory", hw="Sometimes Incomplete",
         remark="Gifted in Mathematics; needs support in languages."),
    # Requires significant improvement
    dict(name="Ravi Verma", cls="8", section="A", roll="807", year="2026-27",
         english=35, maths=28, science=40, social=38, hindi=45,
         working=180, present=122, perf="Needs Improvement", part="Low",
         behaviour="Needs Attention", hw="Needs Improvement",
         remark="Requires close monitoring and additional support."),
    # Very good, well-rounded
    dict(name="Sara Khan", cls="8", section="B", roll="808", year="2026-27",
         english=85, maths=83, science=88, social=84, hindi=80,
         working=180, present=174, perf="Very Good", part="Active",
         behaviour="Excellent", hw="Consistent", remark=""),
    # Good student, moderate attendance
    dict(name="Arjun Reddy", cls="8", section="A", roll="809", year="2026-27",
         english=71, maths=74, science=69, social=73, hindi=76,
         working=180, present=155, perf="Good", part="Moderate",
         behaviour="Good", hw="Usually Complete",
         remark="Should aim for more consistent attendance."),
    # Declining performance, flagged for attention
    dict(name="Priya Desai", cls="8", section="B", roll="810", year="2026-27",
         english=50, maths=46, science=52, social=48, hindi=55,
         working=180, present=140, perf="Needs Improvement", part="Low",
         behaviour="Satisfactory", hw="Sometimes Incomplete",
         remark="Performance has dipped compared to last term; recommend a parent meeting."),
]

rows = []
for s in STUDENTS:
    working, present = s["working"], s["present"]
    rows.append({
        "Student Name": s["name"], "Class": s["cls"], "Section": s["section"],
        "Roll Number": s["roll"], "Academic Year": s["year"],
        "English": s["english"], "Mathematics": s["maths"], "Science": s["science"],
        "Social Science": s["social"], "Hindi": s["hindi"],
        "Working Days": working, "Present Days": present, "Absent Days": working - present,
        "Academic Performance": s["perf"], "Class Participation": s["part"],
        "Behaviour": s["behaviour"], "Homework": s["hw"], "Teacher Remark": s["remark"],
    })

df = pd.DataFrame(rows)
out_path = os.path.join(os.path.dirname(__file__), "students.xlsx")
df.to_excel(out_path, index=False, sheet_name="Students")
print(f"Wrote {out_path} with {len(df)} students")
