"""
Generates a personalized, teacher-style paragraph from a student's actual
data — no AI required. To avoid every student reading identically, sentence
variants are picked using a hash of the student's own data (name + roll +
percentage) so the same student always gets the same phrasing on re-runs,
but different students land on different phrasing.

If AI is enabled (see ai_enhancer.py), this deterministic text is used as
the base and AI is only asked to polish tone/flow — it never invents facts.
"""

import hashlib
from typing import Dict, Optional


def _pick(options, seed_key: str, index: int = 0):
    """Deterministically pick one of `options` based on a hash of seed_key,
    offset by `index` so multiple picks for the same student diverge."""
    digest = hashlib.sha256(f"{seed_key}:{index}".encode()).hexdigest()
    n = int(digest, 16)
    return options[n % len(options)]


PERFORMANCE_OPENERS = {
    "Outstanding": [
        "{name} has delivered an outstanding academic performance this {period}",
        "{name} has excelled academically this {period}, achieving outstanding results",
    ],
    "Very Good": [
        "{name} has demonstrated very good academic performance during the {period}",
        "{name} has performed very well academically this {period}",
    ],
    "Good": [
        "{name} has shown good academic performance this {period}",
        "{name} has put in a solid academic effort this {period}",
    ],
    "Satisfactory": [
        "{name} has maintained a satisfactory level of academic performance this {period}",
        "{name}'s academic performance this {period} has been satisfactory",
    ],
    "Needs Improvement": [
        "{name}'s academic performance this {period} indicates room for improvement",
        "{name} has struggled somewhat academically this {period} and would benefit from extra support",
    ],
    "Requires Significant Improvement": [
        "{name}'s academic performance this {period} requires significant improvement and focused attention",
        "{name} needs considerable additional support to strengthen academic performance this {period}",
    ],
}

STRENGTH_PHRASES = [
    "with particular strength in {subject}",
    "showing especially strong results in {subject}",
    "excelling notably in {subject}",
]

PARTICIPATION_PHRASES = {
    "Very Active": ["participates very actively in classroom activities", "is highly engaged during class"],
    "Active": ["participates actively in classroom activities", "engages well during lessons"],
    "Moderate": ["participates moderately in classroom activities", "engages with class activities from time to time"],
    "Low": ["has limited participation in classroom activities", "is encouraged to engage more actively in class"],
}

BEHAVIOUR_PHRASES = {
    "Excellent": ["maintains excellent behaviour", "consistently displays excellent conduct"],
    "Good": ["maintains good behaviour", "displays good conduct in class"],
    "Satisfactory": ["maintains satisfactory behaviour", "generally behaves appropriately in class"],
    "Needs Attention": ["needs to work on classroom behaviour", "would benefit from closer attention to classroom conduct"],
}

ATTENDANCE_PHRASES = {
    "Excellent attendance": ["reflects excellent regularity", "shows a strong commitment to regular attendance"],
    "Good attendance": ["reflects good regularity", "shows consistent attendance habits"],
    "Satisfactory attendance": ["reflects satisfactory regularity", "shows generally consistent attendance"],
    "Attendance requires attention": ["needs attention going forward", "should be improved in the coming term"],
}

HOMEWORK_PHRASES = {
    "Consistent": ["continue putting in consistent effort across all subjects", "keep up consistent, reliable homework habits"],
    "Usually Complete": ["continue completing homework regularly", "maintain the current level of homework consistency"],
    "Sometimes Incomplete": ["work on completing homework more consistently", "pay closer attention to completing homework on time"],
    "Needs Improvement": ["focus on completing homework consistently going forward", "build a more regular homework routine"],
}

FOCUS_PHRASES = [
    "is encouraged to devote additional attention to {subject}",
    "would benefit from extra practice in {subject}",
    "should focus on strengthening skills in {subject}",
]


def generate_remark(
    name: str,
    percentage: float,
    strong_subject: str,
    focus_subject: str,
    attendance_pct: float,
    overall_performance: str,
    participation: str,
    behaviour: str,
    homework: str,
    teacher_remark: Optional[str] = None,
    period: str = "academic year",
) -> str:
    """Builds a personalized paragraph from the student's actual data.
    `teacher_remark` (the teacher's free-text note, if any) is appended as
    a closing sentence rather than replacing the generated analysis."""

    seed = f"{name}|{percentage}|{strong_subject}|{focus_subject}"
    # No gender field is collected, so the student's first name is reused
    # instead of guessing a pronoun.
    first_name = name.strip().split(" ")[0] if name.strip() else "The student"
    pronoun = first_name

    opener_options = PERFORMANCE_OPENERS.get(overall_performance, PERFORMANCE_OPENERS["Satisfactory"])
    opener = _pick(opener_options, seed, 0).format(name=name, period=period)

    strength = _pick(STRENGTH_PHRASES, seed, 1).format(subject=strong_subject)

    participation_phrase = _pick(
        PARTICIPATION_PHRASES.get(participation, PARTICIPATION_PHRASES["Moderate"]), seed, 2
    )
    behaviour_phrase = _pick(
        BEHAVIOUR_PHRASES.get(behaviour, BEHAVIOUR_PHRASES["Satisfactory"]), seed, 3
    )
    attendance_label = "Excellent attendance" if attendance_pct >= 95 else (
        "Good attendance" if attendance_pct >= 90 else (
            "Satisfactory attendance" if attendance_pct >= 80 else "Attendance requires attention"
        )
    )
    attendance_phrase = _pick(ATTENDANCE_PHRASES[attendance_label], seed, 4)
    homework_phrase = _pick(HOMEWORK_PHRASES.get(homework, HOMEWORK_PHRASES["Usually Complete"]), seed, 5)
    focus_phrase = _pick(FOCUS_PHRASES, seed, 6).format(subject=focus_subject)

    sentences = [
        f"{opener}, {strength}.",
        f"{pronoun} {participation_phrase} and {behaviour_phrase}.",
        f"{pronoun}'s attendance of {attendance_pct:.0f}% {attendance_phrase}.",
        f"{pronoun} {focus_phrase}. In addition, {pronoun} should {homework_phrase}.",
    ]

    paragraph = " ".join(sentences)

    if teacher_remark and teacher_remark.strip():
        paragraph += f" Teacher's note: {teacher_remark.strip()}"

    return paragraph
