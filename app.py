st.write("Columnas detectadas:")
st.write(df.columns.tolist())
import streamlit as st
import pandas as pd
import unicodedata

st.set_page_config(page_title="Buscador UTU", layout="centered")

st.title("🔎 Consulta de Horas")

def limpiar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().replace("\n", " ")
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto.lower()

def normalizar_columnas(df):
    nuevas = {}
    for col in df.columns:
        nuevas[col] = limpiar_texto(col)
    return nuevas

def buscar_columna(df, palabras_clave):
    columnas_norm = normalizar_columnas(df)
    for original, normalizada in columnas_norm.items():
        for palabra in palabras_clave:
            if palabra in normalizada:
                return original
    return None

uploaded_file = st.file_uploader("Subir planilla", type=["xlsx", "csv"])

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Mostrar columnas reales para diagnóstico
    st.write("Columnas detectadas:", df.columns.tolist())

    col_depto = buscar_columna(df, ["departamento"])
    col_area = buscar_columna(df, ["area"])
    col_turno = buscar_columna(df, ["turno"])
    col_dia = buscar_columna(df, ["dia"])
    col_centro = buscar_columna(df, ["centro"])
    col_inicio = buscar_columna(df, ["inicio"])
    col_fin = buscar_columna(df, ["fin"])

    with st.expander("⚙️ Filtros", expanded=True):

        depto = st.multiselect(
            "Departamento",
            sorted(df[col_depto].dropna().astype(str).unique())
        ) if col_depto else []

        area = st.multiselect(
            "Área",
            sorted(df[col_area].dropna().astype(str).unique())
        ) if col_area else []

        turno = st.multiselect(
            "Turno",
            sorted(df[col_turno].dropna().astype(str).unique())
        ) if col_turno else []

        dias = st.multiselect(
            "Día",
            sorted(df[col_dia].dropna().astype(str).unique())
        ) if col_dia else []

    mask = pd.Series(True, index=df.index)

    if depto and col_depto:
        mask &= df[col_depto].isin(depto)

    if area and col_area:
        mask &= df[col_area].isin(area)

    if turno and col_turno:
        mask &= df[col_turno].isin(turno)

    if dias and col_dia:
        mask &= df[col_dia].isin(dias)

    resultados = df[mask]

    st.success(f"Encontradas: {len(resultados)} vacantes")

    for _, row in resultados.iterrows():
        with st.container(border=True):
            titulo = row[col_area] if col_area else "Vacante"
            st.markdown(f"**{titulo}**")

            centro = row[col_centro] if col_centro else ""
            turno_val = row[col_turno] if col_turno else ""
            dia = row[col_dia] if col_dia else ""
            inicio = row[col_inicio] if col_inicio else ""
            fin = row[col_fin] if col_fin else ""

            st.caption(f"📍 {centro} - {turno_val}")
            st.write(f"📅 {dia} | 🕒 {inicio} a {fin}")
