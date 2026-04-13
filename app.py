import streamlit as st
import pandas as pd
import pdfplumber

st.set_page_config(page_title="Buscador UTU PRO", layout="wide")

st.title("🔎 Buscador de Vacantes UTU")

def extraer_limpio(archivo):
    datos = []
    with pdfplumber.open(archivo) as pdf:
        for pagina in pdf.pages:
            tabla = pagina.extract_table()
            if tabla:
                for fila in tabla:
                    # Limpiar ruidos del PDF
                    celdas = [str(c).replace('\n', ' ').strip() for c in fila if c]
                    if len(celdas) > 2:
                        datos.append(celdas)
    return datos

archivo = st.file_uploader("Subir PDF de Vacantes", type=["pdf", "xlsx"])

if archivo:
    # 1. Procesamiento de datos
    filas = extraer_limpio(archivo)
    if filas:
        df = pd.DataFrame(filas)
        
        # 2. Lógica inteligente para encontrar Depto y Turno
        # Buscamos en todo el texto de la fila para no errar
        texto_completo = df.astype(str).apply(lambda x: ' '.join(x), axis=1)
        
        # Lista de departamentos de Uruguay para filtrar
        deptos_uy = ["MONTEVIDEO", "CANELONES", "SORIANO", "COLONIA", "SAN JOSE", "MALDONADO", 
                     "ROCHA", "RIVERA", "PAYSANDU", "SALTO", "ARTIGAS", "FLORIDA", "DURAZNO"]
        
        # --- FILTROS EN LA BARRA LATERAL ---
        st.sidebar.header("Opciones de búsqueda")
        
        # Filtro de Departamento
        depto_seleccionado = st.sidebar.multiselect(
            "Seleccionar Departamento", 
            options=deptos_uy,
            help="Busca el nombre del departamento en cualquier parte de la fila"
        )
        
        # Filtro de Turno
        turnos_posibles = ["MATUTINO", "VESPERTINO", "NOCTURNO", "DOBLE HORARIO"]
        turno_seleccionado = st.sidebar.multiselect("Seleccionar Turno", options=turnos_posibles)

        # 3. Botón de Acción
        if st.sidebar.button("Filtrar Resultados", use_container_width=True):
            df_final = df.copy()
            
            # Filtrado por texto (muy efectivo para PDFs desordenados)
            if depto_seleccionado:
                # Se queda con las filas que mencionen alguno de los departamentos elegidos
                patron = '|'.join(depto_seleccionado)
                df_final = df_final[texto_completo.str.contains(patron, case=False, na=False)]
            
            if turno_seleccionado:
                patron_turno = '|'.join(turno_seleccionado)
                df_final = df_final[texto_completo.str.contains(patron_turno, case=False, na=False)]

            # 4. Mostrar resultados
            st.success(f"Se encontraron {len(df_final)} filas que coinciden.")
            st.dataframe(df_final, use_container_width=True)
            
            # Botón para descargar
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar esta selección", csv, "vacantes_utu.csv", "text/csv")
    else:
        st.error("No se pudo leer el contenido del PDF. Verifica que sea un documento de texto y no una foto.")
else:
    st.info("👋 Sube el PDF de vacantes para activar los filtros de Departamento y Turno.")
