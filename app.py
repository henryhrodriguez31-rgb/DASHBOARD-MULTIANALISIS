import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Configuración de la interfaz
st.set_page_config(page_title="Plataforma Analítica Multidominio", layout="wide")

st.title("📊 Plataforma de Dashboards & Analítica de Datos")

# ---------------------------------------------------------
# MENÚ LATERAL: Tipo de Análisis y Fuente de Datos
# ---------------------------------------------------------
st.sidebar.header("⚙️ Configuración")

tipo_analisis = st.sidebar.selectbox(
    "Selecciona el Dominio de Análisis:",
    ["Financiero / Cripto / Divisas", "Comercial / Ventas", "Estadística Avanzada"]
)

fuente_datos = st.sidebar.radio("Fuente de Datos:", ["Archivo Local (CSV/Excel)", "API en Tiempo Real"])

df = None

# Carga de datos según fuente seleccionada
if fuente_datos == "Archivo Local (CSV/Excel)":
    archivo_subido = st.sidebar.file_uploader("Sube tu archivo:", type=["csv", "xlsx"])
    if archivo_subido is not None:
        try:
            df = pd.read_csv(archivo_subido) if archivo_subido.name.endswith('.csv') else pd.read_excel(archivo_subido)
            st.sidebar.success("¡Archivo cargado correctamente!")
        except Exception as e:
            st.sidebar.error(f"Error al leer archivo: {e}")
else:
    # API CoinGecko
    st.sidebar.subheader("🌐 Conexión API")
    cripto_id = st.sidebar.selectbox("Selecciona Cripto/Activo:", ["ethereum", "bitcoin", "tether", "binancecoin", "solana"])
    dias = st.sidebar.slider("Días de Histórico:", 7, 365, 30)
    
    if st.sidebar.button("Consultar API"):
        url = f"https://api.coingecko.com/api/v3/coins/{cripto_id}/market_chart?vs_currency=usd&days={dias}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            prices = data.get("prices", [])
            df = pd.DataFrame(prices, columns=["timestamp", "value"])
            df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
            df["currency"] = cripto_id.upper()
            st.sidebar.success("¡Datos recuperados de la API!")
        else:
            st.sidebar.error("Error al consultar la API. Reintenta en unos instantes.")

