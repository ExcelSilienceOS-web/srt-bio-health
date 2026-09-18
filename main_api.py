from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core_biometrics import SRTBiometricEngine
import uvicorn

app = FastAPI(
    title="SRT Bio-Health & Mobility API",
    description="API de Triagem Telemétrica de Prontidão Operacional",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = SRTBiometricEngine()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "ExcelSilience SRT Bio-Health Core",
        "version": "4.0.0"
    }

@app.post("/api/v1/telemetry/checkin")
async def process_checkin(
    file: UploadFile = File(...),
    user_id: str = Form("ANON_OPERATOR"),
    sector_id: str = Form("DEFAULT_SECTOR")
):
    try:
        content = await file.read()
        result = engine.process_audio_signal(content, file.filename)
        return {
            "user_id": user_id,
            "sector_id": sector_id,
            "filename": file.filename,
            "telemetry": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/smartwatch/sync")
async def sync_smartwatch(
    user_id: str,
    hrv_rmssd: float,
    resting_hr: float,
    sleep_hours: float,
    age: int = 35
):
    result = engine.process_smartwatch_data(hrv_rmssd, resting_hr, sleep_hours, age)
    return {
        "user_id": user_id,
        "smartwatch_analysis": result
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

