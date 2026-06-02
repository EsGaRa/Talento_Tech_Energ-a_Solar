import streamlit as st
import sys
import os
import utils as ut
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(
    page_title="Incentivos Tributarios",
    page_icon="⚖️",
    layout="wide"
)

ut.generarMenu()

st.title("⚖️ Marco Legal e Incentivos Tributarios")
st.markdown(
    "Incentivos tributarios para proyectos de energía con Fuentes No Convencionales de "
    "Energía Renovable (FNCER) en Colombia, establecidos por la **Ley 1715 de 2014**, "
    "modificada por la **Ley 2099 de 2021** y la **Ley 2294 de 2023**."
)
st.caption(
    "Fuentes oficiales: "
    "[Ley 1715 de 2014 — Gestor Normativo Función Pública](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=57353) · "
    "[Ley 2099 de 2021 — Gestor Normativo Función Pública](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=166326) · "
    "[Minisitio UPME — Incentivos Tributarios FNCE](https://www.upme.gov.co/ventanilla-unica-de-tramites-y-servicios/incentivos-tributarios/)"
)

st.markdown("---")

# KPIs
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric(
        "📋 Incentivos disponibles", "4",
        delta="Ley 1715 / Ley 2099 / Ley 2294",
        delta_color="blue"
    )
with k2:
    st.metric(
        "💰 Deducción en renta", "50%",
        delta="Hasta 15 años — Art. 11 Ley 1715",
        delta_color="blue"
    )
with k3:
    st.metric(
        "🏷️ IVA en equipos y servicios", "0%",
        delta="Exclusión total — Art. 12 Ley 1715",
        delta_color="blue"
    )
with k4:
    st.metric(
        "📉 Depreciación máxima", "33.33% / año",
        delta="Acelerada — Art. 14 Ley 1715",
        delta_color="blue"
    )

st.markdown("---")

# QUIÉNES PUEDEN ACCEDER
with st.expander("👥 ¿Quién puede acceder a estos incentivos?", expanded=True):
    st.markdown(
        "Según los artículos 11, 12, 13 y 14 de la **Ley 1715 de 2014** "
        "(Gestor Normativo — Función Pública), pueden acceder a estos incentivos las "
        "**personas naturales o jurídicas** que realicen inversiones directas en:"
    )
    col1, col2 = st.columns(2)
    with col1:
        st.success("✅ Investigación y desarrollo tecnológico en FNCE")
        st.success("✅ Estudios técnicos, financieros, jurídicos, económicos y ambientales definitivos")
        st.success("✅ Adquisición de equipos, elementos y maquinaria para proyectos FNCE")
    with col2:
        st.success("✅ Montaje y puesta en operación de proyectos FNCE")
        st.success("✅ Proyectos de generación y autogeneración con energía solar, eólica, geotérmica, biomasa, mares, hidrógeno verde, azul y blanco")
        st.success("✅ Acciones de gestión eficiente de la energía (GEE)")
    st.info(
        "ℹ️ Para acceder a cualquiera de estos incentivos, la inversión debe ser "
        "**evaluada y certificada por la UPME** (Unidad de Planeación Minero Energética), "
        "según lo establece el artículo 43 de la Ley 2099 de 2021."
    )

st.markdown("---")
st.subheader("📌 Los 4 Incentivos Tributarios")

# INCENTIVO 1 — DEDUCCIÓN EN RENTA
# Fuente: Artículo 11, Ley 1715 de 2014, modificado por Ley 2099 de 2021
# https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=57353
col1, col2 = st.columns(2)

with col1:
    with st.expander("💰 Deducción Especial en el Impuesto de Renta (50%)", expanded=True):
        st.caption("📜 Artículo 11, Ley 1715 de 2014 — modificado por Ley 2099 de 2021")
        st.markdown(
            "Los obligados a declarar renta que realicen directamente inversiones en "
            "producción de energía con FNCE y gestión eficiente de la energía, "
            "**podrán deducir de su renta el 50% del total de la inversión realizada**, "
            "en un período no mayor de 15 años contados a partir del año gravable siguiente "
            "al que haya entrado en operación la inversión."
        )
        st.warning(
            "⚠️ El valor a deducir no puede ser superior al 50% de la renta líquida "
            "del contribuyente, determinada antes de restar el valor de la inversión."
        )
        st.markdown("**Aplica a:** Personas Naturales o Jurídicas obligadas a declarar renta.")
        st.markdown("**Certificación requerida:** UPME debe certificar el proyecto como FNCE o GEE.")
        st.markdown("**Vigencia:** `Ley 1715 de 2014, Art. 11 — modificado por Ley 2099 de 2021`")

