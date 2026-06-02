from pathlib import Path
import pandas as pd

# ==========================================
# RUTAS
# ==========================================

RAW_PATH = Path("data/raw")
PROCESSED_PATH = Path("data/processed")

PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

# ==========================================
# ARCHIVOS EXCEL
# ==========================================

excel_files = (
    list(RAW_PATH.glob("*.xlsx")) +
    list(RAW_PATH.glob("*.xlsm"))
)

print("\nArchivos encontrados:\n")

for file in excel_files:
    print(f"📄 {file.name}")

# ==========================================
# HOJAS A EXCLUIR
# ==========================================

EXCLUIR = [
    "PORTADA",
    "PRESENT",
    "INDICE",
    "ÍNDICE",
    "VARIACION",
    "GRAF",
    "BASE",
    "T3",
    "T7",
    "TRANSMISION",
    "DISTRIBUCION",
    "ADD",
    "ALFAS",
    "HOJAS"
]

# ==========================================
# MAPA EMPRESA → DEPARTAMENTO
# ==========================================

MAPA_EMPRESAS = {
    "CEDENAR": "Nariño",
    "CELSIA COLOMBIA Valle": "Valle del Cauca",
    "CELSIA COLOMBIA Tolima": "Tolima",
    "CENS": "Norte de Santander",
    "CEO": "Cauca",
    "CETSA": "Chocó",
    "CHEC": "Caldas",
    "ENEL COLOMBIA": "Bogotá/Cundinamarca",
    "DISPAC": "Chocó",
    "EBSA": "Boyacá",
    "EDEQ": "Quindío",
    "EE Putumayo": "Putumayo",
    "EEBP": "Boyacá",
    "EEP PEREIRA": "Risaralda",
    "EEP CARTAGO": "Valle del Cauca",
    "AIR-E": "Atlántico/Magdalena/La Guajira",
    "AFINIA": "Caribe",
    "ELECTROCAQUETÁ": "Caquetá",
    "ELECTROHUILA": "Huila",
    "EMCALI": "Valle del Cauca",
    "EMEESA": "Meta",
    "EMEVASI": "Valle del Cauca",
    "EMSA": "Meta",
    "ENELAR": "Arauca",
    "ENERCA": "Casanare",
    "ENERGUAVIARE": "Guaviare",
    "EPM": "Antioquia",
    "ESSA": "Santander",
    "RUITOQUE": "Santander"
}

# ==========================================
# DATAFRAME FINAL
# ==========================================

df_final = pd.DataFrame()

# ==========================================
# RECORRER ARCHIVOS
# ==========================================

