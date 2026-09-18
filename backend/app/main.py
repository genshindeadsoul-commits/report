from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

from app.routes import reports, config, students, profiles, imports

app = FastAPI(
    title="Student Performance Report Generator",
    description="Generates professional student performance reports (PDF & Word) from form input or bulk Excel upload.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to the deployed frontend origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def all_exceptions_handler(request: Request, exc: Exception):
    # Never leak a Python stack trace to a teacher using the app.
    return JSONResponse(
        status_code=500,
        content={"error": "Something went wrong. Please try again, or contact support if the problem continues."},
    )


app.include_router(reports.router, prefix="/api", tags=["reports"])
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(students.router, prefix="/api", tags=["students"])
app.include_router(profiles.router, prefix="/api", tags=["profiles"])
app.include_router(imports.router, prefix="/api", tags=["imports"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