# INCENTIVO 2 — EXCLUSIÓN DE IVA
# Fuente: Artículo 12, Ley 1715 de 2014, modificado por Ley 2099 de 2021
# https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=57353
with col2:
    with st.expander("🏷️ Exclusión del IVA en Equipos y Servicios (0%)", expanded=True):
        st.caption("📜 Artículo 12, Ley 1715 de 2014 — modificado por Ley 2099 de 2021")
        st.markdown(
            "Los equipos, elementos, maquinaria y **servicios nacionales o importados** "
            "destinados a la preinversión e inversión para la producción y utilización de "
            "energía con FNCE, así como para la medición y evaluación de potenciales recursos "
            "y para medidas de gestión eficiente de energía, **están excluidos del IVA**. "
            "Este beneficio aplica también a servicios prestados en el exterior con la misma destinación."
        )
        st.warning(
            "⚠️ Los bienes deben estar incluidos en el Programa de Uso Racional y Eficiente "
            "de Energía y Fuentes No Convencionales — PROURE. El Decreto 829 de 2020 permite "
            "solicitar ante la DIAN la devolución del IVA pagado si se obtiene la certificación UPME."
        )
        st.markdown("**Aplica a:** Personas Naturales o Jurídicas que realicen inversiones en proyectos FNCE.")
        st.markdown("**Certificación requerida:** UPME debe certificar el proyecto como FNCE o GEE.")
        st.markdown("**Vigencia:** `Ley 1715 de 2014, Art. 12 — modificado por Ley 2099 de 2021`")

col3, col4 = st.columns(2)

# INCENTIVO 3 — EXENCIÓN ARANCELARIA
# Fuente: Artículo 13, Ley 1715 de 2014, modificado por Ley 2099 de 2021
# https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=57353
with col3:
    with st.expander("🚢 Exención de Gravámenes Arancelarios (0%)", expanded=True):
        st.caption("📜 Artículo 13, Ley 1715 de 2014 — modificado por Ley 2099 de 2021")
        st.markdown(
            "Los titulares de nuevas inversiones en proyectos FNCE están **exentos del pago "
            "de derechos arancelarios** en la importación de maquinaria, equipos, materiales "
            "e insumos destinados exclusivamente a las etapas de preinversión e inversión del proyecto."
        )
        st.warning(
            "⚠️ Este beneficio aplica exclusivamente sobre equipos **importados que no sean "
            "producidos por la industria nacional**. La solicitud debe realizarse ante la DIAN "
            "mínimo **15 días hábiles antes de la importación**, anexando la certificación UPME "
            "remitida a la Ventanilla Única de Comercio Exterior — VUCE."
        )
        st.markdown("**Aplica a:** Personas Naturales o Jurídicas titulares de nuevas inversiones en proyectos FNCE.")
        st.markdown("**Certificación requerida:** UPME debe certificar previamente el proyecto.")
        st.markdown("**Vigencia:** `Ley 1715 de 2014, Art. 13 — modificado por Ley 2099 de 2021`")

# INCENTIVO 4 — DEPRECIACIÓN ACELERADA
# Fuente: Artículo 14, Ley 1715 de 2014
# https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=57353
with col4:
    with st.expander("📉 Depreciación Acelerada de Activos (hasta 33.33%/año)", expanded=True):
        st.caption("📜 Artículo 14, Ley 1715 de 2014")
        st.markdown(
            "Las actividades de generación con FNCE y de gestión eficiente de energía gozan "
            "del **régimen de depreciación acelerada** sobre maquinarias, equipos y obras civiles "
            "necesarias para la preinversión, inversión y operación del proyecto, con una "
            "**tasa anual global máxima del 33.33%**. La tasa puede variar anualmente "
            "comunicándolo a la DIAN sin superar ese límite."
        )
        st.warning(
            "⚠️ Si los activos son vendidos antes de finalizar su período de depreciación, "
            "se deben restituir las sumas aplicadas como renta líquida por recuperación de "
            "deducciones (Art. 195 y 196 del Estatuto Tributario). "
            "Este incentivo puede combinarse con la deducción en renta del Art. 11."
        )
        st.markdown("**Aplica a:** Empresas / Personas Jurídicas con proyectos de generación FNCE o GEE.")
        st.markdown("**Certificación requerida:** UPME debe certificar el proyecto como FNCE o GEE.")
        st.markdown("**Vigencia:** `Ley 1715 de 2014, Art. 14`")

