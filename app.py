import streamlit as st
import pandas as pd

st.set_page_config(page_title="Buscador UTU", layout="centered")

st.title("🔎 Consulta de Horas Vacantes")

uploaded_file = st.file_uploader("Subir planilla", type=["xlsx", "csv"])

if uploaded_file:

    # Leer archivo
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Limpiar espacios invisibles en TODAS las columnas
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()

    st.success("Archivo cargado correctamente")

    # ========================
    # FILTROS
    # ========================
    with st.expander("⚙️ Toca aquí para filtrar", expanded=True):

        depto = st.multiselect(
            "Departamento",
            options=sorted(df
