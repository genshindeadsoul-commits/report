"""
Turns raw calculated numbers into the automatic insights a teacher would
otherwise have to work out by eye: strongest subject, focus area, overall
performance classification, attendance commentary, and improvement vs a
previous term (when available).
"""

from typing import Dict, List, Optional
from .config import GradingConfig, band_lookup, DEFAULT_CONFIG


def find_strongest_subject(subject_rows: List[Dict]) -> Dict:
    """subject_rows come from calculations.calculate_subject_grades()."""
    return max(subject_rows, key=lambda r: r["percentage"])


def find_focus_subject(subject_rows: List[Dict]) -> Dict:
    return min(subject_rows, key=lambda r: r["percentage"])


def analyze_performance(percentage: float, config: GradingConfig = DEFAULT_CONFIG) -> str:
    return band_lookup(percentage, config.performance_bands)


def analyze_attendance(attendance_pct: float, config: GradingConfig = DEFAULT_CONFIG) -> str:
    return band_lookup(attendance_pct, config.attendance_bands)


def analyze_improvement(
    current_percentage: float,
    previous_percentage: Optional[float],
) -> Optional[Dict]:
    """Returns None if there's no previous-term data to compare against —
    the report should simply omit this section in that case."""
    if previous_percentage is None:
        return None

    diff = round(current_percentage - previous_percentage, 2)
    if diff > 0.5:
        status = "Improved"
    elif diff < -0.5:
        status = "Declined"
    else:
        status = "Stable"

    return {
        "previous_percentage": previous_percentage,
        "current_percentage": current_percentage,
        "difference": diff,
        "status": status,
    }


def build_insights(
    subject_rows: List[Dict],
    percentage: float,
    attendance_pct: float,
    previous_percentage: Optional[float] = None,
    config: GradingConfig = DEFAULT_CONFIG,
) -> Dict:
    """Bundles every automatic insight the report needs into one dict."""
    strongest = find_strongest_subject(subject_rows)
    focus = find_focus_subject(subject_rows)

    return {
        "strongest_subject": strongest,
        "focus_subject": focus,
        "overall_performance": analyze_performance(percentage, config),
        "attendance_analysis": analyze_attendance(attendance_pct, config),
        "improvement": analyze_improvement(percentage, previous_percentage),
    }
