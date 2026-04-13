import streamlit as st
import pandas as pd
import unicodedata

st.set_page_config(page_title="Buscador UTU", layout="centered")

st.title("🔎 Consulta de Horas")

# --- Función para normalizar texto ---
def normalizar(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto)
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto.lower().strip()

# --- Buscar columna flexible ---
def encontrar_columna(df, posibles_nombres):
    for col in df.columns:
        col_norm = normalizar(col)
        for nombre in posibles_nombres:
            if normalizar(nombre) in col_norm:
                return col
    return None

uploaded_file = st.file_uploader("Subir planilla", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("Archivo cargado correctamente")

    # Detectar columnas automáticamente
    col_depto = encontrar_columna(df, ["departamento"])
    col_area = encontrar_columna(df, ["area"])
    col_turno = encontrar_columna(df, ["turno"])
    col_dia = encontrar_columna(df, ["dia"])
    col_centro = encontrar_columna(df, ["centro"])
    col_inicio = encontrar_columna(df, ["hora inicio", "inicio"])
    col_fin = encontrar_columna(df, ["hora fin", "fin"])
    col_texto = encontrar_columna(df, ["texto original", "detalle"])

    with st.expander("⚙️ Toca aquí para filtrar", expanded=True):

        depto = st.multiselect(
            "Departamento",
            options=sorted(df[col_depto].dropna().astype(str).unique())
        ) if col_depto else []

        area = st.multiselect(
            "Área",
            options=sorted(df[col_area].dropna().astype(str).unique())
        ) if col_area else []

        turno = st.multiselect(
            "Turno",
            options=sorted(df[col_turno].dropna().astype(str).unique())
        ) if col_turno else []

        dias = st.multiselect(
            "Día",
            options=sorted(df[col_dia].dropna().astype(str).unique())
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

            if col_area:
                st.markdown(f"**{row[col_area]}**")

            centro = row[col_centro] if col_centro else ""
            turno_val = row[col_turno] if col_turno else ""
            dia = row[col_dia] if col_dia else ""
            inicio = row[col_inicio] if col_inicio else ""
            fin = row[col_fin] if col_fin else ""

            st.caption(f"📍 {centro} - {turno_val}")
            st.write(f"📅 {dia} | 🕒 {inicio} a {fin}")

            if col_texto:
                with st.expander("Ver detalles"):
                    st.write(row[col_texto])
