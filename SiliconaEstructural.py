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
# 2. ENCABEZADO Y LOGOS
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
# 3. SIDEBAR: PARÁMETROS TÉCNICOS
# =================================================================
st.sidebar.header("⚙️ Parámetros de Diseño")

with st.sidebar.expander("📐 Geometría del Vidrio", expanded=True):
    ancho = st.number_input("Ancho del Vidrio (m)", value=1.50, step=0.05)
    alto = st.number_input("Alto del Vidrio (m)", value=2.50, step=0.05)
    t_vidrio = st.number_input("Espesor del Vidrio (mm)", value=10.0, step=1.0)
    lado_menor = min(ancho, alto)

with st.sidebar.expander("🌪️ Carga de Diseño", expanded=True):
    p_viento = st.number_input("Presión de Diseño p (kgf/m²)", value=185.0, step=5.0)

with st.sidebar.expander("🧪 Propiedades y Configuración", expanded=True):
    toma_peso = st.checkbox("¿Silicona toma peso propio?", value=False)
    
    # NUEVO: Guía de Calzos integrada
    st.markdown("---")
    st.markdown("**📍 Guía Técnica de Calzos**")
    if os.path.exists("ubicacion_calzos.png"):
        st.image("ubicacion_calzos.png", caption="Ubicación normativa de calzos de apoyo")
    else:
        st.caption("Subir 'ubicacion_calzos.png' para visualizar guía.")
    
    f_viento_psi = st.number_input("Esfuerzo Adm. Viento (psi)", value=20.0)
    f_peso_psi = st.number_input("Esfuerzo Adm. Peso (psi)", value=1.0)
    E_silicona_mpa = st.number_input("Módulo de Elasticidad E (MPa)", value=1.40, step=0.10)
    delta_T = st.slider("Diferencial Térmico ΔT (°C)", 10, 80, 50)

# Conversiones Técnicas
psi_to_kgcm2 = 0.070307
fv = f_viento_psi * psi_to_kgcm2
fp = f_peso_psi * psi_to_kgcm2
E_kgcm2 = E_silicona_mpa * 10.1972 

# =================================================================
# 4. MOTOR DE CÁLCULO
# =================================================================
volumen_vidrio = ancho * alto * (t_vidrio / 1000)
peso_vidrio = volumen_vidrio * 2500 

# Bite por Viento
bite_viento_mm = (p_viento * lado_menor) / (2 * fv * 100) * 10

# Bite por Peso
if toma_peso:
    perimetro_cm = 2 * (ancho + alto) * 100
    bite_peso_mm = (peso_vidrio / (perimetro_cm * fp)) * 10
else:
    bite_peso_mm = 0.0

# Glueline Thickness
L_max_mm = max(ancho, alto) * 1000
alfa_al, alfa_vi = 23.2e-6, 9.0e-6
delta_L = L_max_mm * abs(alfa_al - alfa_vi) * delta_T
glueline_mm = max((delta_L * E_kgcm2) / (fv * 1.5), (delta_L / 0.25))

# =================================================================
# 5. GENERADOR DE PDF PROFESIONAL
# =================================================================
def generar_pdf_silicona():
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("Logo.png"):
        pdf.image("Logo.png", x=10, y=8, w=33)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Memoria de Calculo: Silicona Estructural", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 7, "Proyectos Estructurales | Structural Lab", ln=True, align='C')
    pdf.ln(15)

    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, " 1. PARAMETROS DE DISENO", ln=True, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f" Vidrio: {ancho}m x {alto}m | Espesor: {t_vidrio}mm", ln=True)
    pdf.cell(0, 8, f" Presion de Viento: {p_viento} kgf/m2 | Diferencial Termico: {delta_T} C", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, " 2. RESULTADOS ESTRUCTURALES", ln=True, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f" Bite Sugerido (Viento): {bite_viento_mm:.2f} mm", ln=True)
    pdf.cell(0, 8, f" Bite Sugerido (Peso): {bite_peso_mm:.2f} mm" if toma_peso else " Bite Sugerido (Peso): N/A (Soportado por Calzos)", ln=True)
    pdf.cell(0, 8, f" Glueline Thickness (gt): {glueline_mm:.2f} mm", ln=True)
    pdf.cell(0, 8, f" Peso Total Vidrio: {peso_vidrio:.2f} kgf", ln=True)
    
    if os.path.exists("ubicacion_calzos.png") and not toma_peso:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, " 3. ESQUEMA DE APOYO", ln=True, fill=True)
        pdf.image("ubicacion_calzos.png", w=100)

    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Documento elaborado por: XXXXXX", align='C')
    return pdf.output()

