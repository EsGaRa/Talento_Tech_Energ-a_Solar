import pandas as pd
import os
import requests
 
BASE = "C:/Users/User1/Documents/TALENTO_TECH"
SALIDA_TARIFAS = f"{BASE}/data/processed/tarifas_creg.csv"
SALIDA_REGION  = f"{BASE}/data/processed/resumen_por_region.csv"
 
URL_DIC = "https://www.superservicios.gov.co/sites/default/files/inline-files/Informacion-tarifaria-de-energia-comercializadores-operador-de-red-diciembre-2025.xlsx"
URL_FEB = "https://www.superservicios.gov.co/sites/default/files/inline-files/Informacion-tarifaria-de-energia-comercializadores-operador-de-red-Febrero-2026.xlsx"
 
HEADERS = {
    #User-Agent firma del navegador
    #Accept le dice al servidor qué tipo de archivo esperamos
    #Referer le dice al servidor desde qué página está descargando
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*",
    "Referer": "https://www.superservicios.gov.co/Empresas-vigiladas/Energia-y-gas-combustible/Energia/Tarifas",
}
 
os.makedirs(f"{BASE}/data/raw", exist_ok=True)
os.makedirs(f"{BASE}/data/processed", exist_ok=True)
 
ARCHIVO_DIC = f"{BASE}/data/raw/temp_dic2025.xlsx"
ARCHIVO_FEB = f"{BASE}/data/raw/temp_feb2026.xlsx"

#La URL del archivo que queremos
#Los headers simulan ser un navegador
#timeout=30 significa que si el servidor no responde en 30 segundos, abandona y da error en lugar de esperar indefinidamente
respuesta_dic = requests.get(URL_DIC, headers=HEADERS, timeout=30)
respuesta_feb = requests.get(URL_FEB, headers=HEADERS, timeout=30)
 
if respuesta_dic.status_code != 200 or len(respuesta_dic.content) < 10000:
    raise ConnectionError(
        f"No se pudo descargar el archivo de diciembre. Codigo: {respuesta_dic.status_code}"
    )
if respuesta_feb.status_code != 200 or len(respuesta_feb.content) < 10000:
    raise ConnectionError(
        f"No se pudo descargar el archivo de febrero. Codigo: {respuesta_feb.status_code}"
    )
 
with open(ARCHIVO_DIC, "wb") as f:
    f.write(respuesta_dic.content) #escribe el contenido descargado en ese archivo.
with open(ARCHIVO_FEB, "wb") as f:
    f.write(respuesta_feb.content)

# MAPEO en el Excel → (operador, departamento, región, ciudad)
# La llave es el nombre exacto de la pestaña en el Excel, el valor es una tupla con cuatro datos
HOJAS_INFO = {
    "1. CEDENAR":               ("CEDENAR",        "Nariño",                   "Pacífico",   "Pasto"),
    "2. CELSIA COLOMBIA Valle": ("CELSIA",          "Valle del Cauca",          "Pacífico",   "Cali"),
    "3. CELSIA COLOMBIA Tolima":("CELSIA",          "Tolima",                   "Andina",     "Ibagué"),
    "4. CENS":                  ("CENS",            "Norte de Santander",       "Andina",     "Cúcuta"),
    "5. CEO":                   ("CEO",             "Cauca",                    "Pacífico",   "Popayán"),
    "6. CETSA":                 ("CETSA",           "Valle del Cauca",          "Pacífico",   "Tuluá"),
    "7. CHEC":                  ("CHEC",            "Caldas",                   "Andina",     "Manizales"),
    "8. ENEL COLOMBIA":         ("ENEL",            "Cundinamarca / Bogotá",    "Andina",     "Bogotá"),
    "9. DISPAC":                ("DISPAC",          "Chocó",                    "Pacífico",   "Quibdó"),
    "10. EBSA":                 ("EBSA",            "Boyacá",                   "Andina",     "Tunja"),
    "11. EDEQ":                 ("EDEQ",            "Quindío",                  "Andina",     "Armenia"),
    "12. EE Putumayo":          ("EE Putumayo",     "Putumayo",                 "Amazonia",   "Mocoa"),
    "13. EEBP":                 ("EEBP",            "Bajo Putumayo",            "Amazonia",   "Puerto Asís"),
    "14. EEP PEREIRA":          ("EEP Pereira",     "Risaralda",                "Andina",     "Pereira"),
    "15. EEP CARTAGO":          ("EEP Cartago",     "Valle del Cauca (Norte)",  "Andina",     "Cartago"),
    "16. AIR-E":                ("AIR-E",           "Atlántico / Magdalena",    "Caribe",     "Barranquilla"),
    "17. AFINIA":               ("AFINIA",          "Córdoba / Sucre / Bolívar","Caribe",     "Montería"),
    "18. ELECTROCAQUETÁ":       ("Electrocaquetá",  "Caquetá",                  "Amazonia",   "Florencia"),
    "19. ELECTROHUILA":         ("Electrohuila",    "Huila",                    "Andina",     "Neiva"),
    "20. EMCALI":               ("EMCALI",          "Valle del Cauca (Cali)",   "Pacífico",   "Cali"),
    "21. EMEESA":               ("EMEESA",          "Cauca (Popayán)",          "Pacífico",   "Popayán"),
    "22. EMEVASI":              ("EMEVASI",         "Putumayo (Sibundoy)",      "Amazonia",   "Sibundoy"),
    "23. EMSA":                 ("EMSA",            "Meta",                     "Orinoquía",  "Villavicencio"),
    "24. ENELAR":               ("ENELAR",          "Arauca",                   "Orinoquía",  "Arauca"),
    "25.ENERCA":                ("ENERCA",          "Casanare",                 "Orinoquía",  "Yopal"),
    "26.ENERGUAVIARE":          ("ENERGUAVIARE",    "Guaviare",                 "Amazonia",   "San José del Guaviare"),
    "27.EPM":                   ("EPM",             "Antioquia",                "Andina",     "Medellín"),
    "28.ESSA":                  ("ESSA",            "Santander",                "Andina",     "Bucaramanga"),
    "29.RUITOQUE":              ("RUITOQUE",        "Santander (Ruitoque)",     "Andina",     "Floridablanca"),
}

