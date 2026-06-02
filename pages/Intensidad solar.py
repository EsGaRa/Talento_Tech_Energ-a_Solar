import streamlit as st
import plotly.express as px # gráficos rápidos
import plotly.graph_objects as go #gráficos complejos
import pandas as pd
import sys #manejar rutas del sistema de archivos
import os #manejar rutas del sistema de archivos
import utils as ut

# Configuración de la barra
st.set_page_config(
    page_title="Intensidad solar",
    page_icon="🌞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Menú
ut.generarMenu()

#Buscar utils en la carpeta padre e importa las funciones que necesitamos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import cargar_y_estandarizar_datos, filtrar_por_departamento, MESES

st.title("☀️ Intensidad Solar y Potencial Geográfico en Colombia")
st.markdown("Aquí puedes observar donde es más viable invertir en energía solar en Colombia")

#Llama la función de utils.py y recibe los tres DataFrames
df_irr, df_bri, df_sin = cargar_y_estandarizar_datos()

#Agrupa el DataFrame por municipio y departamento, calculando el promedio de latitud, longitud e irradiación
df_ciudad = (
    df_irr.groupby(["Municipio", "Departamento"])
    .agg(
        Latitud=("Latitud", "mean"),
        Longitud=("Longitud", "mean"),
        Promedio_Anual=("Promedio_Anual", "mean"),
    )
    .reset_index() #.reset_index() convierte los grupos en columnas normales.
    .round(4) #.round(4) redondea a 4 decimales.
)

#función que recibe un número y devuelve una etiqueta de potencial
#un recurso de 5.0 kWh/m²/día (o superior) de Irradiación Horizontal Global (GHI) es ampliamente considerado 
#por la Agencia Internacional de las Energías Renovables (IRENA) y la Agencia Internacional de la Energía (IEA)
#indica alto potencial para proyectos fotovoltaicos comerciales y de gran escala     
def clasificar(val):
    if val >= 5.5:   return "🔴 Muy Alto"
    elif val >= 5.0: return "🟠 Alto"
    elif val >= 4.5: return "🟡 Medio"
    else:            return "🟢 Bajo"
#.apply(clasificar) la aplica a cada fila del DataFrame, creando una columna nueva llamada Potencial
df_ciudad["Potencial"] = df_ciudad["Promedio_Anual"].apply(clasificar) 

#Obtiene los departamentos únicos, los ordena alfabéticamente, y muestra un selector múltiple en el menú lateral
#Por defecto todos están seleccionados.
st.sidebar.header("⚙️ Filtros")
lista_dptos = sorted(df_ciudad["Departamento"].unique())
dptos_sel = st.sidebar.multiselect(
    "Departamentos:",
    options=lista_dptos,
    default=lista_dptos
)

#Filtra el DataFrame de ciudades. 
#.isin(dptos_sel) devuelve True solo en las filas cuyo departamento esté en la lista seleccionada
#El if dptos_sel else evita errores si la lista está vacía.
df_f = df_ciudad[df_ciudad["Departamento"].isin(dptos_sel)].copy() if dptos_sel else df_ciudad.copy()
df_irr_f, df_bri_f, df_sin_f = filtrar_por_departamento(df_irr, df_bri, df_sin, dptos_sel)

if df_f.empty:
    st.warning("⚠️ Selecciona al menos un departamento.")
    st.stop()

# SECCIÓN 1 — VISTA GENERAL Y POTENCIAL GEOGRÁFICO
st.markdown("---")
with st.expander("🗺️ Vista General y Potencial Geográfico", expanded=True):

    #KPIs Indicadores clave
    prom_nacional = df_ciudad["Promedio_Anual"].mean()
    prom_filtrado = df_f["Promedio_Anual"].mean() #.mean() es el promedio
    ciudad_max    = df_f.loc[df_f["Promedio_Anual"].idxmax()] #.idxmax() valor más alto
    ciudad_min    = df_f.loc[df_f["Promedio_Anual"].idxmin()] #.idxmin() valor más bajo
    n_alto        = len(df_f[df_f["Promedio_Anual"] >= 5.0]) #len(df_f[condición]) cuenta cuántas filas cumplen la condición.

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(
            "☀️ Irradiación Media — Zona Filtrada",
            f"{prom_filtrado:.2f} kWh/m²/día",
            delta=f"País: {prom_nacional:.2f} kWh/m²/día",
            delta_color="blue",
            help="Promedio de los departamentos seleccionados."
        )
    with k2:
        st.metric(
            "🏆 Ciudad con Más Sol",
            ciudad_max["Municipio"],
            delta=f"{ciudad_max['Promedio_Anual']:.2f} kWh/m²/día · {ciudad_max['Departamento']}",
            delta_color="blue"
        )
    with k3:
        st.metric(
            "📉 Ciudad con Menos Sol",
            ciudad_min["Municipio"],
            delta=f"{ciudad_min['Promedio_Anual']:.2f} kWh/m²/día · {ciudad_min['Departamento']}",
            delta_color="blue"
        )
    with k4:
        st.metric(
            "⚡ Ciudades con Alto Potencial",
            f"{n_alto} de {len(df_f)}",
            delta="≥ 5.0 kWh/m²/día",
            delta_color="blue",
            help="Ciudades con irradiación mayor o igual a 5.0 kWh/m²/día."
        )

    st.markdown(" ")

    #Mapas en pestañas
    #Creamos dos pestañas 
    tab_burbujas, tab_barras = st.tabs([
        "🔵 Mapa de Puntos por Ciudad",
        "📊 Comparativo por Departamento"
    ])

    with tab_burbujas:
        st.markdown(
            "Cada punto es una **ciudad**. "
            "El **tamaño y color** indican su irradiación solar promedio anual."
        )
        #Crea un mapa de puntos usando Plotly Express 
        #lat y lon posicionan cada punto, color y size usan la irradiación para colorear y dimensionar cada burbuja.
        fig_burb = px.scatter_mapbox(
            df_f,
            lat="Latitud",
            lon="Longitud",
            color="Promedio_Anual",
            size="Promedio_Anual",
            color_continuous_scale="YlOrRd",
            size_max=22,
            zoom=4,
            center={"lat": 4.5, "lon": -74.0}, # Centrado en Colombia
            hover_name="Municipio",
            hover_data={
                "Departamento":   True,
                "Potencial":      True,
                "Promedio_Anual": ":.2f",
                "Latitud":        False,
                "Longitud":       False
            },
            mapbox_style="carto-positron", #diseño de mapa de fondo claro, limpio
            labels={"Promedio_Anual": "kWh/m²/día", "Potencial": "Nivel"}
        )
        fig_burb.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0}, # Elimina márgenes blancos externos
            coloraxis_colorbar=dict(title="kWh/m²/día"),
            height=520 #altura del mapa
        )
        #Renderizar en Streamlit adaptándose al ancho de la pantalla
        st.plotly_chart(fig_burb, use_container_width=True)

    with tab_barras:
        st.markdown(
            "Irradiación promedio anual por **departamento**, ordenada de mayor a menor. "
            "La línea roja indica el promedio nacional."
        )
        df_dpto_plot = df_f.sort_values("Promedio_Anual", ascending=True)

        fig_dpto = px.bar(
            df_dpto_plot,
            x="Promedio_Anual",
            y="Departamento",
            orientation="h",
            color="Promedio_Anual",
            color_continuous_scale="YlOrRd",
            text="Promedio_Anual",
            hover_data=["Municipio", "Potencial"],
            labels={
                "Promedio_Anual": "Irradiación (kWh/m²/día)",
                "Departamento":   "Departamento"
            }
        )
        fig_dpto.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside" #El número se escribe a la derecha de la barra
        )
        #Línea de promedio nacional
        #add_vline(x=prom_nacional): Dibuja una línea vertical en el eje X
        fig_dpto.add_vline(
            x=prom_nacional,
            line_dash="dash",
            line_color="black",
            annotation_text=f"Promedio nacional: {prom_nacional:.2f}", #Pone un letrero al lado de la línea para que el usuario
            annotation_position="top right",
            annotation_font_color="white"
        )
        fig_dpto.update_layout(
            coloraxis_showscale=False,
            margin={"t": 20, "b": 10, "r": 120},
            height=max(350, len(df_dpto_plot) * 32) #Multiplica la cantidad de departamentos (len(...)) por 32 píxeles para que las barras nunca se amontonen
        )
        st.plotly_chart(fig_dpto, use_container_width=True)

    st.markdown(" ")

    #Top 10 ciudades y Tabla dinámica
    col_top, col_tabla = st.columns([3, 2]) #primera columna ocupa el 60% del espacio y la segunda el 40%

    with col_top:
        st.subheader("🏆 Top 10 Ciudades con Mayor Irradiación") #Filtra y extrae las 10 filas con los valores más altos en Promedio_Anual
        top10 = df_f.nlargest(10, "Promedio_Anual").copy()
        fig_top = px.bar(
            top10,
            x="Promedio_Anual",
            y="Municipio",
            orientation="h",
            color="Promedio_Anual",
            color_continuous_scale="Oranges",
            text="Promedio_Anual",
            hover_data=["Departamento", "Potencial"],
            labels={
                "Promedio_Anual": "Irradiación (kWh/m²/día)",
                "Municipio":      "Ciudad"
            }
        )
        fig_top.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside"
        )
        fig_top.update_layout(
            yaxis={"categoryorder": "total ascending"}, #Es de Plotly. Le ordena al eje Y que acomode las ciudades de menor a mayor hacia arriba
            coloraxis_showscale=False,
            margin={"t": 10, "b": 10, "r": 80},
            height=max(300, len(top10) * 42) #Ajusta la altura de esta sección multiplicando las 10 filas por 42 píxeles
        )
        st.plotly_chart(fig_top, use_container_width=True)

    with col_tabla:
        st.subheader("📋 Detalle por Departamento")
        tabla = df_f[["Departamento", "Municipio", "Promedio_Anual", "Potencial"]].copy()
        tabla = tabla.sort_values("Promedio_Anual", ascending=False).reset_index(drop=True) #Ordena la tabla de mayor a menor según su irradiación
        tabla.columns = ["Departamento", "Ciudad Capital", "kWh/m²/día", "Potencial"]
        tabla["kWh/m²/día"] = tabla["kWh/m²/día"].round(2)

        #Altura dinámica: Multiplica cada fila por 35 píxeles y le suma 38 píxeles para el encabezado
        #600) asegura que si la tabla es gigantesca, se detenga en un máximo de 600 píxeles de alto y active una barra de desplazamiento (scroll)
        altura = min(35 * len(tabla) + 38, 600)
        st.dataframe(tabla, use_container_width=True, hide_index=True, height=altura)
        st.caption("Fuente: IDEAM — Atlas de Radiación Solar de Colombia, 2017.")

