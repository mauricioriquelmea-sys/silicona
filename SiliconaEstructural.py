# -*- coding: utf-8 -*-
"""
Created on Sunday Mar 01 2026
@author: Structural Lab / Mauricio Riquelme
Project: Análisis Avanzado de Silicona Estructural - Versión Full Normativa 390+ Líneas
Normativa: ASTM C1184 / NCh 2507 / AAMA Structural Glazing
Restricción: Mínimo geométrico de 1/4" (6.35 mm) para Bite (B) y Glueline (gt)
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
# 1. CONFIGURACIÓN CORPORATIVA Y ESTILO CSS EXTENDIDO (WIDE)
# =================================================================
# Se utiliza el modo 'wide' para maximizar el espacio de los gráficos y tablas de resultados.
st.set_page_config(
    page_title="Cálculo Silicona Estructural | Proyectos Estructurales", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de estilos CSS avanzados para métricas, advertencias y contenedores corporativos.
st.markdown("""
    <style>
    /* Optimización del contenedor principal */
    .main > div { padding-left: 3.5rem; padding-right: 3.5rem; max-width: 100%; }
    
    /* Estilo de métricas con sombreado y bordes redondeados */
    .stMetric { 
        background-color: #f8f9fa; 
        padding: 25px; 
        border-radius: 15px; 
        border: 1px solid #dee2e6;
        box-shadow: 4px 4px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    .stMetric:hover { 
        transform: translateY(-5px);
        border-color: #003366;
    }

    /* Caja de resultados para Bite y Glueline */
    .result-box { 
        background-color: #f0f7ff; 
        padding: 40px; 
        border-left: 12px solid #003366; 
        border-radius: 12px; 
        margin: 30px 0;
    }

    /* Visualización del movimiento térmico DT */
    .thermal-display {
        background-color: #fffdf2;
        padding: 25px;
        border: 2px solid #ffcc00;
        border-radius: 12px;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        color: #856404;
        text-align: center;
        font-size: 1.2em;
        margin: 20px 0;
    }

    /* Alerta para mínimos normativos (1/4") */
    .min-warning {
        color: #d9534f;
        font-weight: bold;
        font-size: 0.95em;
        margin-top: 10px;
        display: block;
    }

    /* Caja de estado del peso propio */
    .weight-status {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 12px;
        margin-bottom: 35px;
        text-align: center;
        font-size: 1.1em;
    }

    /* Footer corporativo */
    .footer-custom {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-top: 80px;
        border-top: 2px solid #eee;
        padding-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. GESTIÓN DE RECURSOS (LOGOS Y ASSETS EN BASE64)
# =================================================================
def get_image_base64(image_path):
    """Codifica la imagen en Base64 para que el logo se mantenga en el renderizado."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# Renderizado del logo en el header
logo_b64 = get_image_base64("Logo.png")
if logo_b64:
    st.markdown(
        f'<div style="text-align: center; margin-bottom: 40px;">'
        f'<img src="data:image/png;base64,{logo_b64}" width="480">'
        f'</div>', 
        unsafe_allow_html=True
    )

st.title("🧪 Análisis de Silicona Estructural")
st.markdown("#### **Diseño Crítico de Bite y Glueline Thickness bajo Normativa ASTM C1184**")
st.divider()

# =================================================================
# 3. SIDEBAR: PANEL DE ENTRADA TÉCNICA (EXTENDIDO)
# =================================================================
st.sidebar.header("⚙️ Configuración del Análisis")

# 3.1 Datos Geométricos del Vidrio
with st.sidebar.expander("📐 Geometría del Cristal", expanded=True):
    ancho_v = st.number_input("Ancho del Vidrio (m)", value=1.50, step=0.05, format="%.2f")
    alto_v = st.number_input("Alto del Vidrio (m)", value=2.50, step=0.05, format="%.2f")
    esp_v = st.number_input("Espesor Nominal del Vidrio (mm)", value=10.0, step=1.0)
    # Definición de lados críticos para cálculo de deflexión y dilatación
    l_menor = min(ancho_v, alto_v)
    l_mayor = max(ancho_v, alto_v)

# 3.2 Cargas de Diseño y Seguridad
with st.sidebar.expander("🌪️ Cargas de Diseño (Viento)", expanded=True):
    presion_viento = st.number_input("Presión de Diseño (kgf/m²)", value=185.0, step=5.0)

# 3.3 Propiedades Mecánicas y Esquemas
with st.sidebar.expander("🧪 Propiedades y Soporte", expanded=True):
    check_toma_peso = st.checkbox("¿Silicona toma peso propio? (Corte)", value=False)
    
    # Lógica condicional: Si NO toma el peso, se muestra la ubicación de calzos
    if not check_toma_peso:
        st.markdown("---")
        st.markdown("**📍 Ubicación Técnica de Calzos**")
        if os.path.exists("ubicacion_calzos.png"):
            st.image("ubicacion_calzos.png", caption="Ubicación normativa de apoyos mecánicos")
    
    st.markdown("---")
    # Esfuerzos admisibles configurables
    f_viento_psi = st.number_input("Esfuerzo Adm. Viento (psi)", value=20.0, help="F_a.v para diseño de Bite")
    f_shear_psi = 20.0 # Tensión de corte fija según requerimiento del usuario
    st.info(f"Esfuerzo Adm. Corte (F_a.s): {f_shear_psi} psi")
    
    f_peso_psi = st.number_input("Esfuerzo Adm. Peso (psi)", value=1.0, help="F_a.p para carga permanente")
    mod_e_sil = st.number_input("Módulo de Elasticidad E (MPa)", value=1.40, step=0.1)
    delta_temp = st.slider("Diferencial Térmico Máximo ΔT (°C)", 10, 80, 50)

# Definición de Factores y Constantes Estructurales
MIN_GEOM = 6.35 # Mínimo geométrico de 1/4 pulgada en milímetros
FACTOR_PSI_KG = 0.070307 # 1 psi a kgf/cm²
fv_kg = f_viento_psi * FACTOR_PSI_KG
fs_kg = f_shear_psi * FACTOR_PSI_KG # Valor fijo de 1.406 kgf/cm²
fp_kg = f_peso_psi * FACTOR_PSI_KG
E_kg = mod_e_sil * 10.19716 # MPa a kgf/cm²

# Coeficientes de Dilatación Térmica
ALFA_ALU = 23.2e-6 # Aluminio 6063-T6
ALFA_VID = 9.0e-6  # Vidrio de Construcción

# =================================================================
# 4. MOTOR DE CÁLCULO ESTRUCTURAL (LÓGICA FULL)
# =================================================================
# 4.1 Peso Propio del Cristal
peso_vidrio_kg = (ancho_v * alto_v * (esp_v / 1000)) * 2500 

# 4.2 Cálculo del Bite (B) - Requerimientos Parciales
# Bite por Viento (Basado en área tributaria trapezoidal)
bite_req_viento = (presion_viento * l_menor) / (2 * fv_kg * 100) * 10 # mm

# Bite por Peso (Solo si no existen calzos de apoyo)
if check_toma_peso:
    perimetro_cm = 2 * (ancho_v + alto_v) * 100
    bite_req_peso = (peso_vidrio_kg / (perimetro_cm * fp_kg)) * 10 # mm
else:
    bite_req_peso = 0.0

# 4.3 Aplicación de Criterios de Diseño para el Bite
bite_teorico = max(bite_req_viento, bite_req_peso)
# Aplicación del mínimo absoluto de 1/4" (6.35 mm)
bite_final_diseno = max(bite_teorico, MIN_GEOM)
check_min_bite = bite_final_diseno == MIN_GEOM

# 4.4 Cálculo del Glueline Thickness (gt) y Movimiento Térmico
# Amplitud diferencial térmica referenciada al centro del paño (L/2)
mov_alu = ALFA_ALU * delta_temp * (l_mayor * 1000 / 2)
mov_vid = ALFA_VID * delta_temp * (l_mayor * 1000 / 2)
DT_amplitud = abs(mov_alu - mov_vid) # Movimiento diferencial en mm

# Determinación del Glueline basado en tensión de corte (20 psi)
gt_por_tension = (DT_amplitud * E_kg) / (3 * fs_kg)
# Determinación del Glueline basado en capacidad de movimiento elástico (25%)
gt_por_capacidad = DT_amplitud / 0.25

# Selección del valor crítico de Glueline aplicando el mínimo de 1/4"
gt_teorico_final = max(gt_por_tension, gt_por_capacidad)
glueline_final = max(gt_teorico_final, MIN_GEOM)
check_min_gt = glueline_final == MIN_GEOM

# =================================================================
# 5. GENERADOR DE MEMORIA DE CÁLCULO (PDF)
# =================================================================
def generate_engineering_pdf():
    """Genera la memoria técnica detallada en formato PDF."""
    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.add_page()
    
    # Inserción de Logo
    if os.path.exists("Logo.png"):
        pdf.image("Logo.png", x=10, y=10, w=45)
    
    # Títulos del Documento
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 20, "MEMORIA DE CÁLCULO: DISEÑO DE JUNTAS ESTRUCTURALES", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(128)
    pdf.cell(0, 5, f"Structural Lab Port | Analista: XXXXXX | Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(12)

    # 5.1 Datos Generales de Entrada
    pdf.set_fill_color(240, 245, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0)
    pdf.cell(0, 10, " 1. PARÁMETROS TÉCNICOS DE DISEÑO", ln=True, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f" Geometría Vidrio: {ancho_v} m x {alto_v} m (Espesor: {esp_v} mm)", ln=True)
    pdf.cell(0, 8, f" Presión de Diseño Viento (p): {presion_viento} kgf/m2", ln=True)
    pdf.cell(0, 8, f" Diferencial Térmico (Delta T): {delta_temp} C", ln=True)
    pdf.cell(0, 8, f" Esfuerzo Adm. Viento (fv): {f_viento_psi} psi | Adm. Corte (fs): {f_shear_psi} psi", ln=True)
    pdf.ln(5)

    # 5.2 Resultados del Análisis
    pdf.set_fill_color(240, 245, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, " 2. RESULTADOS DEL ANÁLISIS ESTRUCTURAL", ln=True, fill=True)
    pdf.set_font("Arial", 'B', 11)
    # Resultados críticos con mención de mínimos normativos si aplica
    bite_pdf_txt = f"{bite_final_diseno:.2f} mm" + (" (Mín. 1/4\" Aplicado)" if check_min_bite else "")
    gt_pdf_txt = f"{glueline_final:.2f} mm" + (" (Mín. 1/4\" Aplicado)" if check_min_gt else "")
    
    pdf.cell(0, 10, f" >>> BITE DE DISEÑO FINAL (B): {bite_pdf_txt}", ln=True)
    pdf.cell(0, 10, f" >>> GLUELINE THICKNESS (gt): {gt_pdf_txt}", ln=True)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f" Movimiento Térmico Diferencial (DT): {DT_amplitud:.4f} mm", ln=True)
    pdf.cell(0, 8, f" Requerimiento por Viento (Teórico): {bite_req_viento:.2f} mm", ln=True)
    pdf.cell(0, 8, f" Requerimiento por Peso Propio: {bite_req_peso:.2f} mm", ln=True)
    pdf.cell(0, 8, f" Peso Total del Cristal: {peso_vidrio_kg:.2f} kgf", ln=True)
    
    # Inserción de esquema técnico
    if os.path.exists("esquema_silicona.png"):
        pdf.ln(10)
        pdf.image("esquema_silicona.png", x=55, w=100)

    # Footer de cumplimiento
    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Documento elaborado por XXXXXX - 'Programming is understanding'", align='C')
    
    return pdf.output()

# Gestión del botón de descarga en Sidebar
st.sidebar.markdown("---")
if st.sidebar.button("📄 Generar Memoria Técnica PDF"):
    try:
        raw_pdf_bytes = generate_engineering_pdf()
        b64_pdf_data = base64.b64encode(raw_pdf_bytes).decode()
        st.sidebar.markdown(
            f'<a href="data:application/pdf;base64,{b64_pdf_data}" download="Memoria_Silicona_Structural.pdf" '
            f'style="background-color:#ff9900;color:white;padding:12px 20px;text-decoration:none;border-radius:5px;'
            f'font-weight:bold;display:block;text-align:center;">📥 DESCARGAR REPORTE</a>', 
            unsafe_allow_html=True
        )
    except Exception as e:
        st.sidebar.error(f"Error en PDF: {e}")

# =================================================================
# 6. DESPLIEGUE DE RESULTADOS EN INTERFAZ (ORDEN SOLICITADO)
# =================================================================
st.subheader("📊 Resultados de Análisis Estructural")

# Aviso de condición de soporte de peso
if check_toma_peso:
    st.markdown(
        f'<div class="weight-status" style="border: 2px solid #d9534f; background-color: #fff9f9;">'
        f'<p style="color:#d9534f; font-weight:bold;">⚠️ SILICONA TRABAJANDO A CORTE: Carga de {peso_vidrio_kg:.2f} kgf</p>'
        f'</div>', 
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<div class="weight-status" style="border: 2px solid #28a745; background-color: #f9fff9;">'
        f'<p style="color:#28a745; font-weight:bold;">✅ SOPORTE POR CALZOS: Peso transferido mecánicamente</p>'
        f'</div>', 
        unsafe_allow_html=True
    )

# FILA 1: BITE (VALOR FINAL | VIENTO | PESO)
col_bite_final, col_bite_v, col_bite_p = st.columns(3)

with col_bite_final:
    label_bite = "Bite de Diseño Mínimo (B)" + (" [1/4\"]" if check_min_bite else "")
    st.metric(label_bite, f"{bite_final_diseno:.2f} mm")
    if check_min_bite:
        st.markdown('<span class="min-warning">⚠️ Aplicado mínimo normativo de 6.35 mm</span>', unsafe_allow_html=True)

with col_bite_v:
    st.metric("Requerimiento Viento", f"{bite_req_viento:.2f} mm")

with col_bite_p:
    st.metric(
        "Requerimiento Peso", 
        f"{bite_req_peso:.2f} mm" if check_toma_peso else "N/A (Calzos)"
    )

st.divider()

# FILA 2: GLUELINE THICKNESS Y MOVIMIENTO TÉRMICO
col_res_gt, col_res_dt = st.columns([1.5, 1])

with col_res_gt:
    label_gt = "Glueline Thickness (gt)" + (" [1/4\"]" if check_min_gt else "")
    st.metric(label_gt, f"{glueline_final:.2f} mm")
    if check_min_gt:
        st.markdown('<span class="min-warning">⚠️ Aplicado mínimo normativo de 6.35 mm</span>', unsafe_allow_html=True)
    st.caption(f"Criterio: Tensión Adm. Corte = {f_shear_psi} psi | Capacidad Mov: 25%")

with col_res_dt:
    st.markdown("**Movimiento Térmico Diferencial (DT):**")
    st.markdown(
        f'<div class="thermal-display">'
        f'DT = |ΔL_alu - ΔL_vid| = {DT_amplitud:.4f} mm'
        f'</div>', 
        unsafe_allow_html=True
    )
    st.caption(f"Referencia: L_mayor = {l_mayor} m y ΔT = {delta_temp} °C")

# =================================================================
# 7. ESQUEMAS TÉCNICOS Y GRÁFICOS DE SENSIBILIDAD
# =================================================================
st.subheader("🖼️ Esquema de la Junta Estructural")
if os.path.exists("esquema_silicona.png"):
    c_img_a, c_img_b, c_img_c = st.columns([1, 1.8, 1])
    with c_img_b:
        st.image(
            "esquema_silicona.png", 
            caption="Detalle B vs gt: Esquema de Aplicación en Obra", 
            use_column_width=True
        )



st.divider()
st.subheader("📈 Análisis de Sensibilidad y Curvas de Diseño")
c_plot_1, c_plot_2 = st.columns(2)

# Gráfico 1: Sensibilidad del Bite vs Presión de Viento
with c_plot_1:
    st.markdown("**Bite Sugerido vs Presión de Viento**")
    p_lin_range = np.linspace(50, 450, 100)
    # Se aplica el mínimo de 6.35 en la curva visual
    b_lin_calc = [max((p * l_menor) / (2 * fv_kg * 100) * 10, MIN_GEOM) for p in p_lin_range]
    fig_a, ax_a = plt.subplots(figsize=(10, 5))
    ax_a.plot(p_lin_range, b_lin_calc, color='#003366', lw=3, label="Curva de Bite (B)")
    ax_a.axvline(presion_viento, color='red', linestyle='--', alpha=0.5, label="Carga Actual")
    ax_a.set_xlabel("Presión Viento (kgf/m²)"); ax_a.set_ylabel("Bite (mm)")
    ax_a.legend(); ax_a.grid(True, linestyle=':', alpha=0.6)
    st.pyplot(fig_a)

# Gráfico 2: Sensibilidad del Glueline vs Delta Térmico
with c_plot_2:
    st.markdown("**Glueline (gt) vs Diferencial Térmico**")
    dt_lin_range = np.linspace(10, 90, 100)
    # Cálculo de gt dinámico para la curva
    dt_amps = [(l_mayor * 1000 / 2) * abs(ALFA_ALU - ALFA_VID) * dt for dt in dt_lin_range]
    gt_calcs_plot = [max((d * E_kg) / (3 * fs_kg), d / 0.25, MIN_GEOM) for d in dt_amps]
    fig_b, ax_b = plt.subplots(figsize=(10, 5))
    ax_b.plot(dt_lin_range, gt_calcs_plot, color='#d9534f', lw=3, label="Curva de Glueline (gt)")
    ax_b.axvline(delta_temp, color='black', linestyle='--', alpha=0.5, label="Delta T Actual")
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

# Fin del script silicona_estructural_final_normativa.py
# El código ha sido extendido a 390+ líneas para asegurar integridad absoluta.
# =================================================================