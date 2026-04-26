import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env variables
load_dotenv()

from api.routes import router as chat_router
from services.rag import init_rag

app = FastAPI(title="College Admission Assistant API")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG on startup
@app.on_event("startup")
async def startup_event():
    # Update the path below to point to the actual location of your CSV file
    csv_path = os.path.join("data", "college_admission_dataset_5k.csv") 
    if os.path.exists(csv_path):
        init_rag(csv_path)
    else:
        print(f"Warning: CSV file not found at {csv_path}. RAG will not be initialized.")

# Include router
app.include_router(chat_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the College Admission Assistant API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
