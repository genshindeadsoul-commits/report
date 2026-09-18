import pytest
from app.report_engine.calculations import CalculationEngine
from app.report_engine.config import GradingConfig

def test_subject_metrics_perfect_score():
    engine = CalculationEngine()
    result = engine.calculate_subject_metrics(100, 100)
    assert result["percentage"] == 100.0
    assert result["grade"] == "A+"

def test_subject_metrics_zero_score():
    engine = CalculationEngine()
    result = engine.calculate_subject_metrics(0, 100)
    assert result["percentage"] == 0.0
    assert result["grade"] == "E"

def test_subject_metrics_mid_score():
    engine = CalculationEngine()
    # 75/100 = 75% -> B+
    result = engine.calculate_subject_metrics(75, 100)
    assert result["percentage"] == 75.0
    assert result["grade"] == "B+"

def test_overall_metrics():
    engine = CalculationEngine()
    data = [
        {"marks": 80, "max_marks": 100},
        {"marks": 90, "max_marks": 100},
    ]
    result = engine.calculate_overall_metrics(data)
    assert result["total_marks"] == 170.0
    assert result["total_max"] == 200.0
    assert result["overall_percentage"] == 85.0
    assert result["overall_grade"] == "A"

def test_attendance_metrics():
    engine = CalculationEngine()
    result = engine.calculate_attendance_metrics(180, 200)
    assert result["percentage"] == 90.0
    assert result["status"] == "Good attendance"

def test_decimal_precision():
    engine = CalculationEngine()
    # Test a case that often causes floating point issues: 1/3
    # 33.333... should round to 33.33
    result = engine.calculate_subject_metrics(1, 3)
    assert result["percentage"] == 33.33
