import streamlit as st
import utils as ut
from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px # gráficos rápidos
import plotly.graph_objects as go #gráficos complejos
import sys #manejar rutas del sistema de archivos
import os #manejar rutas del sistema de archivos


# Configuración general
st.set_page_config(
    page_title="Energía Solar",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# MENÚ
ut.generarMenu()

# CONTENIDO PRINCIPAL
st.title("Análisis de energía solar en Colombia")

# Abrir imagen
imagen = Image.open("media/energia1.jpg")

# Mostrar imagen
col1, col2, col3 = st.columns([1,2,1])

with col2:

    st.image(
        imagen,
        width=150
    )
st.markdown("## Proyecto Final Talento Tech - UdeA - 2026")

st.markdown("### Integrantes")

st.markdown("""
- Alejandro Muñoz Palacios
- Luis Alejandro Celis Herrera
- Estefany García Ramírez
- Yuleny Andrea Flórez González
""")
