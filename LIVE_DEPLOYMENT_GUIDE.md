# 🚀 FULL PRODUCTION DEPLOYMENT GUIDE (LOCAL COPY)

This is the absolute, minute-by-minute guide to taking the system from GitHub to a live URL.

## Phase 1: Supabase (The Database & Auth)
Supabase handles your users, your academic data, and your security.

1.  **Create Account**: Go to [supabase.com](https://supabase.com) and sign up/log in.
2.  **Create Project**:
    *   Click **"New Project"** $\rightarrow$ Select an Organization.
    *   **Name**: `Student Report System`
    *   **Database Password**: Create a strong password. **Save this in a notepad; you will need it.**
    *   **Region**: Pick the one closest to your users.
    *   Click **"Create new project"** and wait 2–5 minutes for the database to provision.
3.  **Run SQL Migrations**:
    *   On the left sidebar, click the **SQL Editor** icon (looks like `>_`).
    *   Click **"+ New query"**.
    *   **File 1**: Open your local file `supabase/migrations/01_init_schema.sql`. Copy all text $\rightarrow$ Paste into the editor $\rightarrow$ Click **"Run"**.
    *   **File 2**: Click **"+ New query"**. Open `supabase/migrations/02_rls_policies.sql`. Copy all text $\rightarrow$ Paste $\rightarrow$ Click **"Run"**.
    *   **File 3**: Click **"+ New query"**. Open `supabase/migrations/03_auth_triggers.sql`. Copy all text $\rightarrow$ Paste $\rightarrow$ Click **"Run"**.
4.  **Gather Your Keys**:
    *   Go to **Project Settings** (gear icon) $\rightarrow$ **API**.
    *   **Copy these 4 values to your notepad:**
        1.  `Project URL` (e.g., `https://xyz.supabase.co`)
        2.  `anon` public key
        3.  `service_role` secret (Keep this very secret!)
        4.  `JWT Secret` (You may need to click "Reveal" to see it).

---

## Phase 2: Render (The Backend API)
Render hosts your Python FastAPI server.

1.  **Account**: Log in to [render.com](https://render.com) using your GitHub account.
2.  **Create Service**:
    *   Click **"New +"** $\rightarrow$ **"Web Service"**.
    *   Connect your GitHub account and select the `genshindeadsoul-commits/report` repository.
3.  **Configuration**:
    *   **Name**: `student-report-api`
    *   **Region**: Same as your Supabase region.
    *   **Branch**: `main`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r backend/requirements.txt`
    *   **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
4.  **Environment Variables**:
    *   Click the **"Advanced"** button or the **"Env Vars"** tab.
    *   Add these exactly:
        *   `SUPABASE_URL` $\rightarrow$ (Your Project URL from Phase 1)
        *   `SUPABASE_ANON_KEY` $\rightarrow$ (Your anon key)
        *   `SUPABASE_SERVICE_ROLE_KEY` $\rightarrow$ (Your service_role key)
        *   `SUPABASE_JWT_SECRET` $\rightarrow$ (Your JWT Secret)
5.  **Deploy**: Click **"Create Web Service"**.
6.  **Test**: Once the log says `Application startup complete`, copy the Render URL (e.g., `https://student-report-api.onrender.com`) and add `/api/health` to the end. If it says `{"status": "ok"}`, your backend is live!

---

## Phase 3: Vercel (The Frontend UI)
Vercel hosts your Next.js website.

1.  **Account**: Log in to [vercel.com](https://vercel.com) using GitHub.
2.  **Create Project**:
    *   Click **"Add New..."** $\rightarrow$ **"Project"**.
    *   Import the `genshindeadsoul-commits/report` repository.
3.  **CRITICAL SETTING (Root Directory)**:
    *   In the "Configure Project" screen, look for **"Root Directory"**.
    *   Click **"Edit"** and select the `frontend` folder. **If you skip this, the build will fail.**
4.  **Environment Variables**:
    *   Expand the **"Environment Variables"** section.
    *   Add these:
        *   `NEXT_PUBLIC_SUPABASE_URL` $\rightarrow$ (Your Supabase Project URL)
        *   `NEXT_PUBLIC_SUPABASE_ANON_KEY` $\rightarrow$ (Your Supabase anon key)
        *   `NEXT_PUBLIC_API_BASE_URL` $\rightarrow$ (Your Render URL + `/api`, e.g., `https://student-report-api.onrender.com/api`)
5.  **Deploy**: Click **"Deploy"**.
6.  **Live URL**: Vercel will give you a URL (e.g., `student-report-system.vercel.app`). This is your final website link.

---

## Phase 4: Final Activation (Making yourself Admin)
By default, new users are 'students'. You need to manually promote yourself to 'admin' to use the config tools.

1.  **Sign Up**: Go to your new Vercel URL and create an account (Sign Up).
2.  **Change Role in DB**:
    *   Go back to **Supabase** $\rightarrow$ **Table Editor** (grid icon).
    *   Click on the `profiles` table.
    *   Find your user email/ID.
    *   Double-click the `role` column and change `student` to `admin`.
    *   Click **"Save"**.
3.  **Refresh**: Refresh your Vercel website. You now have full access to the Admin Dashboard, Profile Builder, and Config pages.

### ✅ Checklist for Success
- [ ] Supabase SQL ran without errors.
- [ ] Render logs show "Application startup complete".
- [ ] Vercel "Root Directory" is set to `frontend`.
- [ ] User role is changed to `admin` in Supabase.
