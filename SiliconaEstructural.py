# -*- coding: utf-8 -*-
"""
Created on Sunday Mar 01 2026
@author: Structural Lab / Mauricio Riquelme
Project: Análisis Avanzado de Silicona Estructural - Versión Extendida Full
Normativa: ASTM C1184 / NCh 2507 / AAMA Structural Glazing
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import os
import base64
from fpdf import FPDF
from datetime import datetime

# =================================================================
# 1. CONFIGURACIÓN CORPORATIVA Y ESTILO CSS EXTENDIDO
# =================================================================
# Se utiliza el modo 'wide' para maximizar el espacio de los gráficos y tablas.
st.set_page_config(
    page_title="Cálculo Silicona Estructural | Proyectos Estructurales", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de estilos CSS para métricas, cajas de advertencia y contenedores de resultados.
st.markdown("""
    <style>
    /* Contenedor principal */
    .main > div { padding-left: 3.5rem; padding-right: 3.5rem; max-width: 100%; }
    
    /* Estilo de métricas personalizadas */
    .stMetric { 
        background-color: #f8f9fa; 
        padding: 22px; 
        border-radius: 15px; 
        border: 1px solid #dee2e6;
        box-shadow: 3px 3px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .stMetric:hover { transform: translateY(-3px); }

    /* Caja de resultados críticos */
    .result-box { 
        background-color: #f0f7ff; 
        padding: 35px; 
        border-left: 12px solid #003366; 
        border-radius: 12px; 
        margin: 25px 0;
    }

    /* Caja de visualización de movimiento térmico */
    .thermal-display {
        background-color: #fff9e6;
        padding: 20px;
        border: 2px solid #ffcc00;
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        color: #856404;
        text-align: center;
        margin: 15px 0;
    }

    /* Caja de advertencia de peso */
    .weight-warning {
        background-color: #ffffff;
        padding: 20px;
        border: 3px dashed #d9534f;
        border-radius: 12px;
        margin-bottom: 30px;
        text-align: center;
    }

    /* Texto de pie de página */
    .footer-custom {
        text-align: center;
        color: #777;
        font-size: 0.9rem;
        margin-top: 60px;
        border-top: 2px solid #eee;
        padding-top: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. GESTIÓN DE RECURSOS EXTERNOS (LOGOS Y ASSETS)
# =================================================================
def convert_image_to_base64(path):
    """Codifica imágenes locales en string Base64 para visualización directa en HTML/CSS."""
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# Renderizado de logo corporativo en el encabezado
logo_encoded = convert_image_to_base64("Logo.png")
if logo_encoded:
    st.markdown(
        f'<div style="text-align: center; margin-bottom: 30px;">'
        f'<img src="data:image/png;base64,{logo_encoded}" width="450">'
        f'</div>', 
        unsafe_allow_html=True
    )

st.title("🧪 Análisis de Silicona Estructural")
st.markdown("#### **Determinación de Bite y Glueline Thickness según Movimiento Térmico Diferencial**")
st.divider()

# =================================================================
# 3. SIDEBAR: PANEL DE CONTROL DE PARÁMETROS TÉCNICOS
# =================================================================
st.sidebar.header("⚙️ Configuración del Análisis")

# 3.1 Geometría del Paño de Vidrio
with st.sidebar.expander("📐 Geometría del Cristal", expanded=True):
    ancho_v = st.number_input("Ancho del Vidrio (m)", value=1.50, step=0.05, format="%.2f")
    alto_v = st.number_input("Alto del Vidrio (m)", value=2.50, step=0.05, format="%.2f")
    esp_v = st.number_input("Espesor Nominal (mm)", value=10.0, step=1.0)
    # Lados para cálculo de área tributaria y dilatación
    l_menor = min(ancho_v, alto_v)
    l_mayor = max(ancho_v, alto_v)

# 3.2 Condiciones de Carga de Viento
with st.sidebar.expander("🌪️ Esfuerzos Climáticos (Viento)", expanded=True):
    presion_viento = st.number_input("Presión de Diseño (kgf/m²)", value=185.0, step=5.0)

# 3.3 Propiedades del Sistema y Silicona
with st.sidebar.expander("🧪 Propiedades Mecánicas y Térmicas", expanded=True):
    check_peso = st.checkbox("¿Silicona toma peso propio? (Corte)", value=False)
    
    # Visualización condicional de calzos según la decisión de carga
    if not check_peso:
        st.markdown("---")
        st.markdown("**📍 Esquema de Apoyos (Calzos)**")
        if os.path.exists("ubicacion_calzos.png"):
            st.image("ubicacion_calzos.png", caption="Ubicación normativa de calzos")
    
    st.markdown("---")
    # Esfuerzos admisibles según requerimiento
    f_viento_psi = st.number_input("Esfuerzo Adm. Viento (psi)", value=20.0, help="F_a.v para Bite")
    f_shear_psi = 20.0 # Tensión de corte fija para Glueline según requerimiento
    st.info(f"Esfuerzo Adm. Corte (F_a.s): {f_shear_psi} psi")
    
    f_peso_psi = st.number_input("Esfuerzo Adm. Peso (psi)", value=1.0, help="F_a.p para Bite Permanente")
    mod_e_sil = st.number_input("Módulo de Elasticidad E (MPa)", value=1.40, step=0.1)
    delta_temp = st.slider("Diferencial Térmico Máximo ΔT (°C)", 10, 80, 50)

# Factores de conversión técnica
# 1 psi = 0.070307 kgf/cm²
FACTOR_PSI_KG = 0.070307
fv_kg = f_viento_psi * FACTOR_PSI_KG
fs_kg = f_shear_psi * FACTOR_PSI_KG # 1.406 kgf/cm²
fp_kg = f_peso_psi * FACTOR_PSI_KG
E_kg = mod_e_sil * 10.19716

# Coeficientes de Dilatación Térmica (ASTM)
ALFA_ALU = 23.2e-6 # Aluminio 6063-T6
ALFA_VID = 9.0e-6  # Vidrio Flotado

# =================================================================
# 4. MOTOR DE CÁLCULO ESTRUCTURAL (ALGORITMOS)
# =================================================================
# 4.1 Cálculo del Peso del Cristal
peso_vidrio_kg = (ancho_v * alto_v * (esp_v / 1000)) * 2500 

# 4.2 Cálculo del Bite (B) por Viento
# B = (p * Lmin) / (200 * fv)
bite_req_viento = (presion_viento * l_menor) / (2 * fv_kg * 100) * 10 # mm

# 4.3 Cálculo del Bite (B) por Peso Propio (Corte)
if check_peso:
    perimetro_cm = 2 * (ancho_v + alto_v) * 100
    bite_req_peso = (peso_vidrio_kg / (perimetro_cm * fp_kg)) * 10 # mm
else:
    bite_req_peso = 0.0

# Bite de Diseño Final (Valor Crítico)
bite_diseno_final = max(bite_req_viento, bite_req_peso)

# 4.4 Cálculo del Glueline Thickness (gt) y Movimiento Térmico
# Amplitud diferencial térmica referenciada al centro (L/2)
mov_alu = ALFA_ALU * delta_temp * (l_mayor * 1000 / 2)
mov_vid = ALFA_VID * delta_temp * (l_mayor * 1000 / 2)
DT_amplitud = abs(mov_alu - mov_vid) # Movimiento térmico diferencial en mm

# Cálculo de espesor de junta (gt)
# Basado en tensión de corte (f_a.s = 20 psi)
gt_por_tension = (DT_amplitud * E_kg) / (3 * fs_kg)
# Basado en límite de capacidad de movimiento (25%)
gt_por_capacidad = DT_amplitud / 0.25
glueline_diseno_final = max(gt_por_tension, gt_por_capacidad)

# =================================================================
# 5. GENERACIÓN DE REPORTE TÉCNICO (PDF)
# =================================================================
def generate_engineering_pdf():
    """Genera la memoria de cálculo técnica en PDF."""
    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.add_page()
    
    # Cabecera con Logo
    if os.path.exists("Logo.png"):
        pdf.image("Logo.png", x=10, y=10, w=45)
    
    # Títulos
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 20, "MEMORIA TÉCNICA: ANÁLISIS DE SILICONA ESTRUCTURAL", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(100)
    pdf.cell(0, 5, f"Structural Lab Port | Analista: XXXXXX | Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(12)

    # 5.1 Datos del Proyecto
    pdf.set_fill_color(230, 240, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0)
    pdf.cell(0, 10, " 1. PARÁMETROS DE DISEÑO", ln=True, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f" Geometría Vidrio: {ancho_v} m x {alto_v} m (Espesor: {esp_v} mm)", ln=True)
    pdf.cell(0, 8, f" Presión de Diseño Viento (p): {presion_viento} kgf/m2", ln=True)
    pdf.cell(0, 8, f" Diferencial Térmico (Delta T): {delta_temp} C", ln=True)
    pdf.cell(0, 8, f" Esfuerzo Adm. Viento (fv): {f_viento_psi} psi", ln=True)
    pdf.cell(0, 8, f" Esfuerzo Adm. Corte (fs): {f_shear_psi} psi", ln=True)
    pdf.ln(5)

    # 5.2 Resultados Numéricos
    pdf.set_fill_color(230, 240, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, " 2. RESULTADOS DEL CÁLCULO", ln=True, fill=True)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, f" BITE DE DISEÑO FINAL (B): {bite_diseno_final:.2f} mm", ln=True)
    pdf.cell(0, 10, f" GLUELINE THICKNESS (gt): {glueline_diseno_final:.2f} mm", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f" Movimiento Térmico Diferencial (DT): {DT_amplitud:.4f} mm", ln=True)
    pdf.cell(0, 8, f" Requerimiento por Viento: {bite_req_viento:.2f} mm", ln=True)
    pdf.cell(0, 8, f" Requerimiento por Peso: {bite_req_peso:.2f} mm", ln=True)
    pdf.cell(0, 8, f" Peso del Cristal: {peso_vidrio_kg:.2f} kgf", ln=True)
    
    # Imagen de esquema en el PDF
    if os.path.exists("esquema_silicona.png"):
        pdf.ln(5)
        pdf.image("esquema_silicona.png", x=60, w=95)

    # Footer PDF
    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Documento elaborado por XXXXXX - 'Programming is understanding'", align='C')
    
    return pdf.output()

# Sidebar: Botón de Reporte
st.sidebar.markdown("---")
if st.sidebar.button("📄 Generar Reporte PDF Full"):
    try:
        pdf_raw = generate_engineering_pdf()
        b64_pdf = base64.b64encode(pdf_raw).decode()
        pdf_download_link = f'<a href="data:application/pdf;base64,{b64_pdf}" download="Memoria_Tecnica_Silicona.pdf" style="background-color:#ff9900;color:white;padding:12px 20px;text-decoration:none;border-radius:5px;font-weight:bold;display:block;text-align:center;">📥 DESCARGAR REPORTE</a>'
        st.sidebar.markdown(pdf_download_link, unsafe_allow_html=True)
        st.sidebar.success("Memoria generada exitosamente.")
    except Exception as e:
        st.sidebar.error(f"Error generando reporte: {e}")

# =================================================================
# 6. DESPLIEGUE DE RESULTADOS EN INTERFAZ (ORDEN SOLICITADO)
# =================================================================
st.subheader("📊 Resultados de Análisis Estructural")

# Alerta de condición de carga
if check_peso:
    st.markdown(
        f'<div class="weight-warning">'
        f'<p style="color:#d9534f; font-weight:bold; font-size:1.2em;">⚠️ SISTEMA SIN CALZOS: Silicona cargada con {peso_vidrio_kg:.2f} kgf (Esfuerzo de Corte)</p>'
        f'</div>', 
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<div class="weight-warning" style="border-color:#28a745;">'
        f'<p style="color:#28a745; font-weight:bold; font-size:1.2em;">✅ SISTEMA CON CALZOS: Peso soportado mecánicamente por apoyos</p>'
        f'</div>', 
        unsafe_allow_html=True
    )

# FILA 1: RESULTADOS DE BITE (FINAL | VIENTO | PESO)
col_res_a, col_res_b, col_res_c = st.columns(3)
with col_res_a:
    st.metric(
        "Bite de Diseño Mínimo", 
        f"{bite_diseno_final:.2f} mm", 
        help="Valor crítico final basado en la carga más desfavorable (Viento vs Peso)."
    )
with col_res_b:
    st.metric("Bite Requerido Viento", f"{bite_req_viento:.2f} mm")
with col_res_c:
    st.metric(
        "Bite Requerido Peso", 
        f"{bite_req_peso:.2f} mm" if check_peso else "N/A"
    )

st.divider()

# FILA 2: RESULTADOS DE GLUELINE Y MOVIMIENTO TÉRMICO
col_res_gt, col_res_dt = st.columns([1.5, 1])

with col_res_gt:
    st.metric(
        "Glueline Thickness (gt)", 
        f"{glueline_diseno_final:.2f} mm",
        help="Espesor de la silicona calculado con F_a.s = 20 psi para absorber DT."
    )
    st.caption(f"Criterio de cálculo: Tensión Adm. Corte = {f_shear_psi} psi")

with col_res_dt:
    st.markdown("**Movimiento Térmico Diferencial (DT):**")
    st.markdown(
        f'<div class="thermal-display">'
        f'DT = |ΔL_alu - ΔL_vid| = {DT_amplitud:.4f} mm'
        f'</div>', 
        unsafe_allow_html=True
    )
    st.caption(f"Para L_max = {l_mayor} m y ΔT = {delta_temp} °C")

# =================================================================
# 7. VISUALIZACIÓN DE ESQUEMAS Y ANÁLISIS GRÁFICO
# =================================================================
st.subheader("🖼️ Detalle Constructivo de la Junta")
if os.path.exists("esquema_silicona.png"):
    img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
    with img_col2:
        st.image(
            "esquema_silicona.png", 
            caption="Esquema Técnico: B (Bite) y gt (Glueline Thickness)", 
            use_column_width=True
        )



st.divider()
st.subheader("📈 Análisis de Sensibilidad")
plot_col1, plot_col2 = st.columns(2)

# Gráfico A: Sensibilidad del Bite a la Presión de Viento
with plot_col1:
    st.markdown("**Comportamiento del Bite vs Presión de Viento**")
    p_range = np.linspace(50, 450, 100)
    b_v_calc = [(p * l_menor) / (2 * fv_kg * 100) * 10 for p in p_range]
    fig_a, ax_a = plt.subplots(figsize=(10, 5))
    ax_a.plot(p_range, b_v_calc, color='#003366', lw=3, label="Requerimiento Viento")
    ax_a.axvline(presion_viento, color='red', linestyle='--', alpha=0.6, label="Presión Actual")
    ax_a.set_xlabel("Presión Viento (kgf/m²)"); ax_a.set_ylabel("Bite (mm)")
    ax_a.legend(); ax_a.grid(True, linestyle=':', alpha=0.6)
    st.pyplot(fig_a)

# Gráfico B: Sensibilidad del gt al Diferencial Térmico
with plot_col2:
    st.markdown("**Comportamiento del Glueline (gt) vs Delta Térmico**")
    dt_range = np.linspace(10, 90, 100)
    # Cálculo de gt basado en el diferencial térmico variable
    dt_amplitudes = [(l_mayor * 1000 / 2) * abs(ALFA_ALU - ALFA_VID) * dt for dt in dt_range]
    gt_calcs = [max((d * E_kg) / (3 * fs_kg), d / 0.25) for d in dt_amplitudes]
    fig_b, ax_b = plt.subplots(figsize=(10, 5))
    ax_b.plot(dt_range, gt_calcs, color='#d9534f', lw=3, label="Requerimiento Térmico")
    ax_b.axvline(delta_temp, color='black', linestyle='--', alpha=0.6, label="Delta T Actual")
    ax_b.set_xlabel("Diferencial Térmico (°C)"); ax_b.set_ylabel("Glueline Thickness (mm)")
    ax_b.legend(); ax_b.grid(True, linestyle=':', alpha=0.6)
    st.pyplot(fig_b)

# =================================================================
# 8. PIE DE PÁGINA CORPORATIVO
# =================================================================
st.markdown(
    f'<div class="footer-custom">'
    f'© {datetime.now().year} Mauricio Riquelme | Proyectos Estructurales Lab<br>'
    f'<em>"Programming is understanding, understanding is engineering."</em>'
    f'</div>', 
    unsafe_allow_html=True
)

# Fin del script silicona_estructural_final_pro.py
# Total de líneas estimadas: 340+
# =================================================================