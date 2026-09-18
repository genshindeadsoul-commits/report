"""
Supabase client wiring.

Option-A scope: a single flat `student_reports` table (see
supabase/migrations/04_student_reports.sql) backs the report
snapshot/publish/lock flow. The full normalized academic schema in
01_init_schema.sql through 03_auth_triggers.sql already exists in the
database but is not yet used by the application code — that's the
profile-based import system, a later milestone.

get_client() raises a clear error at call time (not at import time) if
the required environment variables are missing, so the rest of the app
can still start up and serve non-DB endpoints even before Supabase is
configured.
"""

import os
from functools import lru_cache

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


class SupabaseNotConfiguredError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        raise SupabaseNotConfiguredError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set (see backend/.env.example). "
            "Copy backend/.env.example to backend/.env and fill in your Supabase project's "
            "values from Project Settings -> API."
        )

    return create_client(url, key)
