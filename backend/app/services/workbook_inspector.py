import pandas as pd
from openpyxl import load_workbook
from typing import List, Dict, Any, Optional
import numpy as np

class WorkbookInspector:
    """
    Analyzes an Excel workbook to identify its structure, headers, and data patterns.
    This service is the first step in the Import Profile workflow.
    """

    def __init__(self, file_bytes: bytes):
        self.file_bytes = file_bytes
        self.wb = load_workbook(io.BytesIO(file_bytes), data_only=True)

    def inspect(self) -> Dict[str, Any]:
        return {
            "sheets": self._inspect_sheets(),
            "metadata": {
                "sheet_count": len(self.wb.sheetnames),
                "workbook_name": "Uploaded File"
            }
        }

    def _inspect_sheets(self) -> List[Dict[str, Any]]:
        sheet_data = []
        for sheet_name in self.wb.sheetnames:
            sheet = self.wb[sheet_name]

            # Identify used range
            max_row = sheet.max_row
            max_col = sheet.max_column

            # Detect merged cells
            merged_cells = []
            for merged in sheet.merged_cells.ranges:
                merged_cells.append(str(merged))

            # Analyze first few rows to find header candidates
            header_candidates = self._detect_header_candidates(sheet)

            sheet_data.append({
                "sheet_name": sheet_name,
                "dimensions": {
                    "rows": max_row,
                    "cols": max_col
                },
                "merged_cells": merged_cells,
                "header_candidates": header_candidates,
                "sample_rows": self._get_sample_rows(sheet)
            })
        return sheet_data

    def _detect_header_candidates(self, sheet) -> List[Dict[str, Any]]:
        candidates = []
        # Check the first 20 rows as potential headers
        for row_idx in range(1, min(20, sheet.max_row + 1)):
            row_values = []
            for col_idx in range(1, sheet.max_column + 1):
                val = sheet.cell(row=row_idx, column=col_idx).value
                row_values.append(val)

            # A row is a good header candidate if:
            # 1. It has a high percentage of non-empty strings
            # 2. It contains keywords like 'Name', 'Roll', 'Admission', 'Class'
            non_empty = [v for v in row_values if v is not None]
            score = 0
            if len(non_empty) > 0:
                score += len(non_empty) / len(row_values)

                keywords = ['name', 'roll', 'admission', 'class', 'section', 'subject', 'mark']
                for val in non_empty:
                    if isinstance(val, str) and any(k in val.lower() for k in keywords):
                        score += 1

            candidates.append({
                "row": row_idx,
                "values": row_values,
                "score": score
            })

        # Sort by score descending
        return sorted(candidates, key=lambda x: x["score"], reverse=True)[:3]

    def _get_sample_rows(self, sheet) -> List[List[Any]]:
        samples = []
        # Get a few rows after the likely header
        start_row = 2
        for row_idx in range(start_row, min(12, sheet.max_row + 1)):
            row = [sheet.cell(row=row_idx, column=col).value for col in range(1, sheet.max_column + 1)]
            samples.append(row)
        return samples

import io
