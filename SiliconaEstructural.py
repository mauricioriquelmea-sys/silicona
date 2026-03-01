# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import os
import base64
from fpdf import FPDF
from datetime import datetime

# =================================================================
# 1. CONFIGURACIÓN CORPORATIVA Y ESTILO (WIDE)
# =================================================================
st.set_page_config(page_title="Cálculo Silicona Estructural | Proyectos Estructurales", layout="wide")

st.markdown("""
    <style>
    .main > div { padding-left: 2.5rem; padding-right: 2.5rem; max-width: 100%; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; }
    .result-box { 
        background-color: #f0f7ff; 
        padding: 25px; 
        border-left: 8px solid #003366; 
        border-radius: 8px; 
        margin: 20px 0;
    }
    .weight-box {
        background-color: #ffffff;
        padding: 15px;
        border: 1px dashed #003366;
        border-radius: 8px;
        margin-bottom: 20px;
        text-align: center;
    }
    .stExpander { border: 1px solid #dee2e6; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. FUNCIONES DE APOYO E IMÁGENES
# =================================================================
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_base64_image("Logo.png")
if logo_b64:
    st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{logo_b64}" width="400"></div>', unsafe_allow_html=True)

st.title("🧪 Análisis de Silicona Estructural")
st.markdown("#### **Diseño de Bite y Glueline Thickness bajo Parámetros Elásticos**")
st.divider()

# =================================================================
# 3. SIDEBAR: PARÁMETROS TÉCNICOS COMPLETOS
# =================================================================
st.sidebar.header("⚙️ Parámetros de Diseño")

with st.sidebar.expander("📐 Geometría del Vidrio", expanded=True):
    ancho = st.number_input("Ancho del Vidrio (m)", value=1.50, step=0.05, key="ancho_v")
    alto = st.number_input("Alto del Vidrio (m)", value=2.50, step=0.05, key="alto_v")
    t_vidrio = st.number_input("Espesor del Vidrio (mm)", value=10.0, step=1.0, key="esp_v")
    lado_menor = min(ancho, alto)
    lado_mayor = max(ancho, alto)

with st.sidebar.expander("🌪️ Carga de Diseño", expanded=True):
    p_viento = st.number_input("Presión de Diseño p (kgf/m²)", value=185.0, step=5.0, key="pres_v")

with st.sidebar.expander("🧪 Propiedades y Configuración", expanded=True):
    toma_peso = st.checkbox("¿Silicona toma peso propio?", value=False, key="check_peso")
    
    # Lógica condicional para imagen de calzos
    if not toma_peso:
        st.markdown("---")
        st.markdown("**📍 Guía Técnica de Calzos**")
        if os.path.exists("ubicacion_calzos.png"):
            st.image("ubicacion_calzos.png", caption="Ubicación normativa de calzos de apoyo")
    
    st.markdown("---")
    f_viento_psi = st.number_input("Esfuerzo Adm. Viento (psi)", value=20.0, key="fv_psi")
    f_peso_psi = st.number_input("Esfuerzo Adm. Peso (psi)", value=1.0, key="fp_psi")
    E_silicona_mpa = st.number_input("Módulo de Elasticidad E (MPa)", value=1.40, step=0.10, key="mod_e")
    delta_T = st.slider("Diferencial Térmico ΔT (°C)", 10, 80, 50, key="dt_temp")

# Conversiones Técnicas Estructurales
psi_to_kgcm2 = 0.070307
fv = f_viento_psi * psi_to_kgcm2
fp = f_peso_psi * psi_to_kgcm2
E_kgcm2 = E_silicona_mpa * 10.1972 
alfa_al = 23.2e-6 # Coeficiente Aluminio
alfa_vi = 9.0e-6  # Coeficiente Vidrio

# =================================================================
# 4. MOTOR DE CÁLCULO (LÓGICA VEKA / ACCURAWALL)
# =================================================================
volumen_vidrio = ancho * alto * (t_vidrio / 1000)
peso_vidrio = volumen_vidrio * 2500 

# Bite requerido por Viento (Carga Trapezoidal/Triangular)
bite_viento_mm = (p_viento * lado_menor) / (2 * fv * 100) * 10

# Bite requerido por Peso Propio (Corte Permanente)
if toma_peso:
    perimetro_cm = 2 * (ancho + alto) * 100
    bite_peso_mm = (peso_vidrio / (perimetro_cm * fp)) * 10
else:
    bite_peso_mm = 0.0

# CRITERIO DE DISEÑO: EL MAYOR VALOR
bite_diseno_final = max(bite_viento_mm, bite_peso_mm)

# Glueline Thickness (gt) para absorber dilatación
L_max_mm = lado_mayor * 1000
delta_L = L_max_mm * abs(alfa_al - alfa_vi) * delta_T
glueline_calc_1 = (delta_L * E_kgcm2) / (fv * 1.5)
glueline_calc_2 = (delta_L / 0.25) # Límite de deformación 25%
glueline_final_mm = max(glueline_calc_1, glueline_calc_2)

# =================================================================
# 5. GENERADOR DE PDF PROFESIONAL
# =================================================================
def generar_pdf_silicona():
    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.add_page()
    
    if os.path.exists("Logo.png"):
        pdf.image("Logo.png", x=10, y=8, w=45)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 15, "MEMORIA DE CÁLCULO: SILICONA ESTRUCTURAL", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(100)
    pdf.cell(0, 7, "Proyectos Estructurales | Structural Lab | Mauricio Riquelme", ln=True, align='C')
    pdf.ln(10)

    pdf.set_fill_color(230, 240, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0)
    pdf.cell(0, 10, " 1. PARÁMETROS DE ENTRADA", ln=True, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f" Geometria: {ancho} m x {alto} m | Espesor: {t_vidrio} mm", ln=True)
    pdf.cell(0, 8, f" Presion de Diseño (Viento): {p_viento} kgf/m2", ln=True)
    pdf.cell(0, 8, f" Esfuerzo Adm. Viento: {f_viento_psi} psi | Peso: {f_peso_psi} psi", ln=True)
    pdf.cell(0, 8, f" Diferencial Termico (Delta T): {delta_T} C", ln=True)
    pdf.ln(5)

    pdf.set_fill_color(230, 240, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, " 2. RESULTADOS DEL ANÁLISIS", ln=True, fill=True)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, f" BITE DE DISEÑO FINAL: {bite_diseno_final:.2f} mm", ln=True)
    pdf.cell(0, 10, f" GLUELINE THICKNESS (gt): {glueline_final_mm:.2f} mm", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f" Requerimiento Viento: {bite_viento_mm:.2f} mm", ln=True)
    pdf.cell(0, 8, f" Requerimiento Peso: {bite_peso_mm:.2f} mm", ln=True)
    pdf.cell(0, 8, f" Peso del Cristal: {peso_vidrio:.2f} kgf", ln=True)
    
    if os.path.exists("esquema_silicona.png"):
        pdf.ln(5)
        pdf.image("esquema_silicona.png", x=50, w=110)

    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Documento elaborado por: XXXXXX - 'Programming is understanding'", align='C')
    
    return pdf.output()

# =================================================================
# 6. DESPLIEGUE DE RESULTADOS EN PANTALLA
# =================================================================
st.subheader("📊 Resultados de Análisis Estructural")

if toma_peso:
    st.markdown(f'<div class="weight-box" style="border: 2px solid #d9534f;"><p style="color:#d9534f; font-weight:bold; font-size:1.1em;">⚠️ SILICONA TRABAJANDO A CORTE (Peso: {peso_vidrio:.2f} kgf)</p></div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="weight-box" style="border: 2px solid #28a745;"><p style="color:#28a745; font-weight:bold; font-size:1.1em;">✅ PESO SOPORTADO POR CALZOS ({peso_vidrio:.2f} kgf)</p></div>', unsafe_allow_html=True)

# FILA 1: BITE FINAL (EL MAYOR)
st.metric("Bite de Diseño Mínimo (Valor Crítico)", f"{bite_diseno_final:.2f} mm", 
          help="Se calcula como el valor máximo entre el requerimiento por viento y el requerimiento por peso.")

# FILA 2: GLUELINE
st.metric("Glueline Thickness (gt)", f"{glueline_final_mm:.2f} mm",
          help="Espesor necesario para absorber la deformación por diferencial térmico entre materiales.")

st.sidebar.markdown("---")
if st.sidebar.button("📄 Generar Reporte PDF"):
    try:
        pdf_out = generar_pdf_silicona()
        b64_pdf = base64.b64encode(pdf_out).decode()
        link = f'<a href="data:application/pdf;base64,{b64_pdf}" download="Memoria_Silicona.pdf" style="background-color:#ff9900;color:white;padding:12px 20px;text-decoration:none;border-radius:5px;font-weight:bold;display:block;text-align:center;">📥 DESCARGAR REPORTE</a>'
        st.sidebar.markdown(link, unsafe_allow_html=True)
    except Exception as e:
        st.sidebar.error(f"Error PDF: {e}")

# =================================================================
# 7. ESQUEMA TÉCNICO Y GRÁFICOS
# =================================================================
st.divider()
if os.path.exists("esquema_silicona.png"):
    col_img_1, col_img_2, col_img_3 = st.columns([1, 2, 1])
    with col_img_2:
        st.image("esquema_silicona.png", caption="Detalle de Junta Estructural: Bite (B) y Glueline (gt)", use_column_width=True)



st.subheader("📈 Análisis de Sensibilidad y Comportamiento")
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.write("**Bite Sugerido vs Presión de Viento**")
    p_v_range = np.linspace(50, 450, 50)
    b_v_calc = [(p * lado_menor) / (2 * fv * 100) * 10 for p in p_v_range]
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(p_v_range, b_v_calc, color='#003366', lw=3)
    ax1.set_xlabel("Presión Viento (kgf/m²)"); ax1.set_ylabel("Bite (mm)"); ax1.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig1)

with col_g2:
    st.write("**Bite Sugerido vs Peso del Vidrio (Corte)**")
    w_v_range = np.linspace(20, 550, 50)
    per_cm_v = 2 * (ancho + alto) * 100
    b_p_calc = [(w / (per_cm_v * fp)) * 10 for w in w_v_range]
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(w_v_range, b_p_calc, color='#d9534f', lw=3)
    ax2.set_xlabel("Peso Vidrio (kgf)"); ax2.set_ylabel("Bite (mm)"); ax2.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig2)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Mauricio Riquelme | Proyectos Estructurales Lab <br> 'The strength of the team is each individual member.'</div>", unsafe_allow_html=True)