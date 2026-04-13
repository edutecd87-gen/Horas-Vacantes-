import streamlit as st
import pandas as pd

# Configuración para que se vea bien en móviles
st.set_page_config(page_title="Buscador UTU", layout="centered")

st.title("🔎 Consulta de horas vacantes")

uploaded_file = st.file_uploader("Subir planilla", type=["xlsx", "csv"])

if uploaded_file:
    # Carga de datos
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    
    # En móviles, los filtros expandibles funcionan mejor que la barra lateral
    with st.expander("⚙️ Toca aquí para filtrar"):
        # Usamos multiselect para que sea fácil elegir con el dedo
        depto = st.multiselect("Departamento", options=sorted(df["Departamento"].unique().astype(str)))
        area = st.multiselect("Área", options=sorted(df["Área"].unique().astype(str)))
        turno = st.multiselect("Turno", options=sorted(df["Turno"].unique().astype(str)))
        dias = st.multiselect("Días", options=sorted(df["Día"].unique().astype(str)))
        
        btn_buscar = st.button("Aplicar Filtros", use_container_width=True)

    if btn_buscar:
        # Lógica de filtrado
        mask = pd.Series([True] * len(df))
        if depto: mask &= df["Departamento"].isin(depto)
        if area: mask &= df["Área"].isin(area)
        if turno: mask &= df["Turno"].isin(turno)
        if dias: mask &= df["Día"].isin(dias)
        
        resultados = df[mask]
        
        st.success(f"Encontradas: {len(resultados)} vacantes")
        
        # Formato de tarjetas para celular (en lugar de una tabla ancha)
        for i, row in resultados.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['Área']}**")
                st.caption(f"📍 {row['Centro']} - {row['Turno']}")
                st.write(f"📅 {row['Día']} | 🕒 {row['Hora Inicio']} a {row['Hora Fin']}")
                if 'Texto Original' in df.columns:
                    with st.expander("Ver detalles"):
                        st.write(row['Texto Original'])
