import json
import os
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="ExcelSilience SRT API")

# LIBERAÇÃO TOTAL DE CORS (PERMITE CONEXÃO DIRETA DO GITHUB PAGES)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "banco_testes.json"


def carregar_dados():
  if os.path.exists(DB_FILE):
    try:
      with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      return []
  return []


def salvar_dados(dados):
  try:
    with open(DB_FILE, "w", encoding="utf-8") as f:
      json.dump(dados, f, ensure_ascii=False, indent=2)
  except Exception as e:
    print(f"Erro ao salvar arquivo: {e}", flush=True)


@app.get("/")
@app.get("/ping")
def healthcheck():
  dados = carregar_dados()
  return {
      "status": "SRT Bio-Health API Online",
      "total_records": len(dados),
      "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
  }


@app.get("/api/v1/smartwatch/sync")
def get_sync():
  dados = carregar_dados()
  return JSONResponse(content=dados)


@app.post("/api/v1/smartwatch/sync")
async def post_sync(request: Request):
  try:
    body = await request.json()
    print(f"\n🚨 NOVO CHECK-IN RECEBIDO: {body}", flush=True)

    telemetry = body.get("telemetry", {})
    novo_registro = {
        "timestamp": datetime.now().strftime("%H:%M"),
        "date_iso": datetime.now().isoformat(),
        "company": body.get("company", "ExcelSilience Direct"),
        "name": body.get("name", "Operador"),
        "whatsapp": body.get("whatsapp", "N/A"),
        "sector": body.get("sector", "Operacional"),
        "reaction_ms": telemetry.get("reaction_ms", 0),
        "veto_errors": telemetry.get("veto_errors", 0),
        "status": telemetry.get("status", "GREEN"),
    }

    dados = carregar_dados()
    dados.insert(0, novo_registro)
    salvar_dados(dados)

    print(
        f"✅ REGISTRO SALVO COM SUCESSO! Total no banco: {len(dados)}",
        flush=True,
    )
    return JSONResponse(
        content={
            "status": "success",
            "message": "Dados gravados no CCO",
            "data": novo_registro,
        }
    )
  except Exception as e:
    print(f"❌ ERRO AO PROCESSAR POST: {e}", flush=True)
    return JSONResponse(
        content={"status": "error", "message": str(e)}, status_code=500
    )
