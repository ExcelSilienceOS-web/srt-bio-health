from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core_biometrics import SRTBiometricEngine
import uvicorn

app = FastAPI(
    title="SRT Bio-Health & Mobility API",
    description="API de Triagem Telemétrica de Prontidão Operacional em Alta Velocidade",
    version="4.2.0"
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
        "system": "ExcelSilience SRT Bio-Health Core (High-Speed Engine)",
        "version": "4.2.0"
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