for archivo in excel_files:

    print(f"\n{'='*60}")
    print(f"Procesando archivo: {archivo.name}")
    print(f"{'='*60}")

    try:

        xls = pd.ExcelFile(archivo)

        # ==========================================
        # RECORRER HOJAS
        # ==========================================

        for sheet in xls.sheet_names:

            nombre = sheet.upper()

            excluir = any(
                palabra in nombre
                for palabra in EXCLUIR
            )

            if excluir:
                continue

            print(f"\nProcesando empresa: {sheet}")

            empresa = sheet.split(".")[-1].strip()

            departamento = MAPA_EMPRESAS.get(
                empresa,
                "DESCONOCIDO"
            )

            # ==========================================
            # LEER HOJA
            # ==========================================

            df = pd.read_excel(
                archivo,
                sheet_name=sheet,
                header=None
            )

            # ==========================================
            # BUSCAR FILA TABLA
            # ==========================================

            fila_tabla = None

            for i in range(len(df)):

                fila = df.iloc[i].astype(str).str.upper()

                if fila.str.contains("ESTRATO").any():

                    fila_tabla = i
                    break

            if fila_tabla is None:
                continue

            # ==========================================
            # CREAR TABLA
            # ==========================================

            encabezados = df.iloc[fila_tabla + 1]

            tabla = df.iloc[fila_tabla + 2:].copy()

            tabla.columns = encabezados

            # ==========================================
            # LIMPIAR COLUMNAS
            # ==========================================

            tabla.columns = [
                str(col).strip()
                for col in tabla.columns
            ]

            # eliminar vacías
            tabla = tabla.loc[
                :,
                ~tabla.columns.str.contains("^nan$")
            ]

            # ==========================================
            # ELIMINAR DUPLICADOS
            # ==========================================

            tabla = tabla.loc[
                :,
                ~tabla.columns.duplicated()
            ]

            # ==========================================
            # AGREGAR FECHA
            # ==========================================

            tabla.insert(
                0,
                "FECHA",
                df.iloc[fila_tabla + 2:, 0].values
            )

            # ==========================================
            # RESET INDEX
            # ==========================================

            tabla = tabla.reset_index(drop=True)

            print("\nColumnas finales:")
            print(tabla.columns.tolist())

            # ==========================================
            # COLUMNAS NECESARIAS
            # ==========================================

            columnas_usuario = [
                "FECHA",
                "AÑO",
                "PERIODO",
                "ESTRATO 1",
                "ESTRATO 2",
                "ESTRATO 3",
                "ESTRATO 4",
                "ESTRATO 5 y 6, Ind y Com"
            ]

            faltantes = [
                col for col in columnas_usuario
                if col not in tabla.columns
            ]

            if faltantes:

                print(f"❌ Faltan columnas: {faltantes}")
                continue

            # ==========================================
            # TABLA USUARIO
            # ==========================================

            tabla_usuario = tabla[
                columnas_usuario
            ].copy()

            # ==========================================
            # EMPRESA Y DEPARTAMENTO
            # ==========================================

            tabla_usuario["EMPRESA"] = empresa
            tabla_usuario["DEPARTAMENTO"] = departamento

            # ==========================================
            # FORMATO LARGO
            # ==========================================

            tabla_larga = tabla_usuario.melt(
                id_vars=[
                    "FECHA",
                    "AÑO",
                    "PERIODO",
                    "EMPRESA",
                    "DEPARTAMENTO"
                ],
                value_vars=[
                    "ESTRATO 1",
                    "ESTRATO 2",
                    "ESTRATO 3",
                    "ESTRATO 4",
                    "ESTRATO 5 y 6, Ind y Com"
                ],
                var_name="ESTRATO",
                value_name="TARIFA"
            )

            # ==========================================
            # LIMPIAR ESTRATO
            # ==========================================

            tabla_larga["ESTRATO"] = (
                tabla_larga["ESTRATO"]
                .str.replace("ESTRATO ", "", regex=False)
            )

            # ==========================================
            # LIMPIAR TARIFA
            # ==========================================

            tabla_larga["TARIFA"] = pd.to_numeric(
                tabla_larga["TARIFA"],
                errors="coerce"
            )

            tabla_larga = tabla_larga.dropna(
                subset=["TARIFA"]
            )

            # ==========================================
            # CONCATENAR
            # ==========================================

            df_final = pd.concat(
                [df_final, tabla_larga],
                ignore_index=True
            )

            print(f"✅ Registros: {len(df_final)}")

    except Exception as e:

        print(f"\n❌ Error archivo {archivo.name}")
        print(e)

# ==========================================
# LIMPIEZA FINAL
# ==========================================

if not df_final.empty:

    df_final = df_final.drop_duplicates()

    df_final = df_final.reset_index(drop=True)

# ==========================================
# EXPORTAR CSV
# ==========================================

csv_output = (
    PROCESSED_PATH /
    "tarifas_consolidadas.csv"
)

df_final.to_csv(
    csv_output,
    index=False
)

# ==========================================
# EXPORTAR EXCEL
# ==========================================

excel_output = (
    PROCESSED_PATH /
    "tarifas_consolidadas.xlsx"
)

df_final.to_excel(
    excel_output,
    index=False
)

# ==========================================
# FINAL
# ==========================================

print("\n====================================")
print("PROCESO FINALIZADO")
print("====================================")

print(f"\nTotal registros: {len(df_final)}")

print("\nVista previa:\n")

print(df_final.head())

print(f"\nCSV:\n{csv_output}")

print(f"\nEXCEL:\n{excel_output}")