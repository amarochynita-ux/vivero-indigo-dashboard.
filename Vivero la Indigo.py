import pandas as pd
import streamlit as st
import numpy as np 
import plotly.express as px

# 1. Configuración de página (Esto debe ir al principio)
st.set_page_config(page_title="Vivero la Indigo", layout="wide")

# 2. Carga de datos
df = pd.read_csv("vivero_datos.csv")
df_ventas = pd.read_csv("ventas_simuladas.csv")

# Limpieza inicial
df_ventas.columns = df_ventas.columns.str.strip()
df_ventas['Fecha'] = pd.to_datetime(df_ventas['Fecha'])
# Ajustamos el nombre de la columna según tu archivo (Ultima_Riego)
df['Ultima_Riego'] = pd.to_datetime(df['Ultima_Riego']).dt.normalize()

# --- 3. BARRA LATERAL (Filtros y Utilidades) ---
st.sidebar.header("🛠️ Panel de Control")

# Filtro de Mes
meses = df_ventas['Fecha'].dt.month_name().unique()
mes_seleccionado = st.sidebar.selectbox("Selecciona un mes:", ["Todos"] + list(meses))

if mes_seleccionado != "Todos":
    df_ventas = df_ventas[df_ventas['Fecha'].dt.month_name() == mes_seleccionado]

# Buscador de Plantas
st.sidebar.divider()
planta_buscada = st.sidebar.text_input("🔍 Buscar planta por nombre:")
if planta_buscada:
    resultado = df[df['Nombre'].str.contains(planta_buscada, case=False)]
    st.sidebar.dataframe(resultado[['Nombre', 'Stock', 'Precio']])

# Botón de Descarga
st.sidebar.divider()
csv = df_ventas.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Descargar Reporte de Ventas",
    data=csv,
    file_name='reporte_vivero.csv',
    mime='text/csv',
)

# --- 4. DISEÑO PRINCIPAL ---
st.title("🌱 Vivero la Indigo - Control Total")

# Sección: Métricas Financieras (KPIs)
st.header("📌 Resumen Ejecutivo")
valor_total_inventario = (df['Stock'] * df['Precio']).sum()
total_plantas = df['Stock'].sum()
planta_cara = df.loc[df['Precio'].idxmax()]

col_valor, col_cantidad, col_destacado = st.columns(3)
with col_valor:
    st.metric(label="💰 Valor Inventario", value=f"${valor_total_inventario:,.2f}")
with col_cantidad:
    st.metric(label="📦 Stock Total", value=f"{total_plantas} unidades")
with col_destacado:
    st.metric(label="💎 Planta Premium", value=planta_cara['Nombre'], delta=f"${planta_cara['Precio']}")

st.divider()

# Sección: Alertas Operativas
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚠️ Stock Bajo (< 5)")
    plantas_agotandose = df[df['Stock'] < 5]
    if not plantas_agotandose.empty:
        st.dataframe(plantas_agotandose[['Nombre', 'Stock']], use_container_width=True)
    else:
        st.success("Inventario al día.")

with col2:
    st.subheader("💧 Alerta de Riego")
    hoy = pd.Timestamp.now().normalize()
    df['Dias_desde_ultimo_riego'] = (hoy - df['Ultima_Riego']).dt.days
    necesitan_riego = df[df['Dias_desde_ultimo_riego'] > 7]
    if not necesitan_riego.empty:
        st.warning(f"{len(necesitan_riego)} plantas necesitan agua")
        st.dataframe(necesitan_riego[['Nombre', 'Dias_desde_ultimo_riego']], use_container_width=True)
    else:
        st.success("Todo regado.")
        
# --- NUEVA SECCIÓN: CONTROL POR TEMPORADA ---
st.header("🌦️ Guía de Cuidados Estacionales")

