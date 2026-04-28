from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Financial Tracker API")

# Get environment variables
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from routers import expenses, categories, summary, csv_import
from routers import income, sources


# Include routers
app.include_router(categories.router)
app.include_router(expenses.router)
app.include_router(summary.router)
app.include_router(csv_import.router)
app.include_router(income.router)
app.include_router(sources.router)

@app.get("/")
def read_root():
    return {"message": "Financial Tracker API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
