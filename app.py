import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO

st.set_page_config(page_title="Vacantes UTU", layout="wide")

st.title("📚 Buscador de Horas Vacantes")
st.markdown("Subí el PDF oficial y filtrá por Departamento, Localidad y Turno.")

uploaded_file = st.file_uploader("Subir PDF de Horas Vacantes", type="pdf")

def limpiar_texto(texto):
    texto = texto.replace("\n", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()

def extraer_datos(pdf):
    registros = []

    with pdfplumber.open(pdf) as pdf_file:
        texto_completo = ""
        for pagina in pdf_file.pages:
            texto_completo += pagina.extract_text() + "\n"

    lineas = texto_completo.split("\n")

    departamento_actual = ""
    localidad = ""
    turno = ""

    for linea in lineas:
        linea = limpiar_texto(linea)

        # Detectar departamento
        if re.match(r"\d+\s+[A-ZÁÉÍÓÚÑ ]+", linea):
            departamento_actual = linea

        # Detectar centros educativos
        if "ESCUELA" in linea or "INSTITUTO" in linea or "C.E.A." in linea:
            localidad = linea

        # Detectar turno
        if "MATUTINO" in linea:
            turno = "MATUTINO"
        elif "VESPERTINO" in linea:
            turno = "VESPERTINO"
        elif "NOCTURNO" in linea:
            turno = "NOCTURNO"
        elif "DOBLE HORARIO" in linea:
            turno = "DOBLE HORARIO"

        # Detectar asignaturas (simplificado)
        if any(palabra in linea for palabra in ["BIOLOGIA", "QUIMICA", "GASTRONOMIA", "ADMINISTRACION", "DIBUJO"]):
            registros.append({
                "Departamento": departamento_actual,
                "Localidad": localidad,
                "Asignatura": linea,
                "Turno": turno
            })

    df = pd.DataFrame(registros)
    return df

if uploaded_file:

    with st.spinner("Procesando PDF..."):
        df = extraer_datos(uploaded_file)

    if df.empty:
        st.error("No se pudieron extraer datos. Verificá el formato del PDF.")
    else:
        st.success("PDF procesado correctamente.")

        col1, col2, col3 = st.columns(3)

        with col1:
            deptos = sorted(df["Departamento"].dropna().unique())
            depto_sel = st.selectbox("Departamento", ["Todos"] + deptos)

        if depto_sel != "Todos":
            df_filtrado = df[df["Departamento"] == depto_sel]
        else:
            df_filtrado = df.copy()

        with col2:
            localidades = sorted(df_filtrado["Localidad"].dropna().unique())
            localidad_sel = st.selectbox("Localidad", ["Todas"] + localidades)

        if localidad_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado["Localidad"] == localidad_sel]

        with col3:
            turnos = sorted(df_filtrado["Turno"].dropna().unique())
            turno_sel = st.selectbox("Turno", ["Todos"] + turnos)

        if turno_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Turno"] == turno_sel]

        st.markdown("### 📊 Resultados")
        st.dataframe(df_filtrado, use_container_width=True)

        # Descargar Excel
        output = BytesIO()
        df_filtrado.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        st.download_button(
            label="📥 Descargar Excel",
            data=output,
            file_name="vacantes_filtradas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