# Diccionario de consejos según el mes
consejos_temporada = {
    'January': '❄️ Invierno: Reduce el riego a la mitad. Protege las plantas tropicales del frío.',
    'February': '❄️ Invierno: Momento ideal para podar árboles frutales y preparar la tierra.',
    'March': '🌸 Primavera: Inicia el abonado general. Aumenta el riego gradualmente.',
    'April': '🌸 Primavera: Época de trasplantes. Vigila la aparición de los primeros pulgones.',
    'May': '🌸 Primavera: Máxima floración. Asegura buena ventilación en el invernadero.',
    'June': '☀️ Verano: Riego frecuente (temprano o tarde). Usa mallas de sombreo.',
    'July': '☀️ Verano: Control estricto de humedad. Pulveriza agua en hojas de sombra.',
    'August': '☀️ Verano: Evita trasplantes con calor extremo. Limpia hojas secas.',
    'September': '🍂 Otoño: Reduce fertilizantes. Recolecta semillas de flores de verano.',
    'October': '🍂 Otoño: Prepara acolchados para proteger raíces. Disminuye el riego.',
    'November': '🍂 Otoño: Limpieza de restos vegetales. Menos luz, menos agua.',
    'December': '❄️ Invierno: Atención a las heladas. Las nochebuenas necesitan luz indirecta.'
}

# Obtener el mes actual del sistema
mes_actual = pd.Timestamp.now().month_name()
recomendacion = consejos_temporada.get(mes_actual, "Revisa el calendario de cultivo local.")

# Mostrar en un cuadro llamativo
st.info(f"**Mes actual: {mes_actual}** \n\n {recomendacion}")


# Sección: Gráficas de Ventas
st.header("📊 Análisis de Ventas")
ventas_por_mes = df_ventas.groupby('Mes')['Ventas'].sum().reset_index()

c1, c2 = st.columns([2, 1])
with c1:
    st.bar_chart(data=ventas_por_mes, x='Mes', y='Ventas', color="#2E7D32")
with c2:
    total_v = df_ventas['Ventas'].sum()
    st.metric(label="Ingresos del Periodo", value=f"${total_v:,.2f}")

# Sección: Tendencia Temporal
st.header("📈 Tendencia de Ventas")
ventas_diarias = df_ventas.groupby(df_ventas['Fecha'].dt.date)['Ventas'].sum().reset_index()
fig_linea = px.line(ventas_diarias, x='Fecha', y='Ventas', markers=True, color_discrete_sequence=['#2E7D32'])
st.plotly_chart(fig_linea, use_container_width=True)

# Sección: Gestión de Tareas
st.divider()
if st.button('📋 Generar Lista de Tareas para Hoy'):
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.write("**Riego Urgente:**")
        for p in necesitan_riego['Nombre'].head(5): st.write(f"- {p}")
    with col_t2:
        st.write("**Reponer Stock:**")
        for p in plantas_agotandose['Nombre'].head(5): st.write(f"- {p}")

# Sección: Datos Crudos
with st.expander("🔍 Ver base de datos completa"):
    st.write("Ventas Filtradas:", df_ventas)
    st.write("Inventario:", df)
    
# --- SECCIÓN: SEMÁFORO DE SALUD DEL VIVERO ---
st.header("🚦 Semáforo de Salud Operativa")

# 1. Calculamos los estados
total_items = len(df)
con_stock_ok = len(df[df['Stock'] >= 5])
con_riego_ok = len(df[df['Dias_desde_ultimo_riego'] <= 7])

# Creamos una lista con los estados para la gráfica
estados_salud = pd.DataFrame({
    'Estado': ['Inventario OK', 'Riego al Día', 'Alertas (Bajo Stock/Secas)'],
    'Cantidad': [con_stock_ok, con_riego_ok, (total_items - con_stock_ok) + (total_items - con_riego_ok)]
})

# 2. Creamos la gráfica circular
fig_semaforo = px.pie(
    estados_salud, 
    values='Cantidad', 
    names='Estado',
    hole=0.5,
    color='Estado',
    color_discrete_map={
        'Inventario OK': '#2E7D32',      # Verde
        'Riego al Día': '#1976D2',       # Azul
        'Alertas (Bajo Stock/Secas)': '#FF4B4B' # Rojo
    }
)

st.plotly_chart(fig_semaforo, use_container_width=True)







