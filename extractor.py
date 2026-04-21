import pdfplumber
import re
import pandas as pd

TURNOS = ["MATUTINO", "VESPERTINO", "NOCTURNO", "DOBLE HORARIO", "SIN TURNO"]

def extraer_datos_pdf(file):
    datos = []

    with pdfplumber.open(file) as pdf:
        texto = "\n".join([p.extract_text() or "" for p in pdf.pages])

    lineas = texto.split("\n")

    departamento = None
    area_codigo = None
    area_nombre = None
    buffer = []

    for linea in lineas:
        linea = linea.strip()

        match_dep = re.match(r"\d+\s+([A-ZÁÉÍÓÚÑ\s]+)$", linea)
        if match_dep and "Área" not in linea:
            departamento = match_dep.group(1).strip()

        match_area = re.match(r"Área:\s*(\d+)\s*(.*)", linea)
        if match_area:
            area_codigo = int(match_area.group(1))
            area_nombre = match_area.group(2).strip()
            continue

        turno = next((t for t in TURNOS if t in linea), None)

        if re.match(r"^[A-ZÁÉÍÓÚÑ\s\.\-]+$", linea) and len(linea) > 8:
            buffer.append(linea)
            continue

        if turno and buffer:
            asignatura = " ".join(buffer)

            datos.append({
                "Departamento": departamento,
                "Area": area_codigo,
                "Nombre Area": area_nombre,
                "Asignatura": asignatura,
                "Turno": turno
            })

            buffer = []

    df = pd.DataFrame(datos)
    df = df.sort_values(by="Area")

    return df
