import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control de Llaves", layout="wide")

# 1. Cargar los datos desde el Excel
@st.cache_data(ttl=10) # Se actualiza cada 10 segundos
def cargar_datos():
    xls = pd.ExcelFile("Inventario_Llaves.xlsx")
    inv = pd.read_excel(xls, "inventario")
    dia = pd.read_excel(xls, "diario")
    fij = pd.read_excel(xls, "fijas")
    return inv, dia, fij

df_inv, df_dia, df_fij = cargar_datos()

# 2. Computar estados en tiempo real (Sustituye las fórmulas de Excel)
# Cuenta cuántas llaves están afuera en el registro diario (devuelve está vacío)
prestadas_hoy = df_dia[df_dia['devuelve'].isna() | (df_dia['devuelve'] == '')].groupby('id_llave').size()
# Cuenta cuántas están asignadas fijas (fecha_baja está vacía)
asignadas_fijas = df_fij[df_fij['fecha_baja'].isna() | (df_fij['fecha_baja'] == '')].groupby('id_llave').size()

# Unir los conteos al inventario maestro
df_inv = df_inv.set_index('id_llave')
df_inv['Prestadas Diario'] = prestadas_hoy
df_inv['Asignadas Fijas'] = asignadas_fijas
df_inv.fillna(0, inplace=True)
df_inv['Disponibles en Tablero'] = df_inv['stock_total'] - df_inv['Prestadas Diario'] - df_inv['Asignadas Fijas']
df_inv.reset_index(inplace=True)

# 3. Interfaz Gráfica de la Web
st.title("🔑 Sistema de Gestión y Control de Llaves")

menu = st.sidebar.selectbox("Menú de Navegación", ["Tablero de Control", "Registrar Salida Diario", "Asignaciones Fijas"])

if menu == "Tablero de Control":
    st.subheader("📊 Estado Actual del Tablero Físico")
    # Mostrar la tabla interactiva con alertas de color
    st.dataframe(df_inv.style.background_gradient(subset=['Disponibles en Tablero'], cmap='Blues'))

elif menu == "Registrar Salida Diario":
    st.subheader("📋 Formulario de Préstamo Diario")
    with st.form("formulario_prestamo"):
        fecha = st.date_input("Fecha", datetime.now())
        id_llave = st.selectbox("Seleccione la Llave", df_inv['id_llave'].unique())
        
        # Muestra el destino automáticamente al seleccionar la llave
        destino_actual = df_inv[df_inv['id_llave'] == id_llave]['destino'].values[0]
        st.info(f"📍 Destino de esta llave: {destino_actual}")
        
        retira = st.text_input("Nombre de quien retira")
        
        enviar = st.form_submit_button("Registrar Salida")
        if enviar:
            # Aquí se agregaría la lógica para guardar la fila en el Excel
            st.success(f"¡Llave {id_llave} registrada con éxito para {retira}!")