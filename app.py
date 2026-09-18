import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y ESTILOS CSS
# ==========================================
st.set_page_config(
    page_title="Multi-Dashboard Analítico Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Estilos globales y tarjetas KPI */
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #334155;
    }
    .stMetric label {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
    }
    .stMetric div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DICCIONARIO DE ENFOQUES DE ANÁLISIS
# ==========================================
OPCIONES_ANALISIS = {
    "Comercial / Ventas": [
        "Resumen General de Ventas",
        "Análisis de Concentración (Pareto 80/20)",
        "Distribución y Variabilidad del Ticket"
    ],
    "Financiero / Presupuesto": [
        "Estructura y Totales de Ingresos / Gastos",
        "Análisis de Distribución de Costos",
        "Desviación y Márgenes"
    ],
    "Educación / Académico": [
        "Rendimiento Académico General",
        "Análisis de Aprobación vs Reprobación",
        "Distribución de Calificaciones (Boxplot)"
    ],
    "Estadístico / Científico": [
        "Estadística Descriptiva Completa",
        "Matriz de Correlación",
        "Detección de Valores Atípicos (Outliers)"
    ]
}

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
st.sidebar.title("⚙️ Configuración")

# 1. Selección de Dominio Principal
tipo_analisis = st.sidebar.selectbox(
    "Dominio de Análisis:",
    list(OPCIONES_ANALISIS.keys())
)

# 2. Selección de Sub-análisis Dinámico
sub_analisis = st.sidebar.selectbox(
    "Enfoque Analítico Específico:",
    OPCIONES_ANALISIS[tipo_analisis]
)

st.sidebar.markdown("---")
fuente_datos = st.sidebar.radio("Fuente de Datos:", ["Archivo Local (CSV/Excel)", "API en Tiempo Real / Demo"])

df = None

if fuente_datos == "Archivo Local (CSV/Excel)":
    uploaded_file = st.sidebar.file_uploader("Sube tu archivo data:", type=["csv", "xlsx", "xls"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.sidebar.success("¡Archivo cargado con éxito!")
        except Exception as e:
            st.sidebar.error(f"Error al leer el archivo: {e}")
else:
    try:
        # Reemplaza la URL con la API que vas a consumir
        url_api = "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=usd" 
        respuesta = requests.get(url_api)
        datos_json = respuesta.json()
        
        # Convertimos la respuesta a DataFrame
        df = pd.DataFrame(datos_json)
        
        st.sidebar.success("¡Datos cargados exitosamente desde la API!")
    except Exception as e:
        st.sidebar.error(f"Error al conectar con la API: {e}")
        })
    elif tipo_analisis == "Financiero / Presupuesto":
        conceptos = ["Nómina", "Marketing", "Infraestructura", "Servicios", "Suministros", "Ventas Proyectadas"]
        df = pd.DataFrame({
            "Concepto": np.random.choice(conceptos, size=n),
            "Monto": np.random.uniform(500, 15000, size=n)
        })
    elif tipo_analisis == "Educación / Académico":
        materias = ["Matemáticas", "Física", "Química", "Programación", "Estadística"]
        df = pd.DataFrame({
            "Materia": np.random.choice(materias, size=n),
            "Nota": np.random.normal(loc=14, scale=3.5, size=n).clip(0, 20)
        })
    else: # Estadístico / Científico
        df = pd.DataFrame({
            "Variable_A": np.random.normal(50, 10, n),
            "Variable_B": np.random.normal(100, 25, n),
            "Variable_C": np.random.exponential(20, n),
            "Monto": np.random.normal(250, 50, n)
        })
    st.sidebar.info("Cargados datos de demostración automáticos.")

# ==========================================
# CUERPO PRINCIPAL DEL DASHBOARD
# ==========================================
st.title("📊 Multi-Dashboard Analítico Interactivo")

