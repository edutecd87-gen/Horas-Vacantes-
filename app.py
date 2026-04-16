import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO

st.set_page_config(page_title="Horas Vacantes UTU", layout="wide")

st.title("📚 Buscador de Horas Vacantes UTU")
st.markdown("Subí el PDF oficial y filtrá por Departamento, Centro y Turno.")

uploaded_file = st.file_uploader("Subir PDF de Horas Vacantes", type="pdf")


# ----------------------------
# FUNCIONES
# ----------------------------

def
