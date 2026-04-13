import streamlit as st
import pandas as pd
import pdfplumber

st.set_page_config(page_title="Buscador UTU", layout="wide")

st.title("🔎 Consulta de Vacantes")

def procesar_archivo(file):
    if file.name.endswith('.pdf'):
        datos = []
        with pdfplumber.open(file) as pdf:
            for pagina in pdf.pages:
                tabla = pagina.extract_table()
                if tabla:
                    datos.extend(tabla)
        if not datos: return None
        # En los PDF de UTU, el Depto suele estar en la fila que dice "10 MONTEVIDEO", etc.
        # Creamos un DataFrame base
        df = pd.DataFrame(datos)
        # Limpieza básica: quitar saltos de línea
        df = df.map(lambda x: str(x).replace('\n', ' ') if x else "")
        
        # Intentamos asignar nombres de columnas estándar para que aparezcan los filtros
        # Basado en tu PDF: Col 1 es Depto, Col 2 es Centro/Área
        columnas_finales = ["ID", "Departamento", "Centro_Area", "Turno_Detalle", "Horario", "Llamado"]
        df.columns = columnas_finales[:len(df.columns)]
        return df
    else:
        return pd.read_excel(file)

archivo = st.file_uploader("Sube tu PDF o Excel aquí", type=["pdf", "xlsx"])

if archivo:
    df = procesar_archivo(archivo)
    
    if df is not None:
        # --- ESTA PARTE GENERA LOS FILTROS QUE NO TE APARECÍAN ---
        st.sidebar.header("Filtros de Búsqueda")
        
        # Filtro 1: Departamento
        lista_deptos = sorted([x for x in df["Departamento"].unique() if x.strip()])
        depto_sel = st.sidebar.multiselect("Seleccionar Departamento", options=lista_deptos)
        
        # Filtro 2: Turno (intentamos extraerlo de la columna correspondiente)
        col_turno = "Turno_Detalle" if "Turno_Detalle" in df.columns else df.columns[3]
        lista_turnos = sorted([x for x in df[col_turno].unique() if x.strip()])
        turno_sel = st.sidebar.multiselect("Seleccionar Turno", options=lista_turnos)

        # Botón de búsqueda
        if st.sidebar.button("Realizar Búsqueda", use_container_width=True):
            resultado = df.copy()
            if depto_sel:
                resultado = resultado[resultado["Departamento"].isin(depto_sel)]
            if turno_sel:
                resultado = resultado[resultado[col_turno].isin(turno_sel)]
            
            st.success(f"Resultados encontrados: {len(resultado)}")
            st.dataframe(resultado, use_container_width=True)
            
            # Opción para descargar lo filtrado
            csv = resultado.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar esta lista", csv, "busqueda.csv", "text/csv")
    else:
        st.warning("No se detectaron tablas en el archivo. Asegúrate de que no sea una foto.")

else:
    st.info("💡 Consejo: Al subir el PDF, la web extraerá automáticamente los Departamentos y Turnos para que los elijas.")
