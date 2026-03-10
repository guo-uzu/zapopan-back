import io
from typing import List, Literal

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://atencion-al-usuario.uzu.digital",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReportItem(BaseModel):
    id: int
    name: str
    n_reports: int

class ChartRequest(BaseModel):
    title: str
    dateFrom: str
    dateTo: str
    data: List[ReportItem]
    formatFile: Literal["png", "pdf", "svg", "jpeg"]

@app.post("/api/create-chart")
def create_chart(req: ChartRequest):
    if not req.data:
        raise HTTPException(status_code=400, detail="No hay datos para graficar")

    x_axis = [i.name for i in req.data]
    y_axis = [i.n_reports for i in req.data]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(x_axis, y_axis, color="#00c0ff")
    ax.bar_label(bars, fmt="%.0f")
    ax.set_ylabel("Reportes")
    ax.set_title(req.title)

    if len(req.data) > 3:
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format=req.formatFile, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)

    media_types = {
        "png": "image/png",
        "pdf": "application/pdf",
        "svg": "image/svg+xml",
        "jpeg": "image/jpeg",
    }

    return StreamingResponse(buf, media_type=media_types[req.formatFile])