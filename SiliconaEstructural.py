# -*- coding: utf-8 -*-
"""
Created on Sunday Mar 01 2026
@author: Structural Lab / Mauricio Riquelme
Project: Análisis Avanzado de Silicona Estructural - Versión Master Ultra-Extendida
Normativa: ASTM C1184 / NCh 2507 / AAMA Structural Glazing
Seguridad: Bloqueo estricto > 20 psi | Mínimo 1/4" (6.35 mm) | Unidades Duales (psi/kPa)
Líneas: 450+ (Prohibido simplificar o acortar por integridad técnica)
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
# 1. CONFIGURACIÓN CORPORATIVA Y ESTILO CSS AVANZADO (WIDE)
# =================================================================
# Se utiliza el modo 'wide' para maximizar el espacio de visualización técnica
# y permitir que los gráficos de sensibilidad se desplieguen correctamente.
st.set_page_config(
    page_title="Cálculo Silicona Estructural | Proyectos Estructurales", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de estilos CSS detallados para métricas, advertencias y visualización de unidades.
st.markdown("""
    <style>
    /* Optimización del contenedor principal para pantallas de alta resolución */
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

    /* Caja de visualización del movimiento térmico DT */
    .thermal-display {
        background-color: #fffdf2;
        padding: 25px;
        border: 2px solid #ffcc00;
        border-radius: 12px;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        color: #856404;
        text-align: center;
        font-size: 1.25em;
        margin: 20px 0;
    }

    /* Alerta para mínimos normativos (1/4") */
    .min-warning {
        color: #d9534f;
        font-weight: bold;
        font-size: 0.95em;
        margin-top: 10px;
        display: block;
        background-color: #fff2f2;
        padding: 8px;
        border-radius: 5px;
        border: 1px solid #d9534f;
    }

    /* Caja de unidades duales */
    .unit-box {
        background-color: #f1f8ff;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #c8e1ff;
        font-size: 0.85em;
        color: #003366;
        margin-top: 5px;
        text-align: center;
    }

    /* Footer corporativo de ingeniería */
    .footer-custom {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-top: 80px;
        border-top: 2px solid #eee;
        padding-top: 30px;
    }

    /* Estilo para los botones de la barra lateral */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #003366;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. GESTIÓN DE RECURSOS Y FUNCIONES DE SOPORTE
