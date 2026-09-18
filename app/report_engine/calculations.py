"""
Authoritative calculation engine for academic results.
Uses Decimal for high-precision arithmetic to avoid floating-point quirks.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Any, Optional
from .config import GradingConfig, band_lookup, DEFAULT_CONFIG

class CalculationEngine:
    def __init__(self, config: GradingConfig = DEFAULT_CONFIG):
        self.config = config

    def _to_decimal(self, value: Any) -> Decimal:
        if value is None:
            return Decimal("0.00")
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calculate_subject_metrics(self, marks: float, max_marks: float) -> Dict[str, Any]:
        m = self._to_decimal(marks)
        mx = self._to_decimal(max_marks)

        pct = Decimal("0.00")
        if mx > 0:
            pct = (m / mx * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        pct_float = float(pct)
        return {
            "marks": m,
            "max_marks": mx,
            "percentage": pct_float,
            "grade": band_lookup(pct_float, self.config.grade_bands),
            "performance": band_lookup(pct_float, self.config.performance_bands),
        }

    def calculate_overall_metrics(self, subject_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates totals and overall grades from a list of subject metrics.
        subject_data: List of {marks, max_marks}
        """
        total_marks = Decimal("0.00")
        total_max = Decimal("0.00")

        for s in subject_data:
            total_marks += self._to_decimal(s.get("marks", 0))
            total_max += self._to_decimal(s.get("max_marks", 0))

        overall_pct = Decimal("0.00")
        if total_max > 0:
            overall_pct = (total_marks / total_max * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        overall_pct_float = float(overall_pct)
        return {
            "total_marks": float(total_marks),
            "total_max": float(total_max),
            "overall_percentage": overall_pct_float,
            "overall_grade": band_lookup(overall_pct_float, self.config.grade_bands),
            "overall_performance": band_lookup(overall_pct_float, self.config.performance_bands),
        }

    def calculate_attendance_metrics(self, present_days: float, working_days: float) -> Dict[str, Any]:
        p = self._to_decimal(present_days)
        w = self._to_decimal(working_days)

        pct = Decimal("0.00")
        if w > 0:
            pct = (p / w * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        pct_float = float(pct)
        return {
            "present_days": float(p),
            "working_days": float(w),
            "absent_days": float(w - p),
            "percentage": pct_float,
            "status": band_lookup(pct_float, self.config.attendance_bands),
        }
