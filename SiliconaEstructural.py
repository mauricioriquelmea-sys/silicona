# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import os
import base64

# =================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO CORPORATIVO
# =================================================================
st.set_page_config(page_title="Cálculo Silicona Estructural | Mauricio Riquelme", layout="wide")

st.markdown("""
    <style>
    .main > div { padding-left: 3rem; padding-right: 3rem; }
    .stMetric { background-color: #f8f9fa; padding: 20px; border-radius: 12px; border: 1px solid #dee2e6; }
    .result-box { 
        background-color: #f0f7ff; 
        padding: 25px; 
        border-left: 8px solid #0056b3; 
        border-radius: 8px; 
        margin: 20px 0;
    }
    .formula-box {
        background-color: #fdfdfe;
        padding: 15px;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. ENCABEZADO Y LOGOS
# =================================================================
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    return None

logo_b64 = get_base64_image("Logo.png")
if logo_b64:
    st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{logo_b64}" width="400"></div>', unsafe_allow_html=True)

st.title("🧪 Análisis de Silicona Estructural")
st.markdown("#### **Diseño según ASTM C1184 y Estándares de Fachada Glazing**")
st.divider()

# =================================================================
# 3. SIDEBAR: PARÁMETROS TÉCNICOS
# =================================================================
st.sidebar.header("⚙️ Parámetros de Diseño")

# --- GEOMETRÍA DEL PANEL ---
with st.sidebar.expander("📐 Geometría del Vidrio", expanded=True):
    ancho = st.number_input("Ancho del Vidrio (m)", value=1.50, min_value=0.1, step=0.05)
    alto = st.number_input("Alto del Vidrio (m)", value=2.50, min_value=0.1, step=0.05)
    t_vidrio = st.number_input("Espesor del Vidrio (mm)", value=10.0, min_value=3.0, step=1.0)
    # Área tributaria para el lado menor
    lado_menor = min(ancho, alto)

# --- CARGAS ---
with st.sidebar.expander("🌪️ Cargas de Diseño", expanded=True):
    p_viento = st.number_input("Presión de Viento (kgf/m²)", value=185.0, min_value=10.0, step=5.0)

# --- PROPIEDADES SILICONA ---
with st.sidebar.expander("🧪 Propiedades de la Silicona"):
    f_viento_psi = st.number_input("Esfuerzo Adm. Viento (psi)", value=20.0, help="ASTM C1184: Típico 20 psi")
    f_peso_psi = st.number_input("Esfuerzo Adm. Peso (psi)", value=1.0, help="ASTM C1184: Típico 1 psi")
    strain_limit = st.slider("Límite de Deformación (%)", 10, 25, 12) / 100

# Conversiones
psi_to_kgcm2 = 0.070307
fv = f_viento_psi * psi_to_kgcm2
fp = f_peso_psi * psi_to_kgcm2

# =================================================================
# 4. MOTOR DE CÁLCULO
# =================================================================

# A. BITE POR VIENTO (Bv)
# Fórmula: Bite = (Presión * Lado Menor) / (2 * Esfuerzo Admisible)
bite_viento_mm = (p_viento * lado_menor) / (2 * fv * 100) * 10

# B. BITE POR PESO PROPIO (Bp)
# Solo si no existen calzos de apoyo (Setting Blocks)
peso_total = ancho * alto * (t_vidrio / 1000) * 2500 # kg
perimetro_cm = 2 * (ancho + alto) * 100
bite_peso_mm = (peso_total / (perimetro_cm * fp)) * 10

# C. GLUELINE THICKNESS (gt)
# Basado en dilatación diferencial Alum vs Vidrio (Delta T = 50°C)
L_max_mm = max(ancho, alto) * 1000
mov_termico = L_max_mm * abs(23.2e-6 - 9.0e-6) * 50 # mm
glueline_mm = mov_termico / strain_limit

# =================================================================
# 5. RESULTADOS TÉCNICOS
# =================================================================
st.subheader("📊 Resultados de Análisis Estructural")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Bite (Viento)", f"{bite_viento_mm:.2f} mm")
with c2:
    st.metric("Bite (Peso Propio)", f"{bite_peso_mm:.2f} mm")
with c3:
    st.metric("Glueline (Espesor)", f"{glueline_mm:.2f} mm")

# --- FICHA DE ESPECIFICACIÓN ---
bite_final = max(math.ceil(bite_viento_mm), math.ceil(bite_peso_mm), 6) # Mínimo constructivo 6mm
gt_final = max(math.ceil(glueline_mm), 6)



st.markdown(f"""
<div class="result-box">
    <h3>✅ Especificación Técnica Recomendada:</h3>
    <p style="font-size: 1.2em;">
        <strong>Structural Bite Mínimo:</strong> <span style="color: #d9534f;">{bite_final} mm</span><br>
        <strong>Glueline Thickness (gt):</strong> <span style="color: #0056b3;">{gt_final} mm</span>
    </p>
    <hr>
    <small>
        <strong>Nota Normativa:</strong> El Bite estructural no debe ser inferior al espesor de la junta (Glueline) 
        ni menor a 6 mm para permitir una correcta aplicación de la silicona en fábrica (Shop Glazing).
    </small>
</div>
""", unsafe_allow_html=True)

# =================================================================
# 6. GRÁFICO DE COMPORTAMIENTO Y SENSIBILIDAD
# =================================================================
st.subheader("📈 Sensibilidad: Mordida vs Presión de Viento")

p_rango = np.linspace(50, 350, 30)
b_rango = [(p * lado_menor) / (2 * fv * 100) * 10 for p in p_rango]

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(p_rango, b_rango, color='#0056b3', label='Bite requerido (Viento)', lw=2)
ax.axhline(6, color='red', ls='--', label='Mínimo constructivo (6mm)')
ax.set_xlabel("Presión de Diseño (kgf/m²)")
ax.set_ylabel("Bite Mínimo (mm)")
ax.grid(True, which="both", alpha=0.3)
ax.legend()

st.pyplot(fig)

# =================================================================
# 7. CRÉDITOS FINALES
# =================================================================
st.markdown("---")
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; color: #444; font-size: 0.9em;">
        <div>
            <strong>Ingeniero Responsable:</strong> Mauricio Riquelme <br>
            <em>Proyectos Estructurales EIRL</em>
        </div>
        <div style="text-align: right;">
            <strong>Contacto:</strong> <a href="mailto:mriquelme@proyectosestructurales.com">mriquelme@proyectosestructurales.com</a>
        </div>
    </div>
    <div style="text-align: center; margin-top: 40px; margin-bottom: 20px;">
        <p style="font-family: 'Georgia', serif; font-size: 1.4em; color: #003366; font-style: italic; letter-spacing: 1px;">
            "Programming is understanding"
        </p>
    </div>
    """, unsafe_allow_html=True)