from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import pandas as pd
from extractor import extraer_datos_pdf
import io
import tempfile

app = FastAPI()

@app.get("/")
def home():
    return {"status": "API vacantes funcionando 🚀"}

@app.post("/procesar")
async def procesar(file: UploadFile = File(...)):
    
    # Guardar temporal
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        contenido = await file.read()
        tmp.write(contenido)
        tmp_path = tmp.name

    # Procesar
    df = extraer_datos_pdf(tmp_path)

    # Crear Excel en memoria
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=vacantes.xlsx"}
    )
