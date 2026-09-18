from typing import List, Dict, Any, Tuple
import numpy as np

class ProfileMatcher:
    """
    Matches a workbook's structure against an Import Profile.
    Calculates compatibility and detects structural differences.
    """

    def __init__(self, profile: Dict[str, Any], inspection: Dict[str, Any]):
        self.profile = profile
        self.inspection = inspection

    def calculate_match(self) -> Dict[str, Any]:
        # 1. Check sheet compatibility
        matching_sheet = None
        for sheet in self.inspection["sheets"]:
            if sheet["sheet_name"] == self.profile.get("expected_sheet"):
                matching_sheet = sheet
                break

        if not matching_sheet:
            return {
                "score": 0.0,
                "status": "weak",
                "message": "Expected sheet not found in workbook",
                "diffs": {"missing": ["Sheet match"]}
            }

        # 2. Compare field mappings
        profile_mappings = self.profile.get("mappings", {})
        current_headers = matching_sheet["header_candidates"][0]["values"]

        matched = []
        changed = []
        missing = []
        new = []

        # We check for each expected field in the profile
        for field_name, expected_index in profile_mappings.items():
            try:
                actual_val = current_headers[int(expected_index)]
                # In a real app, we'd normalize both strings and compare
                # For now, we assume a match if the value exists at that index
                # or if the value matches the field name.
                if actual_val and (field_name.lower() in str(actual_val).lower()):
                    matched.append(field_name)
                else:
                    changed.append({"field": field_name, "expected": "match", "actual": actual_val})
            except (IndexError, TypeError):
                missing.append(field_name)

        # Detect new columns
        for i, val in enumerate(current_headers):
            if val and not any(str(idx) == str(i) for idx in profile_mappings.values()):
                new.append({"index": i, "value": val})

        # Calculate score
        total_expected = len(profile_mappings)
        if total_expected == 0:
            score = 0.0
        else:
            score = len(matched) / total_expected

        status = "strong" if score >= 0.95 else "moderate" if score >= 0.75 else "weak"

        return {
            "score": score,
            "status": status,
            "matched": matched,
            "changed": changed,
            "missing": missing,
            "new": new
        }