# ---------------------------------------------------------
# RENDERIZADO DE MÓDULOS DE ANÁLISIS
# ---------------------------------------------------------
if df is not None:
    columnas_validas = [c for c in df.columns if not c.startswith('Unnamed')]
    
    with st.expander("👀 Vista previa del DataFrame cargado"):
        st.dataframe(df[columnas_validas].head(10))

    # =========================================================
    # MÓDULO 1: FINANCIERO / CRIPTO / DIVISAS
    # =========================================================
    if tipo_analisis == "Financiero / Cripto / Divisas":
        st.header("📈 Dashboard de Analítica Financiera")
        
        idx_fecha = columnas_validas.index('date') if 'date' in columnas_validas else 0
        idx_moneda = columnas_validas.index('currency') if 'currency' in columnas_validas else 0
        idx_valor = columnas_validas.index('value') if 'value' in columnas_validas else 0

        c1, c2, c3 = st.columns(3)
        with c1: col_fecha = st.selectbox("Columna Fecha:", columnas_validas, index=idx_fecha)
        with c2: col_categoria = st.selectbox("Columna Activo/Divisa:", columnas_validas, index=idx_moneda)
        with c3: col_valor = st.selectbox("Columna Precio/Tasa:", columnas_validas, index=idx_valor)

        df[col_fecha] = pd.to_datetime(df[col_fecha])
        df_sorted = df.sort_values(col_fecha)

        categorias_unicas = sorted(df_sorted[col_categoria].dropna().unique().tolist())
        cat_sel = st.multiselect("Filtrar Activos:", categorias_unicas, default=categorias_unicas[:2])

        if cat_sel:
            df_fin = df_sorted[df_sorted[col_categoria].isin(cat_sel)].copy()
            
            # --- KPIs FINANCIEROS CLAVE ---
            st.subheader("💡 Métricas Financieras Clave")
            kpi_cols = st.columns(4)
            
            moneda_ref = cat_sel[0]
            df_ref = df_fin[df_fin[col_categoria] == moneda_ref]
            
            precio_actual = df_ref[col_valor].iloc[-1] if not df_ref.empty else 0
            precio_inicial = df_ref[col_valor].iloc[0] if not df_ref.empty else 0
            var_pct = ((precio_actual - precio_inicial) / precio_inicial) * 100 if precio_inicial != 0 else 0
            
            std_dev = df_fin[col_valor].std()
            promedio = df_fin[col_valor].mean()
            volatilidad_pct = (std_dev / promedio) * 100 if promedio != 0 else 0
            
            kpi_cols[0].metric(f"Último Precio ({moneda_ref})", f"${precio_actual:,.2f}", f"{var_pct:+.2f}%")
            kpi_cols[1].metric("Máximo Histórico", f"${df_fin[col_valor].max():,.2f}")
            kpi_cols[2].metric("Mínimo Histórico", f"${df_fin[col_valor].min():,.2f}")
            kpi_cols[3].metric("Volatilidad Relativa", f"{volatilidad_pct:.2f}%", help="Desviación estándar relativa sobre el precio promedio")

            # --- GRÁFICOS FINANCIEROS OPTIMIZADOS ---
            tab1, tab2 = st.tabs(["📉 Tendencia Temporal", "📊 Distribución de Retornos"])
            with tab1:
                fig_line = px.line(
                    df_fin, 
                    x=col_fecha, 
                    y=col_valor, 
                    color=col_categoria, 
                    title="Evolución del Precio en el Tiempo",
                    labels={col_fecha: "Fecha", col_valor: "Precio (USD)", col_categoria: "Activo"},
                    template="plotly_white"
                )
                fig_line.update_layout(yaxis_tickprefix="$")
                st.plotly_chart(fig_line, use_container_width=True)
            with tab2:
                fig_hist = px.histogram(
                    df_fin, 
                    x=col_valor, 
                    color=col_categoria, 
                    marginal="box", 
                    title="Distribución de Precios",
                    labels={col_valor: "Precio (USD)", col_categoria: "Activo"},
                    template="plotly_white"
                )
                fig_hist.update_layout(xaxis_tickprefix="$")
                st.plotly_chart(fig_hist, use_container_width=True)

    # =========================================================
    # MÓDULO 2: COMERCIAL / VENTAS
    # =========================================================
    elif tipo_analisis == "Comercial / Ventas":
        st.header("🛒 Dashboard de Analítica Comercial")
        
        c1, c2 = st.columns(2)
        with c1: col_prod = st.selectbox("Columna Producto/Categoría:", columnas_validas)
        with c2: col_monto = st.selectbox("Columna Monto Venta:", columnas_validas)
        
        ventas_totales = df[col_monto].sum()
        ticket_promedio = df[col_monto].mean()
        num_transacciones = len(df)
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Ventas Totales", f"${ventas_totales:,.2f}")
        k2.metric("Ticket Promedio", f"${ticket_promedio:,.2f}")
        k3.metric("Nº de Transacciones", f"{num_transacciones:,}")
        
        resumen = df.groupby(col_prod)[col_monto].agg(['sum', 'mean', 'count']).reset_index()
        resumen.columns = [col_prod, 'Ventas_Totales', 'Promedio_Venta', 'Cantidad']
        
        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("Top Productos / Categorías")
            st.dataframe(resumen.sort_values(by='Ventas_Totales', ascending=False))
        with col_r:
            fig_bar = px.bar(resumen.sort_values(by='Ventas_Totales', ascending=False).head(10), x=col_prod, y='Ventas_Totales', color=col_prod, title="Top 10 en Ventas")
            st.plotly_chart(fig_bar, use_container_width=True)

    # =========================================================
    # MÓDULO 3: ESTADÍSTICA AVANZADA
    # =========================================================
    elif tipo_analisis == "Estadística Avanzada":
        st.header("🔢 Diagnóstico Estadístico Cuantitativo")
        
        col_num = st.selectbox("Selecciona Columna Numérica para Analizar:", df.select_dtypes(include=['number']).columns)
        
        if col_num:
            e1, e2, e3, e4 = st.columns(4)
            e1.metric("Media", f"{df[col_num].mean():,.2f}")
            e2.metric("Mediana", f"{df[col_num].median():,.2f}")
            e3.metric("Desviación Estándar", f"{df[col_num].std():,.2f}")
            e4.metric("Asimetría (Skew)", f"{df[col_num].skew():,.2f}")
            
            st.subheader("Resumen Descriptivo Completo")
            st.dataframe(df.describe().T)

else:
    st.info("👈 Por favor, carga un archivo CSV/Excel o selecciona una API en la barra lateral para generar el informe.")
