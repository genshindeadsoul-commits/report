"""Small shared helpers for turning internal errors into teacher-friendly
messages. Kept here so routes/services don't duplicate wording."""

FRIENDLY_MESSAGES = {
    "missing_columns": "Your file is missing some required columns. Please download the template and match its column headers exactly.",
    "empty_file": "The uploaded file doesn't contain any student rows.",
    "corrupted_file": "This file could not be opened. Please re-save it as a standard .xlsx file and try again.",
    "generation_failed": "We couldn't generate the report right now. Please try again.",
}