st.sidebar.markdown("---")
if st.sidebar.button("📄 Preparar Reporte PDF"):
    try:
        pdf_bytes = generar_pdf_silicona()
        b64 = base64.b64encode(pdf_bytes).decode()
        btn_html = f'''
            <div style="text-align: center; margin-top: 10px;">
                <a href="data:application/pdf;base64,{b64}" download="Memoria_Silicona_{datetime.now().strftime('%Y%m%d')}.pdf" 
                   style="background-color: #ff9900; color: white; padding: 12px 20px; text-decoration: none; 
                   border-radius: 5px; font-weight: bold; display: block;">
                    📥 DESCARGAR REPORTE
                </a>
            </div>
        '''
        st.sidebar.markdown(btn_html, unsafe_allow_html=True)
        st.sidebar.info("Reporte listo para descarga.")
    except Exception as e:
        st.sidebar.error(f"Error técnico: {e}")

# =================================================================
# 6. DESPLIEGUE DE RESULTADOS EN PANTALLA
# =================================================================
st.subheader("📊 Resultados de Análisis Estructural")

if toma_peso:
    st.markdown(f'<div class="weight-box"><p style="color:#d9534f; font-weight:bold;">⚠️ Silicona CARGADA con peso ({peso_vidrio:.2f} kgf)</p></div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="weight-box" style="border-color:#28a745;"><p style="color:#28a745; font-weight:bold;">✅ Peso ({peso_vidrio:.2f} kgf) en CALZOS</p></div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1: st.metric("Bite (Viento)", f"{bite_viento_mm:.2f} mm")
with c2: st.metric("Bite (Peso)", f"{bite_peso_mm:.2f} mm" if toma_peso else "N/A (Calzos)")
with c3: st.metric("Glueline Thickness", f"{glueline_mm:.2f} mm")

# =================================================================
# 7. GRÁFICOS DE SENSIBILIDAD
# =================================================================
st.subheader("📈 Análisis de Comportamiento")
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.write("**Bite Sugerido vs Presión de Viento**")
    p_rango = np.linspace(50, 450, 50)
    b_v_rango = [(p * lado_menor) / (2 * fv * 100) * 10 for p in p_rango]
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(p_rango, b_v_rango, color='#003366', lw=2)
    ax1.set_xlabel("Presión Viento (kgf/m²)"); ax1.set_ylabel("Bite (mm)"); ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

with col_g2:
    st.write("**Bite Sugerido vs Peso del Vidrio (Sin Calzos)**")
    p_vidrio_rango = np.linspace(20, 500, 50) # Rango de 20 a 500 kg
    per_cm_fijo = 2 * (ancho + alto) * 100
    b_p_rango = [(p / (per_cm_fijo * fp)) * 10 for p in p_vidrio_rango]
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(p_vidrio_rango, b_p_rango, color='#d9534f', lw=2)
    ax2.set_xlabel("Peso Vidrio (kgf)"); ax2.set_ylabel("Bite (mm)"); ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Proyectos Estructurales Lab | Mauricio Riquelme | 'Programming is understanding'</div>", unsafe_allow_html=True)