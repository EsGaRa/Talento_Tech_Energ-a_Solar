import streamlit as st
import pandas as pd
import plotly.express as px # Función para crear gráficos interactivos
import utils as ut

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

st.set_page_config(
    page_title="Tarifas",
    page_icon="💰",
    layout="wide"
)

ut.generarMenu()

# --------------------------------------------------
# CARGA DATOS
# --------------------------------------------------

df = ut.cargar_tarifas() # Cargar archivo de tarifas dede utils

# --------------------------------------------------
# TÍTULO
# --------------------------------------------------

st.title("💰 Análisis de tarifas de Energía")

st.write("""
Análisis de la evolución de las tarifas de energía
en Colombia por departamento, empresa y estrato.
""")

# --------------------------------------------------

# FILTROS
# --------------------------------------------------

st.subheader("Filtros")

col1, col2, col3 = st.columns(3) #Dividir la página en tres columnas - departamento, estrtato y año

with col1: # Obtener todos los departamentos del archivo cargar tarifas de ut

            departamentos = st.multiselect( #el multiselect es para crear el filtro que permita seleccionar varios departamentos
                "Departamento",
                sorted(df["DEPARTAMENTO"].unique()) # Ordena alfabeticamente los departamentos
            )

with col2:

            estratos = st.multiselect(
                "Estrato",
                sorted(df["ESTRATO"].unique())
            )

with col3:

            anios = st.multiselect(
                "Año",
                sorted(df["AÑO"].dropna().astype(int).unique())
            )

        # Aplicar filtros

df_filtrado = df.copy() # Crear copia del dataframe original

        # Si se selecciona un departamento, solo conservar las filas de esos departamentos, tanto para año y estrato

if departamentos:
            df_filtrado = df_filtrado[
                df_filtrado["DEPARTAMENTO"].isin(departamentos)
            ]

if estratos:
            df_filtrado = df_filtrado[
                df_filtrado["ESTRATO"].isin(estratos)
            ]

if anios:
            df_filtrado = df_filtrado[
                df_filtrado["AÑO"].isin(anios)
            ]
            