if df is not None:
    columnas_validas = list(df.columns)
    
    # ---------------------------------------------------
    # MÓDULO 1: COMERCIAL / VENTAS
    # ---------------------------------------------------
    if tipo_analisis == "Comercial / Ventas":
        st.subheader(f"🛒 Análisis Comercial: {sub_analisis}")
        
        c1, c2 = st.columns(2)
        with c1: col_prod = st.selectbox("Categoría / Producto / País:", columnas_validas, index=0)
        idx_monto = 1 if len(columnas_validas) > 1 else 0
        with c2: col_monto = st.selectbox("Monto de Venta / Valor:", columnas_validas, index=idx_monto)
        
        if col_prod == col_monto:
            st.warning("⚠️ Selecciona columnas diferentes para la Categoría y el Monto.")
        else:
            df_v = df.copy()
            df_v[col_monto] = pd.to_numeric(
                df_v[col_monto].astype(str).str.replace(r'[\$,\- ]', '', regex=True), 
                errors='coerce'
            ).fillna(0)

            if sub_analisis == "Resumen General de Ventas":
                ventas_totales = df_v[col_monto].sum()
                ticket_prom = df_v[col_monto].mean()
                cant_trans = len(df_v)
                
                k1, k2, k3 = st.columns(3)
                k1.metric("Ventas Totales", f"${ventas_totales:,.2f}")
                k2.metric("Ticket Promedio", f"${ticket_prom:,.2f}")
                k3.metric("Transacciones", f"{cant_trans:,}")

                resumen = df_v.groupby(col_prod, as_index=False)[col_monto].sum().sort_values(by=col_monto, ascending=False).head(10)
                
                fig = px.bar(
                    resumen, x=col_monto, y=col_prod, orientation='h',
                    title="<b>Top 10 en Ventas Totalizadas</b>",
                    color=col_monto, color_continuous_scale="Viridis",
                    labels={col_monto: "Ventas (USD)", col_prod: "Categoría"}
                )
                fig.update_layout(yaxis=dict(autorange="reversed"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.5)", font=dict(color="#f8fafc"))
                st.plotly_chart(fig, use_container_width=True)

            elif sub_analisis == "Análisis de Concentración (Pareto 80/20)":
                resumen = df_v.groupby(col_prod, as_index=False)[col_monto].sum().sort_values(by=col_monto, ascending=False)
                ventas_totales = resumen[col_monto].sum()
                resumen['pct_acumulado'] = (resumen[col_monto].cumsum() / ventas_totales) * 100 if ventas_totales > 0 else 0
                
                top_20_count = int(max(1, np.ceil(len(resumen) * 0.2)))
                ventas_top_20 = resumen.head(top_20_count)[col_monto].sum()
                concentracion_real = (ventas_top_20 / ventas_totales * 100) if ventas_totales > 0 else 0
                
                k1, k2, k3 = st.columns(3)
                k1.metric("Total Categorías/Países", f"{len(resumen)}")
                k2.metric("Top 20% Grupos Contabilizados", f"{top_20_count}")
                k3.metric("Concentración Top 20% (Pareto)", f"{concentracion_real:.1f}%")

                fig = px.line(
                    resumen, x=col_prod, y='pct_acumulado',
                    title="<b>Curva Acumulada de Ingresos (Regla Pareto 80/20)</b>",
                    markers=True, labels={col_prod: "Categoría", 'pct_acumulado': "% Acumulado"}
                )
                fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Límite Pareto 80%")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.5)", font=dict(color="#f8fafc"), yaxis=dict(ticksuffix="%"))
                st.plotly_chart(fig, use_container_width=True)

            elif sub_analisis == "Distribución y Variabilidad del Ticket":
                mediana = df_v[col_monto].median()
                desv_est = df_v[col_monto].std()
                val_max = df_v[col_monto].max()
                
                k1, k2, k3 = st.columns(3)
                k1.metric("Mediana del Monto", f"${mediana:,.2f}")
                k2.metric("Desviación Estándar", f"${desv_est:,.2f}")
                k3.metric("Monto Máximo Transaccionado", f"${val_max:,.2f}")

                fig = px.box(
                    df_v, x=col_prod, y=col_monto, color=col_prod,
                    title="<b>Distribución de Valores por Categoria (Boxplot)</b>",
                    labels={col_monto: "Monto", col_prod: "Categoría"}
                )
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.5)", font=dict(color="#f8fafc"))
                st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------
    # MÓDULO 2: FINANCIERO / PRESUPUESTO
    # ---------------------------------------------------
    elif tipo_analisis == "Financiero / Presupuesto":
        st.subheader(f"💰 Análisis Financiero: {sub_analisis}")
        
        c1, c2 = st.columns(2)
        with c1: col_cat = st.selectbox("Concepto / Categoría:", columnas_validas, index=0)
        idx_num = 1 if len(columnas_validas) > 1 else 0
        with c2: col_val = st.selectbox("Monto / Importe:", columnas_validas, index=idx_num)
        
        df_f = df.copy()
        df_f[col_val] = pd.to_numeric(df_f[col_val].astype(str).str.replace(r'[\$,\- ]', '', regex=True), errors='coerce').fillna(0)

        if sub_analisis == "Estructura y Totales de Ingresos / Gastos":
            monto_total = df_f[col_val].sum()
            promedio = df_f[col_val].mean()
            num_registros = len(df_f)
            
            k1, k2, k3 = st.columns(3)
            k1.metric("Monto Total Evaluado", f"${monto_total:,.2f}")
            k2.metric("Importe Promedio", f"${promedio:,.2f}")
            k3.metric("Total Registros", f"{num_registros:,}")

            resumen_f = df_f.groupby(col_cat, as_index=False)[col_val].sum()
            fig = px.pie(resumen_f, names=col_cat, values=col_val, title="<b>Distribución Porcentual por Concepto</b>", hole=0.4)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc"))
            st.plotly_chart(fig, use_container_width=True)

        elif sub_analisis == "Análisis de Distribución de Costos":
            resumen_f = df_f.groupby(col_cat, as_index=False)[col_val].sum().sort_values(by=col_val, ascending=False)
            fig = px.bar(resumen_f, x=col_cat, y=col_val, title="<b>Estructura Desglosada por Categoría</b>", color=col_val, color_continuous_scale="Reds")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.5)", font=dict(color="#f8fafc"))
            st.plotly_chart(fig, use_container_width=True)

        elif sub_analisis == "Desviación y Márgenes":
            std_val = df_f[col_val].std()
            max_val = df_f[col_val].max()
            min_val = df_f[col_val].min()

            k1, k2, k3 = st.columns(3)
            k1.metric("Desviación Estándar", f"${std_val:,.2f}")
            k2.metric("Monto Máximo", f"${max_val:,.2f}")
            k3.metric("Monto Mínimo", f"${min_val:,.2f}")

            fig = px.histogram(df_f, x=col_val, nbins=20, title="<b>Frecuencia y Dispersión de Registros Financieros</b>", color_discrete_sequence=['#38bdf8'])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.5)", font=dict(color="#f8fafc"))
            st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------
    # MÓDULO 3: EDUCACIÓN / ACADÉMICO
    # ---------------------------------------------------
    elif tipo_analisis == "Educación / Académico":
        st.subheader(f"🎓 Análisis Académico: {sub_analisis}")
        
        c1, c2 = st.columns(2)
        with c1: col_grupo = st.selectbox("Materia / Curso / Grupo:", columnas_validas, index=0)
        idx_nota = 1 if len(columnas_validas) > 1 else 0
        with c2: col_nota = st.selectbox("Calificación / Nota:", columnas_validas, index=idx_nota)
        
        df_e = df.copy()
        df_e[col_nota] = pd.to_numeric(df_e[col_nota], errors='coerce').fillna(0)

        if sub_analisis == "Rendimiento Académico General":
            prom_gen = df_e[col_nota].mean()
            mediana_nota = df_e[col_nota].median()
            total_eval = len(df_e)

            k1, k2, k3 = st.columns(3)
            k1.metric("Promedio General", f"{prom_gen:.2f}")
            k2.metric("Calificación Mediana", f"{mediana_nota:.2f}")
            k3.metric("Estudiantes / Evaluaciones", f"{total_eval}")

            resumen_e = df_e.groupby(col_grupo, as_index=False)[col_nota].mean().sort_values(by=col_nota, ascending=False)
            fig = px.bar(resumen_e, x=col_grupo, y=col_nota, title="<b>Promedio por Materia / Grupo</b>", color=col_nota, color_continuous_scale="Blues")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.5)", font=dict(color="#f8fafc"))
            st.plotly_chart(fig, use_container_width=True)

        elif sub_analisis == "Análisis de Aprobación vs Reprobación":
            corte_aprob = st.slider("Nota Mínima de Aprobación:", min_value=0, max_value=100, value=10 if df_e[col_nota].max() <= 20 else 60)
            
            aprobados = len(df_e[df_e[col_nota] >= corte_aprob])
            reprobados = len(df_e[df_e[col_nota] < corte_aprob])
            pct_aprob = (aprobados / len(df_e) * 100) if len(df_e) > 0 else 0

            k1, k2, k3 = st.columns(3)
            k1.metric("Aprobados", f"{aprobados}")
            k2.metric("Reprobados", f"{reprobados}")
            k3.metric("Tasa de Aprobación", f"{pct_aprob:.1f}%")

            df_status = pd.DataFrame({"Estado": ["Aprobado", "Reprobado"], "Cantidad": [aprobados, reprobados]})
            fig = px.pie(df_status, names="Estado", values="Cantidad", title="<b>Proporción Aprobados vs Reprobados</b>", color="Estado", color_discrete_map={"Aprobado": "#22c55e", "Reprobado": "#ef4444"})
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc"))
            st.plotly_chart(fig, use_container_width=True)

        elif sub_analisis == "Distribución de Calificaciones (Boxplot)":
            fig = px.box(df_e, x=col_grupo, y=col_nota, color=col_grupo, title="<b>Dispersión de Notas por Materia</b>")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.5)", font=dict(color="#f8fafc"))
            st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------
    # MÓDULO 4: ESTADÍSTICO / CIENTÍFICO
    # ---------------------------------------------------
    elif tipo_analisis == "Estadístico / Científico":
        st.subheader(f"🔬 Análisis Estadístico: {sub_analisis}")
        
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(num_cols) == 0:
            st.error("No se encontraron columnas numéricas en el dataset cargado.")
        else:
            if sub_analisis == "Estadística Descriptiva Completa":
                st.write("<b>Resumen Cuantitativo:</b>", unsafe_allow_html=True)
                st.dataframe(df[num_cols].describe().T.style.background_gradient(cmap="viridis"))

            elif sub_analisis == "Matriz de Correlación":
                corr_matrix = df[num_cols].corr()
                fig = px.imshow(corr_matrix, text_auto=True, title="<b>Matriz de Correlación de Pearson</b>", color_continuous_scale="Viridis")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc"))
                st.plotly_chart(fig, use_container_width=True)

            elif sub_analisis == "Detección de Valores Atípicos (Outliers)":
                col_sel = st.selectbox("Selecciona Variable Numérica:", num_cols)
                
                q1 = df[col_sel].quantile(0.25)
                q3 = df[col_sel].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - (1.5 * iqr)
                upper_bound = q3 + (1.5 * iqr)
                outliers = df[(df[col_sel] < lower_bound) | (df[col_sel] > upper_bound)]

                k1, k2, k3 = st.columns(3)
                k1.metric("Rango Intercuartílico (IQR)", f"{iqr:.2f}")
                k2.metric("Límite Inferior / Superior", f"{lower_bound:.1f} / {upper_bound:.1f}")
                k3.metric("Total Outliers Detectados", f"{len(outliers)}")

                fig = px.box(df, y=col_sel, points="all", title=f"<b>Análisis de Atípicos para {col_sel}</b>")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.5)", font=dict(color="#f8fafc"))
                st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👈 Por favor, carga un archivo CSV/Excel en la barra lateral o selecciona 'API en Tiempo Real / Demo'.")