st.markdown("---")

# QUIÉN CERTIFICA
# Fuente: Artículo 43, Ley 2099 de 2021
# https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=166326
with st.expander("🏛️ ¿Quién certifica estos incentivos? — UPME", expanded=False):
    st.caption(
        "📜 Artículo 43, Ley 2099 de 2021 — "
        "[Gestor Normativo Función Pública](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=166326)"
    )
    col1, col2 = st.columns(2)
    with col1:
        st.info(
            "**La UPME es la entidad competente para:**\n\n"
            "- Evaluar y certificar inversiones en generación y utilización de energía con FNCE\n"
            "- Certificar proyectos de gestión eficiente de la energía (GEE)\n"
            "- Certificar proyectos de movilidad eléctrica\n"
            "- Certificar proyectos de hidrógeno verde, azul y blanco"
        )
    with col2:
        st.success(
            "**Novedad Ley 2099 de 2021:**\n\n"
            "El certificado de la UPME es suficiente para acceder a todos los beneficios. "
            "Ya **no se requiere el aval de la ANLA** (Autoridad Nacional de Licencias Ambientales) "
            "para proyectos de gestión eficiente de la energía.\n\n"
            "Desde el 1 de febrero de 2025, las solicitudes se tramitan a través del "
            "**Sistema Único de Usuarios (SUU)** de la UPME."
        )
    st.markdown(
        "🔗 **Minisitio oficial UPME — Incentivos Tributarios FNCE:** "
        "https://www.upme.gov.co/ventanilla-unica-de-tramites-y-servicios/incentivos-tributarios/"
    )

# MARCO NORMATIVO
with st.expander("📚 Marco Normativo Completo", expanded=False):
    st.markdown("Normas vigentes que regulan estos incentivos, según el Gestor Normativo de Función Pública:")
    normas = [
        ("Ley 1715 de 2014",        "13 mayo 2014",     "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=57353",   "Regula la integración de las energías renovables no convencionales al Sistema Energético Nacional. Define los 4 incentivos tributarios."),
        ("Ley 1955 de 2019",        "25 mayo 2019",     "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=93970",    "Plan Nacional de Desarrollo 2018-2022. Modifica el artículo 11 de la Ley 1715 de 2014 sobre incentivos a la generación FNCE."),
        ("Decreto 829 de 2020",     "10 junio 2020",    "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=127884",   "Reglamenta los artículos 11, 12, 13 y 14 de la Ley 1715 de 2014. Modifica el Decreto 1625 de 2016 en materia tributaria."),
        ("Ley 2099 de 2021",        "julio 2021",       "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=166326",   "Ley de Transición Energética. Extiende y amplía los incentivos. Asigna a la UPME como entidad certificadora única. Incluye hidrógeno verde y azul como FNCE."),
        ("Ley 2294 de 2023",        "2023",             "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=209510",   "Plan Nacional de Desarrollo 2022-2026 'Colombia Potencia de la Vida'. Modifica y adiciona artículos de la Ley 1715 de 2014."),
        ("Resolución UPME 135/2025","2025",             "https://gestornormativo.creg.gov.co/gestor/entorno/docs/resolucion_upme_0135_2025.htm", "Establece los requisitos, procedimiento y tarifas vigentes para solicitar certificados de incentivos tributarios ante la UPME."),
    ]
    for norma, fecha, url, descripcion in normas:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"**[{norma}]({url})**\n\n`{fecha}`")
        with col2:
            st.markdown(descripcion)
        st.markdown("---")
