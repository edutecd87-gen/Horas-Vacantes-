import streamlit as st
import pandas as pd
import pdfplumber
import re

# Configuración de página
st.set_page_config(page_title="Gestor de Vacantes UTU", layout="wide")

st.title("Conversor y Buscador de Vacantes")

def extraer_datos_pdf(archivo_pdf):
    filas_finales = []
    with pdfplumber.open(archivo_pdf) as pdf:
        for pagina in pdf.pages:
            tabla = pagina.extract_table()
            if tabla:
                for fila in tabla:
                    # Limpiamos filas vacías
                    fila_limpia = [celda.replace('\n', ' ') if celda else "" for celda in fila]
                    if any(fila_limpia): 
                        filas_finales.append(fila_limpia)
    
    # Creamos el DataFrame usando la primera fila como encabezado
    if filas_finales:
        df = pd.DataFrame(filas_finales[1:], columns=filas_finales[0])
        return df
    return None

# --- INTERFAZ ---
archivo = st.file_uploader("Sube tu PDF de vacantes o Excel", type=["pdf", "xlsx"])

if archivo:
    if archivo.name.endswith('.pdf'):
        with st.spinner('Procesando PDF de UTU...'):
            df = extraer_datos_pdf(archivo)
            st.success("¡PDF convertido a tabla!")
    else:
        df = pd.read_excel(archivo)

    if df is not None:
        # Mostramos los filtros que pediste
        st.subheader("Filtros de búsqueda")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Adaptamos nombres de columnas según el PDF de UTU
            deptos = st.multiselect("Departamento", options=df.iloc[:, 1].unique()) # Generalmente columna 1
        with col2:
            areas = st.multiselect("Área", options=df.iloc[:, 2].unique())
        with col3:
            turnos = st.multiselect("Turno", options=df.iloc[:, 3].unique())
        
        # Botón de búsqueda
        if st.button("Buscar vacantes"):
            # Aquí aplicamos el filtrado (ejemplo simple)
            resultado = df.copy()
            if deptos:
                resultado = resultado[resultado.iloc[:, 1].isin(deptos)]
            
            st.dataframe(resultado)
            
            # Botón para descargar el Excel ya convertido
            csv = resultado.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar esta lista en Excel/CSV", csv, "vacantes_filtradas.csv", "text/csv")

