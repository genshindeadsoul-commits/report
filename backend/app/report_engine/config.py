"""
Central configuration for grading rules, performance bands, and attendance
bands. Keeping these as ordered lists of (threshold, label) tuples makes the
whole grading system easy to tweak later without touching calculation logic.

All thresholds are inclusive lower bounds, checked from highest to lowest.
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class GradingConfig:
    # (minimum percentage, grade label)
    grade_bands: List[Tuple[float, str]] = field(default_factory=lambda: [
        (90, "A+"),
        (80, "A"),
        (70, "B+"),
        (60, "B"),
        (50, "C"),
        (40, "D"),
        (0, "E"),
    ])

    # (minimum percentage, performance label)
    performance_bands: List[Tuple[float, str]] = field(default_factory=lambda: [
        (90, "Outstanding"),
        (80, "Very Good"),
        (70, "Good"),
        (60, "Satisfactory"),
        (50, "Needs Improvement"),
        (0, "Requires Significant Improvement"),
    ])

    # (minimum attendance percentage, label)
    attendance_bands: List[Tuple[float, str]] = field(default_factory=lambda: [
        (95, "Excellent attendance"),
        (90, "Good attendance"),
        (80, "Satisfactory attendance"),
        (0, "Attendance requires attention"),
    ])

    school_name: str = "AECS MAGNOLIA SCHOOL"
    academic_year: str = "2026-27"
    logo_path: str = ""  # optional path to a logo image
    primary_color_hex: str = "#1F4E8C"  # school-report blue
    accent_color_hex: str = "#EAF1FB"


DEFAULT_CONFIG = GradingConfig()


def band_lookup(value: float, bands: List[Tuple[float, str]]) -> str:
    """Return the label for the first band whose threshold <= value,
    scanning bands from highest threshold to lowest."""
    for threshold, label in sorted(bands, key=lambda b: -b[0]):
        if value >= threshold:
            return label
    return bands[-1][1]