# SECCIÓN 2 — COMPORTAMIENTO TEMPORAL Y CONFIABILIDAD SOLAR

st.markdown("---")
with st.expander("📈 ¿El sol es confiable todo el año?", expanded=False):
    st.markdown(
        "No basta saber dónde hay más sol — hay que saber si ese sol es **constante**. "
    )

    #Preparar datos por ciudad para brillo y días sin sol
    MESES_LIST = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
                "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]

    #Toma el DataFrame de brillo solar ya filtrado (df_bri_f) como los demás, lo agrupa por municipio y calcula el promedio de cada mes.
    #Si un municipio tiene varias estaciones, sus valores mensuales se promedian en una sola fila
    df_bri_ciudad = (
        df_bri_f.groupby("Municipio")[MESES_LIST]
        .mean().reset_index().round(2) #Si un municipio tiene varias estaciones, sus valores mensuales se promedian en una sola fila
    )
    df_sin_ciudad = (
        df_sin_f.groupby("Municipio")[MESES_LIST]
        .mean().reset_index().round(2) #.reset_index() convierte el agrupador en columna normal.
    )
    df_irr_ciudad = (
        df_irr_f.groupby("Municipio")[MESES_LIST]
        .mean().reset_index().round(2)
    )

    ciudades_disponibles = sorted( #sorted() ordena alfabéticamente.
        # set() convierte la columna en un conjunto de valores únicos. 
        # & encuentra solo las ciudades que aparecen en los tres archivos al mismo tiempo.
        set(df_irr_ciudad["Municipio"]) 
        & set(df_bri_ciudad["Municipio"])
        & set(df_sin_ciudad["Municipio"])
    )

    if not ciudades_disponibles:
        st.info("ℹ️ No hay ciudades con datos completos en los departamentos seleccionados.")
        st.stop()

    #Pestañas: una ciudad vs varias ciudades
    tab_una, tab_varias = st.tabs([
        "🏙️ Analizar una ciudad",
        "🆚 Comparar varias ciudades"
    ])

    #PESTAÑA 1: Una ciudad
    with tab_una:
        # menú desplegable con todas las ciudades disponibles
        ciudad_sel = st.selectbox(
            "Selecciona una ciudad para analizar:",
            options=ciudades_disponibles,
            key="ciudad_una" #identificador único
        )

        #Filtra cada DataFrame para quedarse solo con la fila de la ciudad seleccionada
        fila_irr = df_irr_ciudad[df_irr_ciudad["Municipio"] == ciudad_sel]
        fila_bri = df_bri_ciudad[df_bri_ciudad["Municipio"] == ciudad_sel]
        fila_sin = df_sin_ciudad[df_sin_ciudad["Municipio"] == ciudad_sel]

        if not fila_irr.empty and not fila_bri.empty and not fila_sin.empty:
            vals_irr = fila_irr[MESES_LIST].values[0]
            vals_bri = fila_bri[MESES_LIST].values[0]
            vals_sin = fila_sin[MESES_LIST].values[0]

            col_izq, col_der = st.columns(2)

            # Curva de irradiación mensual
            with col_izq:
                st.subheader(f"☀️ Irradiación mensual — {ciudad_sel}")
                df_irr_plot = pd.DataFrame({"Mes": MESES_LIST, "Irradiación": vals_irr}) #DataFrame pequeño con dos columnas: los meses y sus valores de irradiación
                df_irr_plot["Mes"] = pd.Categorical(df_irr_plot["Mes"], categories=MESES_LIST, ordered=True)

                fig_irr = px.area(
                    df_irr_plot,
                    x="Mes", y="Irradiación",
                    labels={"Irradiación": "kWh/m²/día"},
                    color_discrete_sequence=["#F39C12"]
                )
                #Agrega una línea horizontal punteada en el valor promedio anual de irradiación
                fig_irr.add_hline(
                    y=vals_irr.mean(),
                    line_dash="dash", line_color="crimson",
                    annotation_text=f"Promedio: {vals_irr.mean():.2f}",
                    annotation_position="top left",
                    annotation_font_color="crimson"
                )
                fig_irr.update_layout(margin={"t": 20, "b": 10}, height=320)
                st.plotly_chart(fig_irr, use_container_width=True)

            # Cruce brillo vs días sin sol
            with col_der:
                st.subheader(f"⛅ Sol vs. Nubosidad — {ciudad_sel}")
                #Crea un gráfico vacío usando graph_objects
                fig_doble = go.Figure()
                #Agrega las barras amarillas que representan las horas de brillo solar por mes
                fig_doble.add_trace(go.Bar(
                    x=MESES_LIST, y=vals_bri,
                    name="Horas de sol/día",
                    marker_color="#F1C40F",
                    opacity=0.75
                ))
                #Agrega la línea roja de días sin sol. yaxis="y2" la conecta al eje derecho independiente
                fig_doble.add_trace(go.Scatter(
                    x=MESES_LIST, y=vals_sin,
                    name="Días sin sol al mes",
                    yaxis="y2",
                    mode="lines+markers", #muestra la línea y los puntos en cada mes
                    line=dict(color="#E74C3C", width=3),
                    marker=dict(size=7)
                ))
                #Configura el diseño del gráfico
                #eje izquierdo (yaxis) barras
                #eje derecho (yaxis2) la línea roja
                #overlaying="y" superpone sobre el mismo gráfico
                fig_doble.update_layout(
                    xaxis=dict(title="Mes"),
                    yaxis=dict(
                        title=dict(text="Horas de sol/día", font=dict(color="#B7950B")),
                        tickfont=dict(color="#B7950B")
                    ),
                    yaxis2=dict(
                        title=dict(text="Días sin sol al mes", font=dict(color="#E74C3C")),
                        tickfont=dict(color="#E74C3C"),
                        overlaying="y", side="right"
                    ),
                    legend=dict(orientation="h", y=1.12, x=0),
                    margin={"t": 50, "b": 10},
                    height=320
                )
                st.plotly_chart(fig_doble, use_container_width=True)

            #Encuentra automáticamente el mejor mes, el peor mes y el mes más nublado
            mes_mejor  = MESES_LIST[list(vals_irr).index(max(vals_irr))]
            mes_peor   = MESES_LIST[list(vals_irr).index(min(vals_irr))]
            mes_nublado= MESES_LIST[list(vals_sin).index(max(vals_sin))]
            st.info(
                f"💡 **{ciudad_sel}** tiene su mejor mes solar en **{mes_mejor}** "
                f"({max(vals_irr):.2f} kWh/m²/día) y el mes más nublado es **{mes_nublado}** "
                f"({max(vals_sin):.1f} días sin sol). "
                f"El mes de menor irradiación es **{mes_peor}** ({min(vals_irr):.2f} kWh/m²/día)."
            )

    #PESTAÑA 2: Varias ciudades
    with tab_varias:
        #selector múltiple
        ciudades_multi = st.multiselect(
            "Selecciona las ciudades a comparar:",
            options=ciudades_disponibles,
            default=ciudades_disponibles[:4], #pre-selecciona las primeras 4 ciudades
            key="ciudades_multi"
        )

        if not ciudades_multi:
            st.warning("⚠️ Selecciona al menos una ciudad.")
        else:
            tab_irr2, tab_bri2, tab_sin2 = st.tabs([
                "☀️ Irradiación Global",
                "🌤️ Horas de Sol",
                "⛅ Días Sin Sol"
            ])
            #función reutilizable
            def grafico_lineas(df_data, ciudades, col_y, titulo, color_label):
                df_sel = df_data[df_data["Municipio"].isin(ciudades)]
                df_melt = df_sel.melt( #.melt() convierte la tabla de formato ancho a formato largo.
                    id_vars="Municipio",
                    value_vars=MESES_LIST,
                    var_name="Mes",
                    value_name=col_y
                )
                df_melt["Mes"] = pd.Categorical(df_melt["Mes"], categories=MESES_LIST, ordered=True)
                df_melt = df_melt.sort_values("Mes")

                fig = px.line(
                    df_melt,
                    x="Mes", y=col_y,
                    color="Municipio",
                    markers=True,
                    labels={"Municipio": "Ciudad", col_y: color_label}
                )
                fig.update_layout(
                    legend=dict(orientation="h", y=-0.25, x=0),
                    margin={"t": 20, "b": 10},
                    height=400
                )
                return fig

            with tab_irr2:
                st.markdown("Compara cómo varía la **irradiación solar** mes a mes entre ciudades.")
                st.plotly_chart(
                    grafico_lineas(df_irr_ciudad, ciudades_multi, "Irradiación",
                                "Irradiación Global", "kWh/m²/día"),
                    use_container_width=True
                )

            with tab_bri2:
                st.markdown("Compara las **horas de brillo solar** diarias por mes entre ciudades.")
                st.plotly_chart(
                    grafico_lineas(df_bri_ciudad, ciudades_multi, "Brillo Solar",
                                "Brillo Solar", "Horas/día"),
                    use_container_width=True
                )

            with tab_sin2:
                st.markdown("Compara los **días completamente nublados** por mes entre ciudades.")
                st.plotly_chart(
                    grafico_lineas(df_sin_ciudad, ciudades_multi, "Días Sin Sol",
                                "Días Sin Sol", "Días/mes"),
                    use_container_width=True
                )

            # Tabla resumen de confiabilidad
            st.markdown("#### 📋 Resumen de Confiabilidad Solar")
            #Crea una lista vacía y luego recorre cada ciudad seleccionada para construir un resumen
            resumen_conf = []
            for ciudad in ciudades_multi:
                f_irr = df_irr_ciudad[df_irr_ciudad["Municipio"] == ciudad]
                f_sin = df_sin_ciudad[df_sin_ciudad["Municipio"] == ciudad]
                if not f_irr.empty and not f_sin.empty:
                    irr_vals = f_irr[MESES_LIST].values[0]
                    sin_vals = f_sin[MESES_LIST].values[0]
                    resumen_conf.append({
                        "Ciudad":             ciudad,
                        "Irrad. Media":       round(irr_vals.mean(), 2),
                        "Mejor Mes":          MESES_LIST[list(irr_vals).index(max(irr_vals))],
                        "Peor Mes":           MESES_LIST[list(irr_vals).index(min(irr_vals))],
                        "Días Nublados/Mes":  round(sin_vals.mean(), 1),
                        "Confiabilidad":      "🟢 Alta" if sin_vals.mean() < 2 else ("🟡 Media" if sin_vals.mean() < 4 else "🔴 Baja")
                    })

            if resumen_conf:
                df_conf = pd.DataFrame(resumen_conf)
                altura_conf = min(35 * len(df_conf) + 38, 400)
                st.dataframe(df_conf, use_container_width=True, hide_index=True, height=altura_conf)
                st.caption("Confiabilidad: 🟢 Alta < 2 días nublados/mes · 🟡 Media 2-4 · 🔴 Baja > 4")

