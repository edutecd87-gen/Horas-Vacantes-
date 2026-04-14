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

    # Eliminar filas completamente vacías
    df = df.dropna(how="all")

    # Convertir todo a texto y limpiar espacios
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    st.success("Archivo cargado correctamente")

    # 🔎 Mostrar columnas para verificar
    # st.write(df.head())

    # ========================
    # FILTROS
    # ========================
    with st.expander("⚙️ Toca aquí para filtrar", expanded=True):

        depto_opts = sorted([x for x in df["Departamento"].unique() if x != "nan"])
        area_opts = sorted([x for x in df["Área"].unique() if x != "nan"])
        turno_opts = sorted([x for x in df["Turno"].unique() if x != "nan"])
        dia_opts = sorted([x for x in df["Día"].unique() if x != "nan"])

        depto = st.multiselect("Departamento", depto_opts)
        area = st.multiselect("Área", area_opts)
        turno = st.multiselect("Turno", turno_opts)
        dias = st.multiselect("Día", dia_opts)

        btn_buscar = st.button("Aplicar Filtros", use_container_width=True)

    # ========================
    # FILTRADO
    # ========================
    if btn_buscar:

        mask = pd.Series(True, index=df.index)

        if depto:
            mask &= df["Departamento"].isin(depto)

        if area:
            mask &= df["Área"].isin(area)

        if turno:
            mask &= df["Turno"].isin(turno)

        if dias:
            mask &= df["Día"].isin(dias)

        resultados = df[mask]

        st.success(f"Encontradas: {len(resultados)} vacantes")

        for _, row in resultados.iterrows():
            with st.container(border=True):

                titulo = row["Área"] if row["Área"] != "nan" else "Sin Área"

                st.markdown(f"### {titulo}")
                st.caption(f"📍 {row['Centro']} - {row['Turno']}")
                st.write(f"📅 {row['Día']} | 🕒 {row['Hora Inicio']} a {row['Hora Fin']}")

                if "Texto Original" in df.columns and row["Texto Original"] != "nan":
                    with st.expander("Ver detalles"):
                        st.write(row["Texto Original"])
