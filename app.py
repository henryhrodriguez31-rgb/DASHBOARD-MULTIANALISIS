import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# Configuración de página
st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide", initial_sidebar_state="expanded")

# CSS Personalizado para Tarjetas KPI estilo Excel/Sheets
st.markdown("""
<style>
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
        text-align: left;
        margin-bottom: 10px;
    }
    .kpi-title {
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        color: #0f172a;
        font-size: 26px;
        font-weight: 700;
        margin-top: 4px;
        margin-bottom: 4px;
    }
    .kpi-badge-green {
        color: #16a34a;
        background-color: #dcfce7;
        font-size: 12px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 20px;
        display: inline-block;
    }
    .kpi-badge-red {
        color: #dc2626;
        background-color: #fee2e2;
        font-size: 12px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 20px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Plataforma de Dashboards & Analítica Executiva")

# ---------------------------------------------------------
# BARRA LATERAL
# ---------------------------------------------------------
st.sidebar.header("⚙️ Configuración")
tipo_analisis = st.sidebar.selectbox(
    "Dominio de Análisis:",
    ["Financiero / Cripto / Divisas", "Comercial / Ventas", "Estadística Avanzada"]
)
fuente_datos = st.sidebar.radio("Fuente de Datos:", ["Archivo Local (CSV/Excel)", "API en Tiempo Real"])

df = None

if fuente_datos == "Archivo Local (CSV/Excel)":
    archivo_subido = st.sidebar.file_uploader("Sube tu archivo:", type=["csv", "xlsx"])
    if archivo_subido is not None:
        try:
            df = pd.read_csv(archivo_subido) if archivo_subido.name.endswith('.csv') else pd.read_excel(archivo_subido)
            st.sidebar.success("¡Archivo cargado!")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
else:
    st.sidebar.subheader("🌐 Conexión API")
    cripto_id = st.sidebar.selectbox("Activo:", ["ethereum", "bitcoin", "tether", "binancecoin", "solana"])
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
            st.sidebar.success("¡Datos recuperados!")
        else:
            st.sidebar.error("Error al consultar la API.")

# ---------------------------------------------------------
# CONTENIDO PRINCIPAL
# ---------------------------------------------------------
if df is not None:
    columnas_validas = [c for c in df.columns if not c.startswith('Unnamed')]
    
    with st.expander("👀 Vista previa de la tabla de datos"):
        st.dataframe(df[columnas_validas].head(10), use_container_width=True)

    if tipo_analisis == "Financiero / Cripto / Divisas":
        st.subheader("📈 Analítica Financiera de Alto Impacto")
        
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
        cat_sel = st.multiselect("Filtrar Activos:", categorias_unicas, default=categorias_unicas[:1])

        if cat_sel:
            df_fin = df_sorted[df_sorted[col_categoria].isin(cat_sel)].copy()
            moneda_ref = cat_sel[0]
            df_ref = df_fin[df_fin[col_categoria] == moneda_ref]
            
            precio_actual = df_ref[col_valor].iloc[-1] if not df_ref.empty else 0
            precio_inicial = df_ref[col_valor].iloc[0] if not df_ref.empty else 0
            var_pct = ((precio_actual - precio_inicial) / precio_inicial) * 100 if precio_inicial != 0 else 0
            max_hist = df_fin[col_valor].max()
            min_hist = df_fin[col_valor].min()
            volatilidad = (df_fin[col_valor].std() / df_fin[col_valor].mean()) * 100 if df_fin[col_valor].mean() != 0 else 0

            # --- TARJETAS KPI ESTILO SHEETS/EXCEL ---
            k1, k2, k3, k4 = st.columns(4)
            
            badge_class = "kpi-badge-green" if var_pct >= 0 else "kpi-badge-red"
            badge_icon = "▲" if var_pct >= 0 else "▼"
            
            k1.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Último Precio ({moneda_ref})</div>
                <div class="kpi-value">${precio_actual:,.2f}</div>
                <span class="{badge_class}">{badge_icon} {var_pct:+.2f}%</span>
            </div>
            """, unsafe_allow_html=True)

            k2.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Máximo Registrado</div>
                <div class="kpi-value">${max_hist:,.2f}</div>
                <span style="color:#64748b; font-size:12px;">Pico del periodo</span>
            </div>
            """, unsafe_allow_html=True)

            k3.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Mínimo Registrado</div>
                <div class="kpi-value">${min_hist:,.2f}</div>
                <span style="color:#64748b; font-size:12px;">Piso del periodo</span>
            </div>
            """, unsafe_allow_html=True)

            k4.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Volatilidad Histórica</div>
                <div class="kpi-value">{volatilidad:.2f}%</div>
                <span style="color:#64748b; font-size:12px;">Riesgo relativo</span>
            </div>
            """, unsafe_allow_html=True)

            st.write("") # Espaciador visual

            # --- GRÁFICO TIPO EXCEL ESTILIZADO (AREA CHART) ---
            fig_area = px.area(
                df_fin, 
                x=col_fecha, 
                y=col_valor, 
                color=col_categoria,
                title="<b>Tendencia Histórica de Cotización</b>",
                labels={col_fecha: "Fecha", col_valor: "Precio (USD)", col_categoria: "Activo"},
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            # Estilizado avanzado de Plotly
            fig_area.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(248,250,252,1)",
                font=dict(family="Segoe UI, sans-serif", size=12, color="#334155"),
                xaxis=dict(showgrid=True, gridcolor="#e2e8f0"),
                yaxis=dict(showgrid=True, gridcolor="#e2e8f0", tickprefix="$"),
                hovermode="x unified",
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_area, use_container_width=True)

    elif tipo_analisis == "Comercial / Ventas":
        st.subheader("🛒 Dashboard Comercial Ejecutivo")
        c1, c2 = st.columns(2)
        with c1: col_prod = st.selectbox("Producto/Categoría:", columnas_validas, index=0)
        
        # Evitar que seleccione la misma columna para producto y monto por defecto
        idx_monto = 1 if len(columnas_validas) > 1 else 0
        with c2: col_monto = st.selectbox("Monto de Venta:", columnas_validas, index=idx_monto)
        
        if col_prod == col_monto:
            st.warning("⚠️ Selecciona columnas diferentes para Producto y Monto de Venta.")
        else:
            df_ventas = df.copy()
            
            # Limpieza segura de montos (elimina $, comas, espacios y guiones)
            df_ventas[col_monto] = pd.to_numeric(
                df_ventas[col_monto].astype(str).str.replace(r'[\$,\- ]', '', regex=True), 
                errors='coerce'
            ).fillna(0)

            ventas_totales = df_ventas[col_monto].sum()
            ticket_prom = df_ventas[col_monto].mean()
            cant_trans = len(df_ventas)
            
            # KPIs estilo tarjetas
            k1, k2, k3 = st.columns(3)
            k1.markdown(f'<div class="kpi-card"><div class="kpi-title">Ventas Totales</div><div class="kpi-value">${ventas_totales:,.2f}</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="kpi-card"><div class="kpi-title">Ticket Promedio</div><div class="kpi-value">${ticket_prom:,.2f}</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="kpi-card"><div class="kpi-title">Transacciones</div><div class="kpi-value">{cant_trans:,}</div></div>', unsafe_allow_html=True)
            
            # Agrupación segura evitando duplicados de nombres de columnas
            resumen = df_ventas.groupby(col_prod, as_index=False)[col_monto].sum()
            resumen = resumen.sort_values(by=col_monto, ascending=False).head(10)
            
            fig_bar = px.bar(
                resumen, x=col_monto, y=col_prod, orientation='h',
                title="<b>Top 10 Productos por Ventas</b>",
                color=col_monto, color_continuous_scale="Viridis",
                labels={col_monto: "Ventas (USD)", col_prod: "Producto"}
            )
            fig_bar.update_layout(yaxis=dict(autorange="reversed"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f8fafc")
            st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("👈 Selecciona una fuente de datos en el panel izquierdo para comenzar.")
