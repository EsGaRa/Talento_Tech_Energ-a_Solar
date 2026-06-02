import streamlit as st
import pandas as pd
import os #verifica si los archivos existen en el computador

# ==========================
# MENÚ GENERAL
# ==========================

def generarMenu():

    with st.sidebar:

        st.title("☀️ ENERGÍA SOLAR")

        st.page_link(
            page="app.py",
            label="Inicio",
            icon="➡️"
        )

        st.page_link(
            page="pages/Costos.py",
            label="Tarifas",
            icon="💰"
        )

        st.page_link(
            page="pages/Intensidad solar.py",
            label="Intensidad Solar",
            icon="🌞"
        )

        st.page_link(
            page="pages/Incentivos.py",
            label="Incentivos",
            icon="⚖️"
        )

        st.page_link(
            page="pages/Produccion.py",
            label="Simulador y costos de infraestructura",
            icon="🏗️"
        )


# ==========================
# FUNCIONES PARA COSTOS - DATOS DE TARIFAS
# ==========================

def cargar_tarifas():

    df = pd.read_csv(
        "data/processed/tarifas_consolidadas.csv"
    )

    # Revisar tipos de datos
    print(df.dtypes)

    # Revisar valores vacíos
    print("AÑOS VACÍOS:", df["AÑO"].isna().sum())
    print("PERIODOS VACÍOS:", df["PERIODO"].isna().sum())

    # Eliminar filas con año o periodo vacío
    df = df.dropna(
        subset=["AÑO", "PERIODO"]
    )

    # Crear fecha real para ordenar correctamente
    df["FECHA_ORDEN"] = pd.to_datetime(
        {
            "year": df["AÑO"].astype(int),
            "month": df["PERIODO"].astype(int),
            "day": 1
        }
    )

    return df

def filtrar_tarifas(
    df,
    departamentos,
    estratos
):

    if departamentos:
        df = df[
            df["DEPARTAMENTO"].isin(departamentos)
        ]

    if estratos:
        df = df[
            df["ESTRATO"].isin(estratos)
        ]

    return df


def obtener_kpis(df):

    tarifa_promedio = round(
        df["TARIFA"].mean(),
        2
    )

    tarifa_maxima = round(
        df["TARIFA"].max(),
        2
    )

    tarifa_minima = round(
        df["TARIFA"].min(),
        2
    )

    return (
        tarifa_promedio,
        tarifa_maxima,
        tarifa_minima
    )

# FUNCIONES PARA INTENSIDAD SOLAR

#Rutas de cada archivo, se guardan en una variable
RUTA_IRR     = "data/processed/radiacion_irradiacion.csv"
RUTA_BRI     = "data/processed/radiacion_brillo_solar.csv"
RUTA_SIN     = "data/processed/radiacion_dias_sin_sol.csv"
RUTA_DPTO    = "data/processed/radiacion_resumen_dpto.csv"
RUTA_REGION  = "data/processed/resumen_por_region.csv"
RUTA_TARIFAS = "data/processed/tarifas_creg.csv"

#Declaración de la variable meses para utilizar
MESES = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
         "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]

#Hace el dashboard más rápido. 
@st.cache_data
def cargar_y_estandarizar_datos():
    rutas = {
        "Irradiación":    RUTA_IRR,
        "Brillo Solar":   RUTA_BRI,
        "Días Sin Sol":   RUTA_SIN,
    }
    #Antes de leer los archivos, verifica que existan
    for tipo, ruta in rutas.items():
        if not os.path.exists(ruta):
            st.error(f"No se encontró el archivo de {tipo} en: `{ruta}`")
            st.stop()

    #Lee los tres CSV y los convierte en tablas de datos DATAFRAMES
    df_irr = pd.read_csv(RUTA_IRR)
    df_bri = pd.read_csv(RUTA_BRI)
    df_sin = pd.read_csv(RUTA_SIN)

    #Recorre los tres DataFrames y elimina espacios invisibles en los nombres de columnas.
    for df in [df_irr, df_bri, df_sin]:
        df.columns = df.columns.str.strip() 
        #estandariza los nombres de las columnas, busca la calve y los reemplaza
        renombres = {}
        for col in df.columns:
            c = col.lower()
            if "estaci"    in c: renombres[col] = "Estacion"
            elif "municip" in c: renombres[col] = "Municipio"
            elif "departam" in c: renombres[col] = "Departamento"
            elif "lat"     in c: renombres[col] = "Latitud"
            elif "lon"     in c: renombres[col] = "Longitud"
            elif "elevaci" in c: renombres[col] = "Elevacion_msnm"
            elif "promedio" in c and "anual" in c: renombres[col] = "Promedio_Anual"
        df.rename(columns=renombres, inplace=True)

    #Devuelve los tres DataFrames ya limpios para que cualquier página pueda usarlos.
    return df_irr, df_bri, df_sin


@st.cache_data
def cargar_datos_complementarios():
    
    rutas = {
        "Resumen Departamental": RUTA_DPTO,
        "Resumen Regional":      RUTA_REGION,
        "Tarifas CREG":          RUTA_TARIFAS,
    }
    for tipo, ruta in rutas.items():
        if not os.path.exists(ruta):
            st.error(f"No se encontró el archivo de {tipo} en: `{ruta}`")
            st.stop()

    df_dpto    = pd.read_csv(RUTA_DPTO)
    df_region  = pd.read_csv(RUTA_REGION)
    df_tarifas = pd.read_csv(RUTA_TARIFAS)

    return df_dpto, df_region, df_tarifas


#Filtra los tres DataFrames para quedarse solo con las filas de los departamentos seleccionados
#Si la lista está vacía, devuelve los datos completos.
#.copy() evita que los cambios posteriores afecten el DataFrame original.
def filtrar_por_departamento(df_irr, df_bri, df_sin, departamentos):
    
    if not departamentos:
        return df_irr.copy(), df_bri.copy(), df_sin.copy()

    irr_f = df_irr[df_irr["Departamento"].isin(departamentos)].copy()
    bri_f = df_bri[df_bri["Departamento"].isin(departamentos)].copy()
    sin_f = df_sin[df_sin["Departamento"].isin(departamentos)].copy()

    return irr_f, bri_f, sin_f