# Crear dos pestañas para la información, una por empresa y otra por estratos y departamentos.
tab1, tab2 = st.tabs(
    [
        "🏢 Análisis por empresas",
        "🏠 Análisis por estratos y departamentos"
    ]
)
with tab1:

    # --------------------------------------------------
    # KPIs
    # Llama la función de utils y calcula esas variables según los datos filtrados, st metric muestra las tarjetas
    # --------------------------------------------------

    st.subheader("📊 Indicadores Principales")

    promedio, maxima, minima = ut.obtener_kpis(
        df_filtrado
    )

    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:

        st.metric(
            "Tarifa Promedio",
            f"${promedio:,.2f}"
        )

    with kpi2:

        st.metric(
            "Tarifa Máxima",
            f"${maxima:,.2f}"
        )

    with kpi3:

        st.metric(
            "Tarifa Mínima",
            f"${minima:,.2f}"
        )

    # --------------------------------------------------
    # EMPRESAS MÁS COSTOSAS
    # --------------------------------------------------

    st.subheader(
        "🏆 Empresas con Tarifas Más Altas"
    )

    ranking = (
        df_filtrado
        .groupby("EMPRESA")["TARIFA"]
        .mean()
        .sort_values(
            ascending=False # Ordenar de mayor a menor, por tarifa.
        )
        .head(10) # Conserva las 10 empresas mas caras
        .reset_index()
    )

    fig2 = px.bar(
        ranking,
        x="EMPRESA",
        y="TARIFA",
        text_auto=".2f"
    )

    fig2.update_layout(
        xaxis_title="Empresa",
        yaxis_title="Tarifa Promedio"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
        key="empresas_caras"
    )

    # --------------------------------------------------
    # EMPRESAS MÁS ECONÓMICAS
    # --------------------------------------------------

    st.subheader(
        "💡 Empresas con Tarifas Más Bajas"
    )

    economicas = (
        df_filtrado
        .groupby("EMPRESA")["TARIFA"]
        .mean()
        .sort_values(
            ascending=True
        )
        .head(10)
        .reset_index()
    )

    fig3 = px.bar(
        economicas,
        x="EMPRESA",
        y="TARIFA",
        text_auto=".2f"
    )

    fig3.update_layout(
        xaxis_title="Empresa",
        yaxis_title="Tarifa Promedio"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True,
        key="empresas_baratas"
    )

    # --------------------------------------------------
    # TABLA RESUMEN
    # --------------------------------------------------

    st.subheader(
        "📋 Resumen de Tarifas por Empresa"
    )
    # Analizar cada empresa por separado, y para cada una calcula promedio, máximo, mínimo. 
    tabla = (
        df_filtrado
        .groupby("EMPRESA")
        .agg(
            Tarifa_Promedio=("TARIFA", "mean"),
            Tarifa_Maxima=("TARIFA", "max"),
            Tarifa_Minima=("TARIFA", "min")
        )
        .round(2) # 2 Decimales
        .sort_values( # Muestra primero las empresas mas costosas
            by="Tarifa_Promedio",
            ascending=False
        )
    )

    st.dataframe(
        tabla,
        use_container_width=True
    )

        # --------------------------------------------------
    # VARIACIÓN HISTÓRICA POR EMPRESA
    # --------------------------------------------------

    st.subheader(
        "📈 Variación Histórica de Tarifas por Empresa"
    )

    # Tarifa promedio por empresa y año

    tabla_empresas = (
        df_filtrado
        .groupby(
            ["EMPRESA", "AÑO"]
        )["TARIFA"]
        .mean()
        .reset_index()
        .pivot(
            index="EMPRESA",
            columns="AÑO",
            values="TARIFA"
        )
    )

    # Años disponibles

    anios_empresas = sorted(
        tabla_empresas.columns
    )

    # Variación acumulada histórica

    tabla_empresas[
        "Variación Total (%)"
    ] = (
        (
            tabla_empresas[
                anios_empresas[-1]
            ]
            -
            tabla_empresas[
                anios_empresas[0]
            ]
        )
        /
        tabla_empresas[
            anios_empresas[0]
        ]
    ) * 100

    # Eliminar empresas sin datos suficientes

    tabla_empresas = tabla_empresas.dropna(
        subset=["Variación Total (%)"]
    )

    # Top 10 empresas con mayor incremento

    top_incremento = (
        tabla_empresas[
            ["Variación Total (%)"]
        ]
        .sort_values(
            by="Variación Total (%)",
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    empresa_mayor_incremento = (
        top_incremento.iloc[0]["EMPRESA"]
    )

    incremento = (
        top_incremento.iloc[0]["Variación Total (%)"]
    )

    st.success(
        f"📈 La empresa con mayor incremento histórico fue {empresa_mayor_incremento}, con un aumento acumulado de {incremento:.2f}%."
    )

    fig_incremento = px.bar(
    top_incremento,
    x="EMPRESA",
    y="Variación Total (%)",
    text_auto=".2f"
    )

    fig_incremento.update_layout(
        xaxis_title="Empresa",
        yaxis_title="Variación Acumulada (%)"
    )

    st.plotly_chart(
        fig_incremento,
        use_container_width=True,
        key="variacion_empresas"
    )

    st.subheader(
        "📋 Variación Acumulada por Empresa"
    )

    st.dataframe(
        tabla_empresas.sort_values(
            by="Variación Total (%)",
            ascending=False
        ).round(2),
        use_container_width=True
    )

with tab2:
    
    # EVOLUCIÓN TARIFAS
    # --------------------------------------------------

    st.subheader(
        "📈 Evolución de Tarifas por Departamento"
    )

    #Agrupar por fecha y departamento para calcular tarifa promedio para cada combinación
    df_linea = (
        df_filtrado
        .groupby(
            ["FECHA_ORDEN", "DEPARTAMENTO"]
        )["TARIFA"]
        .mean()
        .reset_index()
    )
    # Crear gráfico, X - Fecha, Y - Tarifa, cada departamento aparece con un color distintivo
    fig = px.line(
        df_linea,
        x="FECHA_ORDEN",
        y="TARIFA",
        color="DEPARTAMENTO",
        markers=True
    )
    # Personalizar gráfico
    fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Tarifa",
        legend_title="Departamento"
    )
    # Insertar gráfico en la página, calcula tarifa promedio de cada empresa
    st.plotly_chart(
        fig,
        use_container_width=True,
        key="evolucion_tarifas"
    )

    # Vamos a validar la variación de cobros por estrato

    # --------------------------------------------------
    # EVOLUCIÓN POR ESTRATO
    # --------------------------------------------------

    st.subheader(
        "📈 Evolución de Tarifas por Estrato"
    )

    df_estratos = (
        df_filtrado
        .groupby(
            ["AÑO", "ESTRATO"]
        )["TARIFA"]
        .mean()
        .reset_index()
    )

    fig_estratos = px.line(
        df_estratos,
        x="AÑO",
        y="TARIFA",
        color="ESTRATO",
        markers=True
    )

    fig_estratos.update_layout(
        xaxis_title="Año",
        yaxis_title="Tarifa Promedio",
        legend_title="Estrato"
    )

    st.plotly_chart(
        fig_estratos,
        use_container_width=True,
        key="variacion_estratos"
    )

    # --------------------------------------------------
    # TABLA DE VARIACIONES POR ESTRATO
    # --------------------------------------------------

    st.subheader(
        "📋 Variación Histórica por Estrato"
    )

    tabla_estratos = (
        df_filtrado
        .groupby(
            ["ESTRATO", "AÑO"]
        )["TARIFA"]
        .mean()
        .reset_index()
        .pivot(
            index="ESTRATO",
            columns="AÑO",
            values="TARIFA"
        )
    )

    # Obtener años disponibles

    anios_disponibles = sorted(
        tabla_estratos.columns
    )

    # Crear columnas de variación entre años consecutivos

    for i in range(
        len(anios_disponibles) - 1
    ):

        anio_actual = anios_disponibles[i]
        anio_siguiente = anios_disponibles[i + 1]

        tabla_estratos[
            f"Var {int(anio_actual)}-{int(anio_siguiente)} (%)"
        ] = (
            (
                tabla_estratos[anio_siguiente]
                -
                tabla_estratos[anio_actual]
            )
            /
            tabla_estratos[anio_actual]
        ) * 100

    # Variación acumulada histórica

    tabla_estratos[
        "Variación Total (%)"
    ] = (
        (
            tabla_estratos[
                anios_disponibles[-1]
            ]
            -
            tabla_estratos[
                anios_disponibles[0]
            ]
        )
        /
        tabla_estratos[
            anios_disponibles[0]
        ]
    ) * 100

    tabla_estratos = tabla_estratos.round(2)

    st.dataframe(
        tabla_estratos,
        use_container_width=True
    )

    # --------------------------------------------------
    # KPI ESTRATO CON MAYOR AUMENTO
    # --------------------------------------------------

    estrato_mayor_aumento = (
        tabla_estratos[
            "Variación Total (%)"
        ].idxmax()
    )

    valor_aumento = (
        tabla_estratos[
            "Variación Total (%)"
        ].max()
    )

    st.success(
        f"📊 El estrato con mayor incremento histórico fue el Estrato {estrato_mayor_aumento}, con un aumento acumulado de {valor_aumento:.2f}%."
    )

    # --------------------------------------------------
    # --------------------------------------------------
# GRÁFICO DE VARIACIÓN TOTAL
# --------------------------------------------------

    st.subheader(
        "📊 Comparación de Variación Histórica por Estrato"
    )

    variacion_total = (
        tabla_estratos[
            ["Variación Total (%)"]
        ]
        .reset_index()
    )

    # Convertir a texto para que Plotly lo trate como categoría
    variacion_total["ESTRATO"] = (
        variacion_total["ESTRATO"]
        .astype(str)
    )

    fig_variacion = px.bar(
        variacion_total,
        x="ESTRATO",
        y="Variación Total (%)",
        text_auto=".2f"
    )

    fig_variacion.update_layout(
        xaxis_title="Estrato",
        yaxis_title="Variación Acumulada (%)"
    )

    # Evitar valores intermedios como 0.5, 1.5, 2.5...
    fig_variacion.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=[
            "1",
            "2",
            "3",
            "4",
            "5 y 6, Ind y Com"
        ]
    )

    st.plotly_chart(
        fig_variacion,
        use_container_width=True,
        key="variacion_total_estratos"
    )