# Deployment Guide: Student Report Card System

This guide provides the step-by-step procedure to move the system from local development to a live production environment.

## 🏗️ Architecture Summary
- **Database & Auth**: Supabase (PostgreSQL + GoTrue)
- **Backend API**: FastAPI (Python)
- **Frontend**: Next.js (TypeScript)

---

## Step 1: Set Up Supabase (Database & Auth)

1.  **Create a Project**: Log in to [Supabase](https://supabase.com/) and create a new project.
2.  **Run Migrations**:
    *   Go to the **SQL Editor** in the Supabase dashboard.
    *   Copy the contents of `supabase/migrations/01_init_schema.sql` and run it.
    *   Copy the contents of `supabase/migrations/02_rls_policies.sql` and run it.
    *   Copy the contents of `supabase/migrations/03_auth_triggers.sql` and run it.
3.  **Get API Keys**:
    *   Go to **Project Settings** $\rightarrow$ **API**.
    *   Copy the `Project URL` and the `anon` (public) key.
    *   Copy the `service_role` secret (keep this private!).

---

## Step 2: Deploy the Backend (FastAPI)

You can use platforms like **Render**, **Railway**, or **Fly.io**.

1.  **Connect GitHub**: Connect your GitHub repository to the hosting provider.
2.  **Build Command**: `pip install -r backend/requirements.txt`
3.  **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4.  **Environment Variables**: Set the following in your hosting provider's dashboard:
    *   `SUPABASE_URL`: Your Supabase Project URL.
    *   `SUPABASE_ANON_KEY`: Your Supabase anon key.
    *   `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service_role key.
    *   `SUPABASE_JWT_SECRET`: Your Supabase JWT Secret (found in API settings).

---

## Step 3: Deploy the Frontend (Next.js)

The best choice for Next.js is **Vercel** or **Netlify**.

1.  **Connect GitHub**: Connect your GitHub repository to Vercel/Netlify.
2.  **Root Directory**: Set the root directory to `frontend`.
3.  **Build Command**: `npm run build`
4.  **Environment Variables**: Set the following:
    *   `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase Project URL.
    *   `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Your Supabase anon key.
    *   `NEXT_PUBLIC_API_BASE_URL`: The URL of your deployed Backend API (e.g., `https://api.your-app.render.com/api`).

---

## Step 4: Final Verification

1.  **Login**: Try logging in via the frontend.
2.  **Config**: Log in as an Admin and create an **Academic Year** and a **Class**.
3.  **Import**: Upload a sample Excel file, create an **Import Profile**, and commit the data.
4.  **Generate**: Preview a student's report and download the PDF.

## 🛠️ Troubleshooting

| Issue | Solution |
|---|---|
| **401 Unauthorized** | Ensure your `SUPABASE_JWT_SECRET` is correctly set in the backend. |
| **PDF not generating** | Check that `reportlab` is installed in the backend requirements. |
| **CORS Error** | Ensure the `allow_origins` in `backend/app/main.py` includes your frontend URL. |
| **RLS Denied** | Verify that the user role is set to `admin` or `teacher` in the `profiles` table. |