# SECCIÓN 3 — ¿VALE LA PENA ECONÓMICAMENTE?

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import cargar_datos_complementarios

st.markdown("---")
with st.expander("💰 ¿Vale la pena económicamente?", expanded=False):
    st.markdown(
        "Cruzamos el **recurso solar disponible** con las **tarifas eléctricas** "
        "para identificar dónde instalar paneles solares tiene el mayor retorno. "
        "A más sol y más cara la tarifa → mayor ahorro potencial."
    )

    #Cargar y cruzar datos
    _, _, df_tarifas = cargar_datos_complementarios()

    df_irr_dpto = (
        df_irr.groupby("Departamento")
        .agg(Irradiacion=("Promedio_Anual", "mean"), Municipio=("Municipio", "first"))
        .reset_index().round(2)
    )
    # Limpia los nombres de departamento en tarifas para que coincidan con los del Atlas
    # Elimina el texto entre paréntesis y la barra diagonal con espacios
    df_tarifas["Departamento_Clean"] = (
        df_tarifas["Departamento"]
        .str.replace(r"\s*\(.*?\)", "", regex=True)  # quita "(Cali)", "(Popayán)", etc.
        .str.replace(r"\s*/.*", "", regex=True)       # quita "/ Bogotá", "/ Magdalena", etc.
        .str.strip()
    )
    df_tar_dpto = (
        df_tarifas.groupby("Departamento_Clean")
        .agg(CU=("CU_Feb2026", "mean"), Region=("Region", "first"), Tendencia=("Tendencia", "first"))
        .reset_index().round(2)
        .rename(columns={"Departamento_Clean": "Departamento"})
    )
    
    df_cruce = pd.merge(df_irr_dpto, df_tar_dpto, on="Departamento", how="inner")

    #Índice de Oportunidad (normalizado 0–100)
    irr_min, irr_max = df_cruce["Irradiacion"].min(), df_cruce["Irradiacion"].max()
    cu_min,  cu_max  = df_cruce["CU"].min(),  df_cruce["CU"].max()

    #El departamento con el valor más bajo obtiene 0, el de valor más alto obtiene 100, y los demás quedan distribuidos proporcionalmente entre esos extremos
    df_cruce["Score_Irr"] = (df_cruce["Irradiacion"] - irr_min) / (irr_max - irr_min) * 100
    df_cruce["Score_CU"]  = (df_cruce["CU"] - cu_min)  / (cu_max  - cu_min)  * 100
    #Combina los dos scores con pesos: el sol tiene un peso de 60% y la tarifa de 40%
    df_cruce["Indice_Oportunidad"] = (df_cruce["Score_Irr"] * 0.6 + df_cruce["Score_CU"] * 0.4).round(1)

    def nivel_oportunidad(score):
        if score >= 70:   return "🔴 Muy Alta"
        elif score >= 50: return "🟠 Alta"
        elif score >= 30: return "🟡 Media"
        else:             return "🟢 Baja"

    df_cruce["Oportunidad"] = df_cruce["Indice_Oportunidad"].apply(nivel_oportunidad)

    #KPIs
    mejor   = df_cruce.loc[df_cruce["Indice_Oportunidad"].idxmax()]
    cu_alto = df_cruce.loc[df_cruce["CU"].idxmax()]
    irr_top = df_cruce.loc[df_cruce["Irradiacion"].idxmax()]
    n_alta  = len(df_cruce[df_cruce["Indice_Oportunidad"] >= 50])

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(
            "🏆 Mayor Oportunidad de Inversión",
            mejor["Departamento"],
            delta=f"Índice: {mejor['Indice_Oportunidad']:.0f}/100",
            delta_color="blue",
            help="Departamento con mejor combinación de sol alto y tarifa eléctrica alta."
        )
    with k2:
        st.metric(
            "⚡ Tarifa más Alta",
            cu_alto["Departamento"],
            delta=f"${cu_alto['CU']:,.0f}/kWh · {cu_alto['Region']}",
            delta_color="blue",
            help="Mayor costo de energía = mayor ahorro potencial con paneles solares."
        )
    with k3:
        st.metric(
            "☀️ Mayor Irradiación",
            irr_top["Departamento"],
            delta=f"{irr_top['Irradiacion']:.2f} kWh/m²/día",
            delta_color="blue"
        )
    with k4:
        st.metric(
            "📊 Dptos. con Alta Oportunidad",
            f"{n_alta} de {len(df_cruce)}",
            delta="Índice ≥ 50/100",
            delta_color="blue"
        )

    st.markdown(" ")

    #Scatter: Irradiación vs Tarifa
    #Crea un gráfico de dispersión donde cada punto es un departamento.
    st.subheader("🔍 Mapa de Oportunidad — Irradiación vs Tarifa Eléctrica")
    st.markdown(
        "El **cuadrante superior derecho** (mucho sol + tarifa alta) representa "
        "la zona de mayor oportunidad. Cada punto es un departamento."
    )

    fig_scatter = px.scatter(
        df_cruce,
        x="Irradiacion",
        y="CU",
        color="Indice_Oportunidad",
        size="Indice_Oportunidad",
        size_max=28,
        color_continuous_scale="RdYlGn",
        hover_name="Departamento",
        hover_data={
            "Municipio":          True,
            "Region":             True,
            "Irradiacion":        ":.2f",
            "CU":                 ":,.0f",
            "Indice_Oportunidad": ":.1f",
            "Oportunidad":        True
        },
        text="Departamento",
        labels={
            "Irradiacion":        "Irradiación Solar (kWh/m²/día)",
            "CU":                 "Tarifa Eléctrica CU ($/kWh)",
            "Indice_Oportunidad": "Índice Oportunidad"
        }
    )
    fig_scatter.update_traces(textposition="top center", textfont=dict(size=11))

    #Agrega una línea vertical en el promedio de irradiación y una horizontal en el promedio de tarifa. 
    #Estas dos líneas dividen el gráfico en 4 cuadrantes
    fig_scatter.add_vline(
        x=df_cruce["Irradiacion"].mean(),
        line_dash="dash", line_color="gray", opacity=0.5,
        annotation_text="Irradiación promedio",
        annotation_position="bottom right",
        annotation_font_color="gray"
    )
    fig_scatter.add_hline(
        y=df_cruce["CU"].mean(),
        line_dash="dash", line_color="gray", opacity=0.5,
        annotation_text="Tarifa promedio",
        annotation_position="top left",
        annotation_font_color="gray"
    )
    fig_scatter.update_layout(
        height=500,
        margin={"t": 30, "b": 20},
        coloraxis_colorbar=dict(title="Índice")
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Leyenda de cuadrantes
    c1, c2, c3, c4 = st.columns(4)
    c1.success("↗️ **Arriba-derecha**\nMucho sol + tarifa alta\n→ **Máxima oportunidad**")
    c2.warning("↖️ **Arriba-izquierda**\nPoco sol + tarifa alta\n→ Tarifa favorece pero falta sol")
    c3.error("↘️ **Abajo-derecha**\nMucho sol + tarifa baja\n→ Sol disponible, menor ahorro")
    c4.info("↙️ **Abajo-izquierda**\nPoco sol + tarifa baja\n→ Menor prioridad")

    st.markdown(" ")

    #Tabla ranking de oportunidad
    st.subheader("📋 Ranking de Oportunidad por Departamento")

    col_tab, col_bar = st.columns([2, 3])

    with col_tab:
        tabla_rank = df_cruce[[
            "Departamento", "Municipio", "Irradiacion", "CU", "Indice_Oportunidad", "Oportunidad"
        ]].sort_values("Indice_Oportunidad", ascending=False).reset_index(drop=True)
        tabla_rank.index += 1
        tabla_rank.columns = ["Departamento", "Ciudad", "Sol (kWh/m²)", "Tarifa ($/kWh)", "Índice", "Nivel"]
        altura_rank = min(35 * len(tabla_rank) + 38, 530)
        st.dataframe(tabla_rank, use_container_width=True, height=altura_rank)
        st.caption("Índice = 60% irradiación + 40% tarifa, escala 0–100.")

    with col_bar:
        fig_rank = px.bar(
            df_cruce.sort_values("Indice_Oportunidad", ascending=True),
            x="Indice_Oportunidad",
            y="Departamento",
            orientation="h",
            color="Indice_Oportunidad",
            color_continuous_scale="RdYlGn",
            text="Indice_Oportunidad",
            hover_data=["Municipio", "Oportunidad"],
            labels={
                "Indice_Oportunidad": "Índice de Oportunidad (0–100)",
                "Departamento":       "Departamento"
            }
        )
        fig_rank.update_traces(texttemplate="%{text:.0f}", textposition="outside")
        fig_rank.add_vline(
            x=50, line_dash="dash", line_color="BLACK",
            annotation_text="Umbral alta oportunidad",
            annotation_font_color="black"
        )
        fig_rank.update_layout(
            coloraxis_showscale=False,
            margin={"t": 10, "b": 10, "r": 60},
            height=530
        )
        st.plotly_chart(fig_rank, use_container_width=True)

    # ─── Insight final para ambos perfiles ────────────────────────────────────────
    st.markdown("---")
    col_inv, col_ciu = st.columns(2)

    top3 = df_cruce.nlargest(3, "Indice_Oportunidad")["Departamento"].tolist()

    with col_inv:
        st.markdown("#### 📈 Para el inversionista")
        st.success(
            f"Los departamentos **{', '.join(top3)}** presentan la mejor combinación "
            f"de recurso solar y costo energético. Un sistema fotovoltaico en estas zonas "
            f"maximiza el retorno por kWh generado frente a la tarifa de red desplazada."
        )

    with col_ciu:
        st.markdown("#### 🏠 Para el ciudadano")
        st.info(
            f"Si vives en **{top3[0]}** o **{top3[1]}**, instalar paneles solares en tu casa "
            f"puede reducir significativamente tu factura eléctrica. "
            f"Entre más alta tu tarifa actual, más rápido recuperas la inversión."
        )