# FUNCIÓN leer CUV_119 (Costo Unitario oficial)
# función reutilizable, dónde está el archivo, qué pestaña leer, qué año y qué mes buscar
def extraer_cuv119(ruta, hoja, anio, periodo):
    #Abre el Excel y lee la pestaña indicada, header=None indica que no lea encabezado ya que es irregular
    try:
        df = pd.read_excel(ruta, sheet_name=hoja, header=None)
        #Recorre las filas desde la 6 hasta la 21, df.iloc[i] trae la fila número i integer location (ubicación por número entero).
        for i in range(6, min(22, len(df))):
            fila = df.iloc[i]
            try:
                #Lee el año y el periodo/mes
                a = int(fila.iloc[1]) if pd.notna(fila.iloc[1]) else None #pd.notna() verifica que la celda no esté vacía
                p = int(fila.iloc[2]) if pd.notna(fila.iloc[2]) else None
            except (ValueError, TypeError):
                continue
            if a != anio or p != periodo: #!= significa "diferente de"
                continue
            try: #Lee el CUV_119, el costo unitario oficial, si el valor existe y es mayor que cero lo devuelve redondeado a 2 decimales. Si no, devuelve None
                v = float(fila.iloc[9]) if pd.notna(fila.iloc[9]) else None
            except:
                v = None
            return round(v, 2) if v and v > 0 else None
        return None
    except:
        return None

# PROCESAR LOS 29 OPERADORES, BUCLE PRINCIPAL
#Crea una lista vacía y recorre las 29 entradas del diccionario
registros = []

for hoja, (operador, departamento, region, ciudad) in HOJAS_INFO.items():
    #Llama la función dos veces: una para diciembre 2025 y otra para febrero 2026
    cu25 = extraer_cuv119(ARCHIVO_DIC, hoja, 2025, 12)
    cu26 = extraer_cuv119(ARCHIVO_FEB, hoja, 2026,  2)

    if cu25 and cu26 and cu25 > 0:
        var   = round((cu26 - cu25) / cu25 * 100, 2)
        tend  = "Subió" if var > 0.1 else ("Bajó" if var < -0.1 else "Estable")
    else:
        var, tend = None, "Sin datos"

    #diccionario con todos los datos de ese operador, con los registros se tiene 29 diccionarios
    registros.append({
        "Operador_Red":   operador,
        "Departamento":   departamento,
        "Region":         region,
        "Ciudad_Capital": ciudad,
        "CU_Dic2025":     cu25,
        "CU_Feb2026":     cu26,
        "Variacion_Pct":  var,
        "Tendencia":      tend,
        "Fuente":         "CREG — Información tarifaria Dic-2025 y Feb-2026, columna CUV_119",
    })

#Convierte la lista de 29 diccionarios en una tabla organizada
#La ordena de mayor a menor por CU_Feb2026. na_position="last" pone los vacíos al final.
df = pd.DataFrame(registros).sort_values(
    "CU_Feb2026", ascending=False, na_position="last"
).reset_index(drop=True)

# Resumen por región. Agrupa la tabla por región
df_region = df.groupby("Region").agg(
    Operadores      =("Operador_Red", "count"), #"count" cuenta cuántos operadores hay por región.
    CU_Prom_Dic2025 =("CU_Dic2025",   "mean"), #"mean" calcula el promedio de cada columna numérica
    CU_Prom_Feb2026 =("CU_Feb2026",   "mean"),
    Variacion_Prom  =("Variacion_Pct","mean"),
).round(2).reset_index() #.round(2) redondea todo a 2 decimales.

# Guarda las dos tablas como archivos CSV en data/processed. encoding="utf-8-sig" garantiza que las tildes y la ñ se vean bien en Excel en español
df.to_csv(SALIDA_TARIFAS, index=False, encoding="utf-8-sig")
df_region.to_csv(SALIDA_REGION, index=False, encoding="utf-8-sig")

#Muestra en la terminal un mensaje confirmando que los archivos se crearon y cuántas filas tiene cada uno.
print("Archivos generados:")
print(f"  {SALIDA_TARIFAS}  ({len(df)} filas)")
print(f"  {SALIDA_REGION}  ({len(df_region)} filas)")
