import io
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic.main import BaseModel
import matplotlib.pyplot as plt
import numpy as np

app = FastAPI()
origins = [
    "http://localhost:3000",
    "https://atencion-al-usuario.uzu.digital",
    "https://atencion-al-usuario.uzu.digital/",
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
    formatFile: str

@app.post("/api/create-chart")
def read_root(req: ChartRequest):
    xAxis = [i.name for i in req.data]
    yAxis = [i.n_reports for i in req.data]
    ticks = [i for i in range(len(req.data))]
    fig, ax = plt.subplots()
    barContainer = ax.bar(xAxis, yAxis, label=xAxis, color=["#00c0ff"])
    ax.bar_label(barContainer, fmt='{:,.0f}')
    ax.set_ylabel("Reportes")
    ax.set_title(req.title)
    if(len(req.data) > 3):
        font2 = {'color':'black','size':8}
        ax.set_xticklabels(xAxis, rotation=45, ha="right", fontdict=font2)
        plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format=req.formatFile)
    buf.seek(0)
    plt.close(fig)
    if req.formatFile == "png":
        return StreamingResponse(buf, media_type="image/png")
    elif req.formatFile == "pdf":
        return StreamingResponse(buf, media_type="application/pdf")
    elif req.formatFile == "svg":
        return StreamingResponse(buf, media_type="image/svg+xml")
    else:
        return StreamingResponse(buf, media_type="image/jpeg")
