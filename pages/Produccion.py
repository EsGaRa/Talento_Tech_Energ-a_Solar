import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import utils as ut

# =====================================================================
# CONFIGURACIÓN DE LA PÁGINA (ESTILO INSTITUCIONAL)
# =====================================================================
st.set_page_config(
    page_title="Simulador e infraestructura",
    page_icon="🏗️",
    layout="wide"
)

ut.generarMenu()

# =====================================================================
# PORTADA Y DATOS DEL PROYECTO ACADÉMICO
# =====================================================================
st.title("🏗️  Simulador y costos de infraestructura")

# =====================================================================
# CREACIÓN DE LAS PESTAÑAS (TABS)
# =====================================================================
tab1, tab2 = st.tabs(["📉 Análisis de Consumo y Ahorro", "🏗️ Costos de Infraestructura y Equipos"])

# =====================================================================
# PESTAÑA 1: CALCULADORA DE CONSUMO Y GRÁFICA COMPARATIVA
# =====================================================================
with tab1:
    st.header("⚡ Simulador Financiero de Consumo Energético")
    st.write(
        "Modifica los valores en los campos de abajo para calcular cuánto pagas actualmente "
        "con la red eléctrica tradicional en comparación con un sistema de energía solar fotovoltaica."
    )

    col_inputs = st.columns(3)

    with col_inputs[0]:
        tarifa_electrica = st.number_input(
            "Tarifa kW Energía Eléctrica ($ COP)", 
            min_value=0.0, 
            value=850.0,  
            step=50.0,
            key="tarifa_elec"
        )

    with col_inputs[1]:
        tarifa_solar = st.number_input(
            "Tarifa kW Energía Solar ($ COP)", 
            min_value=0.0, 
            value=300.0,  
            step=50.0,
            key="tarifa_sol"
        )

    with col_inputs[2]:
        consumo_mensual = st.number_input(
            "Consumo Mensual Total (kWh)", 
            min_value=0.0, 
            value=180.0,  
            step=10.0,
            key="consumo_mes"
        )

    # Operaciones Matemáticas de Consumo
    pago_total_electrica = consumo_mensual * tarifa_electrica
    pago_total_solar = consumo_mensual * tarifa_solar
    diferencia_ahorro = pago_total_electrica - pago_total_solar

    st.subheader("📋 Resumen de Pago Mensual")
    col_resultados = st.columns(2)

    with col_resultados[0]:
        st.metric(
            label="Pago con Energía Eléctrica", 
            value=f"${pago_total_electrica:,.2f} COP"
        )

    with col_resultados[1]:
        st.metric(
            label="Pago con Energía Solar", 
            value=f"${pago_total_solar:,.2f} COP",
            delta=f"-${diferencia_ahorro:,.2f} COP" if diferencia_ahorro > 0 else f"${abs(diferencia_ahorro):,.2f} COP",
            delta_color="inverse"
        )

    st.subheader("📊 Comparación Visual de Costos ($ COP)")
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 3.5))

    categorias = ['Energía Eléctrica\nTradicional', 'Energía Solar\nFotovoltaica']
    valores = [pago_total_electrica, pago_total_solar]
    colores = ['#E63946', '#2A9D8F']  

    barras = ax.bar(categorias, valores, color=colores, width=0.4, edgecolor='black', linewidth=0.7)
    ax.set_ylabel('Total a Pagar ($ COP)', fontsize=10, fontweight='bold')
    ax.set_title('Proyección del Gasto Mensual según Fuente de Energía', fontsize=12, fontweight='bold', pad=15)

    for barra in barras:
        altura = barra.get_height()
        ax.annotate(f'${altura:,.2f} COP',
                    xy=(barra.get_x() + barra.get_width() / 2, altura),
                    xytext=(0, 5),  
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_ylim(0, max(valores) * 1.25 if max(valores) > 0 else 100)
    sns.despine(left=True, bottom=True)
    st.pyplot(fig)

    st.markdown("---")
    if diferencia_ahorro > 0:
        porcentaje_ahorro = (diferencia_ahorro / pago_total_electrica) * 100
        st.success(
            f"💡 *Análisis Técnico-Económico:* Migrar a un modelo solar fotovoltaico representa una "
            f"reducción del *{porcentaje_ahorro:.1f}%* en el costo de la energía mensual. "
            f"El proyecto genera un ahorro neto directo de *${diferencia_ahorro:,.2f} COP* al mes, "
            f"lo que equivale a un beneficio de *${diferencia_ahorro * 12:,.2f} COP al año*."
        )
    elif diferencia_ahorro < 0:
        st.warning("⚠️ El modelo solar es más costoso bajo la configuración de tarifas actual.")
    else:
        st.info("El costo por kW es idéntico en ambas tecnologías.")

# =====================================================================
# PESTAÑA 2: COSTOS DE INFRAESTRUCTURA Y EQUIPOS
# =====================================================================
with tab2:
    st.header("🏗️ Presupuesto de Infraestructura y Equipos Fotovoltaicos")
    st.write(
        "Ajusta las cantidades y precios unitarios para estimar la inversión "
        "inicial requerida para el montaje físico del sistema solar."
    )

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.subheader("🔧 Componentes Principales")
        cant_paneles = st.number_input("Cantidad de Paneles Solares", min_value=0, value=4, step=1)
        precio_panel = st.number_input("Precio Unitario Panel Solar ($ COP)", min_value=0.0, value=650000.0, step=50000.0)
        
        st.markdown("---")
        cant_baterias = st.number_input("Cantidad de Baterías de Litio/Gel", min_value=0, value=2, step=1)
        precio_bateria = st.number_input("Precio Unitario Batería ($ COP)", min_value=0.0, value=1200000.0, step=100000.0)

    with col_c2:
        st.subheader("🔌 Equipos y Soporte")
        precio_inversor = st.number_input("Precio Inversor Solar Central ($ COP)", min_value=0.0, value=2500000.0, step=100000.0)
        costo_estructura = st.number_input("Estructura de Anclaje y Cableado ($ COP)", min_value=0.0, value=900000.0, step=50000.0)
        costo_mano_obra = st.number_input("Instalación y Mano de Obra Calificada ($ COP)", min_value=0.0, value=1500000.0, step=100000.0)

    # --- CÁLCULO DE COSTOS SUB-TOTALES ---
    total_paneles = cant_paneles * precio_panel
    total_baterias = cant_baterias * precio_bateria
    total_infraestructura = total_paneles + total_baterias + precio_inversor + costo_estructura + costo_mano_obra

    # --- MOSTRAR DESGLOSE EN TABLA ---
    st.subheader("📝 Desglose General de la Inversión")
    
    datos_presupuesto = {
        "Concepto / Elemento": ["Paneles Solares", "Baterías", "Inversor Solar", "Estructuras y Cableado", "Mano de Obra"],
        "Cantidad": [cant_paneles, cant_baterias, 1, 1, 1],
        "Costo Total ($ COP)": [
            f"${total_paneles:,.2f}", 
            f"${total_baterias:,.2f}", 
            f"${precio_inversor:,.2f}", 
            f"${costo_estructura:,.2f}", 
            f"${costo_mano_obra:,.2f}"
        ]
    }
    df_costos = pd.DataFrame(datos_presupuesto)
    st.table(df_costos) 

    # --- MÉTRICA DE INVERSIÓN TOTAL ---
    st.markdown("---")
    st.metric(
        label="💰 VALOR TOTAL ESTIMADO DE LA INVERSIÓN", 
        value=f"${total_infraestructura:,.2f} COP"
    )

    # --- CRUCE DE DATOS ENTRE PESTAÑAS (ANÁLISIS DE RETORNO - ROI) ---
    if diferencia_ahorro > 0:
        retorno_meses = total_infraestructura / diferencia_ahorro
        st.info(
            f"⏱️ *Retorno de Inversión (ROI) Estimado:* Basado en el ahorro mensual calculado en la pestaña "
            f"anterior (*${diferencia_ahorro:,.2f} COP*), el sistema recuperará su costo de infraestructura "
            f"en aproximadamente *{retorno_meses:.1f} meses* (unos *{retorno_meses/12:.1f} años*)."
        )
    else:
        st.warning("⚠️ No es posible calcular el Retorno de Inversión (ROI) ya que la configuración actual de tarifas no genera un ahorro financiero.")