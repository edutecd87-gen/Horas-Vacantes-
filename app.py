import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO

st.set_page_config(page_title="Horas Vacantes UTU", layout="wide")

st.title("📚 Buscador PRO de Horas Vacantes UTU")
st.markdown("Versión estructurada por columnas reales del PDF.")

uploaded_file = st.file_uploader("Subir PDF oficial", type="pdf")


# --------------------------------------------------
# FUNCIÓN PRO DE EXTRACCIÓN
# --------------------------------------------------

def extraer_datos(pdf):

    registros = []

    TURNOS_VALIDOS = [
        "MATUTINO",
        "VESPERTINO",
        "NOCTURNO",
        "DOBLE HORARIO",
        "SIN TURNO",
        "VESPERTINO/NOCTURNO"
    ]

    with pdfplumber.open(pdf) as pdf_file:

        for page in pdf_file.pages:

            words = page.extract_words()

            # Agrupar palabras por posición vertical (misma fila)
            filas = {}
            for w in words:
                y = round(w["top"], 1)
                if y not in filas:
                    filas[y] = []
                filas[y].append(w)

            departamento_actual = ""
            centro_actual = ""
            turno_actual = ""

            for y in sorted(filas.keys()):

                fila = filas[y]
                fila = sorted(fila, key=lambda x: x["x0"])
                texto_fila = " ".join([w["text"] for w in fila]).strip()

                # Normalizar cortes raros
                texto_fila = texto_fila.replace("NO CTURNO", "NOCTURNO")
                texto_fila = texto_fila.replace("VESPERTINO/NO CTURNO", "VESPERTINO/NOCTURNO")

                # Detectar Departamento
                if re.match(r"\d+\s+[A-ZÁÉÍÓÚÑ ]+$", texto_fila):
                    departamento_actual = texto_fila
                    continue

                # Detectar Centro
                if any(x in texto_fila for x in ["ESCUELA", "INSTITUTO", "C.E.C.", "C.E.A.", "POLO", "ANEXO"]):
                    centro_actual = texto_fila
                    continue

                # Detectar Turno
                for turno in TURNOS_VALIDOS:
                    if turno in texto_fila:
                        turno_actual = turno

                # Detectar asignatura (patrón típico: número + texto)
                if re.search(r"\d+[A-ZÁÉÍÓÚÑ]", texto_fila):

                    registros.append({
                        "Departamento": departamento_actual,
                        "Centro": centro_actual,
                        "Asignatura": texto_fila,
                        "Turno": turno_actual
                    })

    df = pd.DataFrame(registros)

    # Limpieza final
    df = df[df["Asignatura"].str.len() > 5]

    return df


# --------------------------------------------------
# APP
# --------------------------------------------------

if uploaded_file:

    with st.spinner("Reconstruyendo estructura del PDF..."):
        df = extraer_datos(uploaded_file)

    if df.empty:
        st.error("No se detectaron registros. Revisar PDF.")
    else:
        st.success("PDF procesado correctamente.")

        col1, col2, col3 = st.columns(3)

        # Departamento
        with col1:
            deptos = sorted(df["Departamento"].dropna().unique())
            depto_sel = st.selectbox("Departamento", ["Todos"] + deptos)

        if depto_sel != "Todos":
            df_filtrado = df[df["Departamento"] == depto_sel]
        else:
            df_filtrado = df.copy()

        # Centro
        with col2:
            centros = sorted(df_filtrado["Centro"].dropna().unique())
            centro_sel = st.selectbox("Centro", ["Todos"] + centros)

        if centro_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Centro"] == centro_sel]

        # Turno
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