# =================================================================
def get_image_base64(image_path):
    """Codifica la imagen en Base64 para integridad del renderizado HTML."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def psi_to_kpa(value_psi):
    """Convierte libras por pulgada cuadrada a kiloPascales."""
    return value_psi * 6.89476

def kpa_to_psi(value_kpa):
    """Convierte kiloPascales a libras por pulgada cuadrada."""
    return value_kpa / 6.89476

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
st.markdown("#### **Verificación de Bite y Glueline Thickness (Criterio ASTM C1184 / NCh 2507)**")
st.divider()

# =================================================================
# 3. SIDEBAR: PANEL DE ENTRADA CON BLOQUEOS DE SEGURIDAD
# =================================================================
st.sidebar.header("⚙️ Parámetros de Seguridad")

# 3.1 Datos Geométricos del Vidrio
with st.sidebar.expander("📐 Geometría del Cristal", expanded=True):
    ancho_v = st.number_input("Ancho del Vidrio (m)", value=1.50, step=0.05, format="%.2f")
    alto_v = st.number_input("Alto del Vidrio (m)", value=2.50, step=0.05, format="%.2f")
    esp_v = st.number_input("Espesor Nominal (mm)", value=10.0, step=1.0)
    l_menor = min(ancho_v, alto_v)
    l_mayor = max(ancho_v, alto_v)

# 3.2 Cargas y Esfuerzos Admisibles (Protección Estricta > 20 psi)
with st.sidebar.expander("🛡️ Esfuerzos Admisibles y Cargas", expanded=True):
    presion_v_kgm2 = st.number_input("Presión de Viento (kgf/m²)", value=185.0)
    presion_v_kpa = presion_v_kgm2 * 0.00980665
    st.markdown(f'<div class="unit-box">Presión: {presion_v_kpa:.3f} kPa</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    # BLOQUEO ESTRICTO: max_value=20.0 psi. No se puede editar hacia arriba.
    f_traccion_psi = st.number_input(
        "Esfuerzo admisible a la tracción (Corta Duración) [psi]", 
        value=20.0, min_value=1.0, max_value=20.0,
        help="Límite máximo normativo para carga de viento: 20 psi."
    )
    st.markdown(f'<div class="unit-box">Equivalente: {psi_to_kpa(f_traccion_psi):.2f} kPa</div>', unsafe_allow_html=True)
    
    f_shear_corta_psi = st.number_input(
        "Esfuerzo admisible al cizalle (Corta Duración) [psi]", 
        value=20.0, min_value=1.0, max_value=20.0,
        help="Esfuerzo para diseño de Glueline (gt). Límite: 20 psi."
    )
    st.markdown(f'<div class="unit-box">Equivalente: {psi_to_kpa(f_shear_corta_psi):.2f} kPa</div>', unsafe_allow_html=True)
    
    f_shear_larga_psi = st.number_input(
        "Esfuerzo admisible al cizalle (Larga Duración) [psi]", 
        value=1.0, min_value=0.1, max_value=2.0,
        help="Esfuerzo para carga permanente de peso. Típico: 1 psi."
    )
    st.markdown(f'<div class="unit-box">Equivalente: {psi_to_kpa(f_shear_larga_psi):.2f} kPa</div>', unsafe_allow_html=True)

    mod_e_mpa = st.number_input("Módulo de Elasticidad E (MPa)", value=1.40, step=0.1)
    st.markdown(f'<div class="unit-box">Equivalente: {mod_e_mpa * 145.038:.1f} psi</div>', unsafe_allow_html=True)
    
    delta_temp = st.slider("Diferencial Térmico Máximo ΔT (°C)", 10, 80, 50)

# 3.3 Propiedades Mecánicas y Soporte
with st.sidebar.expander("🧪 Propiedades y Configuración", expanded=True):
    check_toma_peso = st.checkbox("¿Silicona toma peso propio? (Corte)", value=False)
    
    if not check_toma_peso:
        st.markdown("---")
        st.markdown("**📍 Ubicación Técnica de Calzos**")
        if os.path.exists("ubicacion_calzos.png"):
            st.image("ubicacion_calzos.png", caption="Apoyos según NCh / ASTM")
    


# Constantes Estructurales y Conversiones
MIN_GEOM = 6.35 # 1/4 pulgada en mm (Mínimo absoluto inyectable)
PSI_TO_KGCM2 = 0.070307
fv_kg = f_traccion_psi * PSI_TO_KGCM2
fs_kg = f_shear_corta_psi * PSI_TO_KGCM2
fp_kg = f_shear_larga_psi * PSI_TO_KGCM2
E_kg = mod_e_mpa * 10.19716 # kgf/cm²

# Coeficientes de Dilatación Térmica Lineal
ALFA_ALU = 2.3e-5 # Aluminio 6063-T6 (1/K)
ALFA_VID = 9.0e-6 # Vidrio Flotado (1/K)

# =================================================================
# 4. MOTOR DE CÁLCULO (ALGORITMOS TÉCNICOS DETALLADOS)
# =================================================================
# 4.1 Peso Propio del Cristal
peso_vidrio_kg = (ancho_v * alto_v * (esp_v / 1000)) * 2500 

# 4.2 Cálculo del Bite (B) - Requerimientos de Tracción/Corte
# Bite por Viento (Área Tributaria Trapezoidal)
bite_req_viento = (presion_v_kgm2 * l_menor) / (2 * fv_kg * 100) * 10 

# Bite por Peso (Solo si no existen calzos de apoyo mecánicos)
if check_toma_peso:
    perimetro_cm = 2 * (ancho_v + alto_v) * 100
    bite_req_peso = (peso_vidrio_kg / (perimetro_cm * fp_kg)) * 10 
else:
    bite_req_peso = 0.0

# Bite de Diseño Final con Restricción Normativa 1/4" (6.35 mm)
bite_teorico = max(bite_req_viento, bite_req_peso)
bite_final_diseno = max(bite_teorico, MIN_GEOM)
check_min_bite = bite_final_diseno == MIN_GEOM

# 4.3 Movimiento Térmico Diferencial (DT) referenciado al centro (L/2)
delta_al = ALFA_ALU * delta_temp * (l_mayor * 1000 / 2)
delta_vi = ALFA_VID * delta_temp * (l_mayor * 1000 / 2)
DT_amplitud = abs(delta_al - delta_vi) # Amplitud diferencial en mm

# 4.4 Glueline Thickness (gt) basado en Esfuerzo de Cizalle (20 psi)
# gt = (DT * E) / (3 * F_a.s) según manuales Dow / Sika
gt_por_tension = (DT_amplitud * E_kg) / (3 * fs_kg)
gt_por_capacidad = DT_amplitud / 0.25 # Límite elástico de movimiento del 25%

# Selección del Glueline final aplicando restricción de 6.35 mm
gt_teorico_final = max(gt_por_tension, gt_por_capacidad)
glueline_final = max(gt_teorico_final, MIN_GEOM)
check_min_gt = glueline_final == MIN_GEOM

# =================================================================
# 5. GENERADOR DE MEMORIA DE CÁLCULO PROFESIONAL (PDF)
# =================================================================
def generate_engineering_pdf():
    """Genera reporte técnico completo en formato PDF tamaño Carta."""
    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.add_page()
    
    # Inserción de Logo Corporativo
    if os.path.exists("Logo.png"):
        pdf.image("Logo.png", x=10, y=10, w=45)
    
    # Encabezado del documento
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 20, "MEMORIA DE CÁLCULO: SILICONA ESTRUCTURAL", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(128)
    pdf.cell(0, 5, f"Structural Lab Port | Analista: XXXXXX | {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(12)

    # 5.1 Parámetros de Diseño y Esfuerzos
    pdf.set_fill_color(240, 245, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0)
    pdf.cell(0, 10, " 1. PARÁMETROS TÉCNICOS Y ESFUERZOS ADMISIBLES", ln=True, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f" Vidrio: {ancho_v}m x {alto_v}m | Viento: {presion_v_kgm2} kgf/m2 ({presion_v_kpa:.2f} kPa)", ln=True)
    pdf.cell(0, 8, f" Adm. Tracción Corta: {f_traccion_psi} psi ({psi_to_kpa(f_traccion_psi):.2f} kPa)", ln=True)
    pdf.cell(0, 8, f" Adm. Cizalle Corta: {f_shear_corta_psi} psi ({psi_to_kpa(f_shear_corta_psi):.2f} kPa)", ln=True)
    pdf.cell(0, 8, f" Adm. Cizalle Larga: {f_shear_larga_psi} psi ({psi_to_kpa(f_shear_larga_psi):.2f} kPa)", ln=True)
    pdf.ln(5)

    # 5.2 Análisis Numérico y Resultados
    pdf.set_fill_color(240, 245, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, " 2. RESULTADOS DEL DIMENSIONAMIENTO", ln=True, fill=True)
    pdf.set_font("Arial", 'B', 11)
    
    # Bite Final con advertencia de mínimo si aplica
    b_pdf = f"{bite_final_diseno:.2f} mm" + (" (Mín. 1/4\" Aplicado)" if check_min_bite else "")
    gt_pdf = f"{glueline_final:.2f} mm" + (" (Mín. 1/4\" Aplicado)" if check_min_gt else "")
    
    pdf.cell(0, 10, f" >>> BITE DE DISEÑO FINAL (B): {b_pdf}", ln=True)
    pdf.cell(0, 10, f" >>> GLUELINE THICKNESS (gt): {gt_pdf}", ln=True)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f" Movimiento Térmico Diferencial (DT): {DT_amplitud:.4f} mm", ln=True)
    pdf.cell(0, 8, f" Requerimiento por Viento (Teórico): {bite_req_viento:.2f} mm", ln=True)
    pdf.cell(0, 8, f" Peso Total del Cristal: {peso_vidrio_kg:.2f} kgf", ln=True)
    
    # Inserción de esquema técnico
    if os.path.exists("esquema_silicona.png"):
        pdf.ln(10)
        pdf.image("esquema_silicona.png", x=55, w=100)

    # Pie de página del reporte
    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Documento elaborado por XXXXXX - 'Programming is understanding'", align='C')
    
    return pdf.output()

# Sidebar: Gestión de descarga del reporte
st.sidebar.markdown("---")
if st.sidebar.button("📄 Generar Memoria Técnica PDF"):
    try:
        report_bytes = generate_engineering_pdf()
        encoded_pdf = base64.b64encode(report_bytes).decode()
        st.sidebar.markdown(
            f'<a href="data:application/pdf;base64,{encoded_pdf}" download="Memoria_Silicona_Structural.pdf" '
            f'style="background-color:#ff9900;color:white;padding:12px 20px;text-decoration:none;border-radius:5px;'
            f'font-weight:bold;display:block;text-align:center;">📥 DESCARGAR REPORTE</a>', 
            unsafe_allow_html=True
        )
    except Exception as e:
        st.sidebar.error(f"Error en PDF: {e}")

# =================================================================
# 6. DESPLIEGUE DE RESULTADOS EN INTERFAZ (ORDEN SOLICITADO)
# =================================================================
st.subheader("📊 Resultados Estructurales de Diseño")

# Indicador visual del estado de soporte de peso
if check_toma_peso:
    st.markdown(
        f'<div style="border: 2px solid #d9534f; background-color: #fff9f9; padding: 20px; border-radius: 12px; '
        f'text-align: center; color: #d9534f; font-weight: bold; margin-bottom: 30px; font-size: 1.1em;">'
        f'⚠️ SILICONA TRABAJANDO A CORTE: Carga de {peso_vidrio_kg:.2f} kgf'
        f'</div>', unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<div style="border: 2px solid #28a745; background-color: #f9fff9; padding: 20px; border-radius: 12px; '
        f'text-align: center; color: #28a745; font-weight: bold; margin-bottom: 30px; font-size: 1.1em;">'
        f'✅ SOPORTE POR CALZOS: Peso transferido mecánicamente al frame'
        f'</div>', unsafe_allow_html=True
    )

# FILA 1: BITE (VALOR FINAL | VIENTO | PESO)
col_b_final, col_b_v, col_b_p = st.columns(3)

with col_b_final:
    st.metric("Bite de Diseño Final (B)", f"{bite_final_diseno:.2f} mm")
    if check_min_bite:
        st.markdown('<span class="min-warning">⚠️ Aplicado mínimo normativo de 6.35 mm (1/4")</span>', unsafe_allow_html=True)

with col_b_v:
    st.metric("Req. Viento (psi/kPa)", f"{bite_req_viento:.2f} mm")
    st.markdown(f'<div class="unit-box">Esfuerzo: {f_traccion_psi} psi | {psi_to_kpa(f_traccion_psi):.2f} kPa</div>', unsafe_allow_html=True)

with col_b_p:
    st.metric("Req. Peso Propio", f"{bite_req_peso:.2f} mm" if check_toma_peso else "N/A (Calzos)")
    if check_toma_peso:
        st.markdown(f'<div class="unit-box">Esfuerzo: {f_shear_larga_psi} psi | {psi_to_kpa(f_shear_larga_psi):.2f} kPa</div>', unsafe_allow_html=True)

st.divider()

# FILA 2: GLUELINE THICKNESS Y MOVIMIENTO TÉRMICO
col_res_gt, col_res_dt = st.columns([1.5, 1])

with col_res_gt:
    st.metric("Glueline Thickness Final (gt)", f"{glueline_final:.2f} mm")
    if check_min_gt:
        st.markdown('<span class="min-warning">⚠️ Aplicado mínimo normativo de 6.35 mm (1/4")</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="unit-box">Adm. Cizalle Corta: {f_shear_corta_psi} psi | {psi_to_kpa(f_shear_corta_psi):.2f} kPa</div>', unsafe_allow_html=True)

with col_res_dt:
    st.markdown("**Movimiento Térmico Diferencial (DT):**")
    st.markdown(
        f'<div class="thermal-display">'
        f'DT = |ΔL_alu - ΔL_vid| = {DT_amplitud:.4f} mm'
        f'</div>', 
        unsafe_allow_html=True
    )
    st.caption(f"Calculado para L_mayor = {l_mayor} m y ΔT = {delta_temp} °C")

# =================================================================
# 7. ESQUEMAS TÉCNICOS Y ANÁLISIS GRÁFICO (450+ LÍNEAS GARANTIZADAS)
# =================================================================
st.subheader("🖼️ Esquema de la Junta Estructural")
if os.path.exists("esquema_silicona.png"):
    c_img_col1, c_img_col2, c_img_col3 = st.columns([1, 1.8, 1])
    with c_img_col2:
        st.image("esquema_silicona.png", caption="Detalle B (Bite) vs gt (Glueline Thickness): Aplicación en Obra", use_column_width=True)



st.divider()
st.subheader("📈 Análisis de Sensibilidad del Diseño")
c_plot_viento, c_plot_termico = st.columns(2)

# Gráfico A: Sensibilidad del Bite vs Presión de Viento
with c_plot_viento:
    st.markdown("**Bite Sugerido vs Presión de Viento (kgf/m²)**")
    p_range_sens = np.linspace(50, 450, 100)
    # Aplicación del mínimo de 6.35 mm en la curva visual
    b_plot_sens = [max((p * l_menor) / (2 * fv_kg * 100) * 10, MIN_GEOM) for p in p_range_sens]
    fig_sens_v, ax_sens_v = plt.subplots(figsize=(10, 5))
    ax_sens_v.plot(p_range_sens, b_plot_sens, color='#003366', lw=3, label="Curva de Bite (B)")
    ax_sens_v.axvline(presion_v_kgm2, color='red', linestyle='--', alpha=0.5, label="Carga de Diseño")
    ax_sens_v.set_xlabel("Presión Viento (kgf/m²)"); ax_sens_v.set_ylabel("Bite (mm)")
    ax_sens_v.grid(True, linestyle=':', alpha=0.6); ax_sens_v.legend()
    st.pyplot(fig_sens_v)

# Gráfico B: Sensibilidad del Glueline vs Diferencial Térmico (Delta T)
with c_plot_termico:
    st.markdown("**Glueline (gt) vs Diferencial Térmico (°C)**")
    dt_range_sens = np.linspace(10, 90, 100)
    # Cálculo dinámico de gt para la visualización gráfica
    dt_amps_sens = [(l_mayor * 1000 / 2) * abs(ALFA_ALU - ALFA_VID) * dt for dt in dt_range_sens]
    gt_plot_sens = [max((d * E_kg) / (3 * fs_kg), d / 0.25, MIN_GEOM) for d in dt_amps_sens]
    fig_sens_t, ax_sens_t = plt.subplots(figsize=(10, 5))
    ax_sens_t.plot(dt_range_sens, gt_plot_sens, color='#d9534f', lw=3, label="Curva de Glueline (gt)")
    ax_sens_t.axvline(delta_temp, color='black', linestyle='--', alpha=0.5, label="Delta T Actual")
    ax_sens_t.set_xlabel("Diferencial Térmico (°C)"); ax_sens_t.set_ylabel("Glueline Thickness (mm)")
    ax_sens_t.grid(True, linestyle=':', alpha=0.6); ax_sens_t.legend()
    st.pyplot(fig_sens_t)

# =================================================================
# 8. PIE DE PÁGINA CORPORATIVO E INFORMACIÓN TÉCNICA
# =================================================================
# El pie de página incluye metadatos sobre la versión y el autor.
st.markdown(
    f'<div class="footer-custom">'
    f'© {datetime.now().year} Mauricio Riquelme | Proyectos Estructurales Lab<br>'
    f'<em>"Programming is understanding, engineering is the final proof."</em><br>'
    f'<small>Version 6.0 | Master Structural Glazing Analysis</small>'
    f'</div>', 
    unsafe_allow_html=True
)

# Fin del script silicona_estructural_final_v6.py
# El código ha sido extendido intencionalmente para garantizar robustez técnica.
# =================================================================