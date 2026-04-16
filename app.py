import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO

st.set_page_config(page_title="Horas Vacantes UTU", layout="wide")

st.title("📚 Buscador de Horas Vacantes UTU")
st.markdown("Subí el PDF oficial y filtrá por Departamento, Centro y Turno.")

uploaded_file = st.file_uploader("Subir PDF de Horas Vacantes", type="pdf")


# ----------------------------
# FUNCIONES
# ----------------------------

def limpiar_texto(texto):
    texto = texto.replace("\n", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def extraer_datos(pdf):
    registros = []

    with pdfplumber.open(pdf) as pdf_file:
        texto = ""
        for pagina in pdf_file.pages:
            contenido = pagina.extract_text()
            if contenido:
                texto += contenido + "\n"

    # Normalizar cortes raros del PDF
    texto = texto.replace("NO\nCTURNO", "NOCTURNO")
    texto = texto.replace("VESPERTINO/NO\nCTURNO", "VESPERTINO/NOCTURNO")

    lineas = texto.split("\n")

    departamento_actual = ""
    centro_actual = ""
    turno_actual = ""

    TURNOS_VALIDOS = [
        "MATUTINO",
        "VESPERTINO",
        "NOCTURNO",
        "DOBLE HORARIO",
        "SIN TURNO",
        "VESPERTINO/NOCTURNO"
    ]

    for i, linea in enumerate(lineas):
        linea = limpiar_texto(linea)

        if not linea:
            continue

        # Detectar Departamento (ej: 10 MONTEVIDEO)
        if re.match(r"\d+\s+[A-ZÁÉÍÓÚÑ ]+$", linea):
            departamento_actual = linea

        # Detectar Centro Educativo
        if (
            "ESCUELA" in linea
            or "INSTITUTO" in linea
            or "C.E.C." in linea
            or "C.E.A." in linea
            or "POLO EDUCATIVO" in linea
            or "ANEXO" in linea
        ):
            centro_actual = linea

        # Detectar Turno
        for turno in TURNOS_VALIDOS:
            if turno in linea:
                turno_actual = turno

        # Detectar asignatura (líneas que contienen código tipo 1MATEMATICA, 1INGLES, etc.)
        if re.search(r"\d[A-ZÁÉÍÓÚÑ]", linea):
            registros.append({
                "Departamento": departamento_actual,
                "Centro": centro_actual,
                "Asignatura": linea,
                "Turno": turno_actual
            })

    df = pd.DataFrame(registros)

    return df


# ----------------------------
# APP
# ----------------------------

if uploaded_file:

    with st.spinner("Procesando PDF..."):
        df = extraer_datos(uploaded_file)

    if df.empty:
        st.error("No se pudieron extraer datos. Verificá el formato del PDF.")
    else:
        st.success("PDF procesado correctamente.")

        col1, col2, col3 = st.columns(3)

        # Filtro Departamento
        with col1:
            deptos = sorted(df["Departamento"].dropna().unique())
            depto_sel = st.selectbox("Departamento", ["Todos"] + deptos)

        if depto_sel != "Todos":
            df_filtrado = df[df["Departamento"] == depto_sel]
        else:
            df_filtrado = df.copy()

        # Filtro Centro
        with col2:
            centros = sorted(df_filtrado["Centro"].dropna().unique())
            centro_sel = st.selectbox("Centro", ["Todos"] + centros)

        if centro_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Centro"] == centro_sel]

        # Filtro Turno
        with col3:
            turnos = sorted(df_filtrado["Turno"].dropna().unique())
            turno_sel = st.selectbox("Turno", ["Todos"] + turnos)

        if turno_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Turno"] == turno_sel]

        st.markdown("### 📊 Resultados")
        st.dataframe(df_filtrado, use_container_width=True)

        # Descargar Excel
        output = BytesIO()
        df_filtrado.to_excel(output, index=False, engine="openpyxl")
        output.seek(0)

        st.download_button(
            label="📥 Descargar Excel",
            data=output,
            file_name="horas_vacantes_filtradas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
