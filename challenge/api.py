import fastapi
import pandas as pd
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, validator
from typing import List
from pathlib import Path
from challenge.model import DelayModel

app = fastapi.FastAPI()

model = DelayModel()
data = pd.read_csv(Path(__file__).parent.parent / "data" / "data.csv", low_memory=False)
features, target = model.preprocess(data, target_column="delay")
model.fit(features, target)

class Flight(BaseModel):
    OPERA: str
    TIPOVUELO: str
    MES: int

    @validator("MES")
    def mes_range(cls, v):
        if not 1 <= v <= 12:
            raise ValueError("MES must be between 1 and 12")
        return v

    @validator("TIPOVUELO")
    def tipo_valid(cls, v):
        if v not in ("N", "I"):
            raise ValueError("TIPOVUELO must be N or I")
        return v

    @validator("OPERA")
    def opera_valid(cls, v):
        valid = ["Aerolineas Argentinas", "Aeromexico", "Air Canada", "Air France",
            "Alitalia", "American Airlines", "Austral", "Avianca",
            "British Airways", "Copa Air", "Delta Air", "Gol Trans",
            "Grupo LATAM", "Iberia", "JetSmart SPA", "K.L.M.", "Lacsa",
            "Latin American Wings", "Oceanair Linhas Aereas",
            "Plus Ultra Lineas Aereas", "Qantas Airways", "Sky Airline",
            "United Airlines"]
        if v not in valid:
            raise ValueError(f"Invalid airline: {v}")
        return v

class PredictRequest(BaseModel):
    flights: List[Flight]

@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }

@app.post("/predict", status_code=200)
async def post_predict(request: PredictRequest) -> dict:
    df = pd.DataFrame([f.dict() for f in request.flights])
    features = model.preprocess(df)
    predictions = model.predict(features)
    return {"predict": predictions}
