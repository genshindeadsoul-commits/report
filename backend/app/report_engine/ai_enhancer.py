"""
Optional AI enhancement layer. The application works fully without this —
every function here is a pure add-on that takes the already-computed,
already-correct student summary and asks an LLM only to improve the prose
of the teacher's observation. The AI is never given raw marks to calculate
with and never asked to produce grades, percentages, or classifications.

If ANTHROPIC_API_KEY / OPENAI_API_KEY is not set, `is_ai_available()`
returns False and callers should fall back to the deterministic remark from
remark.py untouched.
"""

import os
import json
from typing import Dict, Optional


def is_ai_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY"))


def build_ai_payload(
    student_name: str,
    percentage: float,
    grade: str,
    attendance: float,
    strong_subject: str,
    focus_subject: str,
    performance: str,
    participation: str,
    behaviour: str,
    homework: str,
    teacher_remark: Optional[str],
) -> Dict:
    """Exactly the processed-only payload described in the spec — no raw
    subject-by-subject marks, so the AI cannot be tempted to recompute
    anything."""
    return {
        "student": student_name,
        "percentage": percentage,
        "grade": grade,
        "attendance": attendance,
        "strong_subject": strong_subject,
        "focus_subject": focus_subject,
        "performance": performance,
        "participation": participation,
        "behaviour": behaviour,
        "homework": homework,
        "teacher_remark": teacher_remark or "",
    }


def enhance_remark_with_ai(base_remark: str, payload: Dict) -> str:
    """Calls the configured LLM provider to rewrite `base_remark` in a
    warmer, more natural teacher voice — using only the facts in `payload`.
    Falls back to `base_remark` unchanged on any error or missing key.

    This function intentionally does NOT import an SDK at module load time,
    so the rest of the app has zero hard dependency on any AI package.
    """
    if not is_ai_available():
        return base_remark

    system_prompt = (
        "You are a school teacher's assistant. Rewrite the given report "
        "paragraph in warm, professional teacher language. Use ONLY the "
        "facts provided in the JSON payload — do not invent marks, grades, "
        "attendance figures, or subjects. Keep it to one paragraph, 3-5 "
        "sentences. Return plain text only, no markdown."
    )
    user_prompt = (
        f"Student data:\n{json.dumps(payload, indent=2)}\n\n"
        f"Draft paragraph to improve:\n{base_remark}"
    )

    try:
        if os.environ.get("ANTHROPIC_API_KEY"):
            import anthropic
            client = anthropic.Anthropic()
            resp = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=400,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = "".join(
                block.text for block in resp.content if getattr(block, "type", "") == "text"
            )
            return text.strip() or base_remark

        elif os.environ.get("OPENAI_API_KEY"):
            import openai
            client = openai.OpenAI()
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=400,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            text = resp.choices[0].message.content
            return (text or "").strip() or base_remark

    except Exception:
        # Any AI failure must never break report generation.
        return base_remark

    return base_remark
