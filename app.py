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
            options=sorted(df["Departamento"].dropna().unique())
        )

        area = st.multiselect(
            "Área",
            options=sorted(df["Área"].dropna().unique())
        )

        turno = st.multiselect(
            "Turno",
            options=sorted(df["Turno"].dropna().unique())
        )

        dias = st.multiselect(
            "Día",
            options=sorted(df["Día"].dropna().unique())
        )

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

        # ========================
        # MOSTRAR RESULTADOS
        # ========================
        for _, row in resultados.iterrows():
            with st.container(border=True):

                st.markdown(f"### {row['Área']}")
                st.caption(f"📍 {row['Centro']} - {row['Turno']}")
                st.write(f"📅 {row['Día']} | 🕒 {row['Hora Inicio']} a {row['Hora Fin']}")

                if "Texto Original" in df.columns:
                    with st.expander("Ver detalles"):
                        st.write(row["Texto Original"])

        # ========================
        # DESCARGAR RESULTADOS
        # ========================
        if len(resultados) > 0:
            st.download_button(
                label="📥 Descargar resultados en Excel",
                data=resultados.to_excel(index=False, engine="openpyxl"),
                file_name="resultados_filtrados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
