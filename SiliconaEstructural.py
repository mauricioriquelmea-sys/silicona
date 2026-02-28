# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import os
import base64

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
        border-left: 8px solid #0056b3; 
        border-radius: 8px; 
        margin: 20px 0;
    }
    .info-tag {
        font-size: 0.85em;
        color: #555;
        background-color: #e9ecef;
        padding: 5px 10px;
        border-radius: 4px;
        margin-top: 5px;
    }
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
st.markdown("#### **Diseño de Bite y Glueline según ASTM C1184**")
st.divider()

# =================================================================
# 3. SIDEBAR: PARÁMETROS TÉCNICOS RIGUROSOS
# =================================================================
st.sidebar.header("⚙️ Parámetros de Diseño")

# --- GEOMETRÍA DEL PANEL ---
with st.sidebar.expander("📐 Geometría del Vidrio", expanded=True):
    ancho = st.number_input("Ancho del Vidrio (m)", value=1.50, step=0.05)
    alto = st.number_input("Alto del Vidrio (m)", value=2.50, step=0.05)
    t_vidrio = st.number_input("Espesor del Vidrio (mm)", value=10.0, step=1.0)
    lado_menor = min(ancho, alto)

# --- CARGAS DE VIENTO ---
with st.sidebar.expander("🌪️ Carga de Viento de Diseño", expanded=True):
    p_viento = st.number_input("Presión de Diseño p (kgf/m²)", value=185.0, step=5.0)
    st.markdown('<div class="info-tag">Basado en NCh 432:2025</div>', unsafe_allow_html=True)

# --- PROPIEDADES DE LA SILICONA ---
with st.sidebar.expander("🧪 Propiedades de la Silicona"):
    f_viento_psi = st.number_input("Esfuerzo Adm. Viento (psi)", value=20.0)
    f_peso_psi = st.number_input("Esfuerzo Adm. Peso (psi)", value=1.0)
    st.markdown('<div class="info-tag">Típicos ASTM C1184</div>', unsafe_allow_html=True)
    
    delta_T = st.slider("Diferencial Térmico ΔT (°C)", 10, 80, 50)
    strain_limit = st.slider("Límite de Deformación (%)", 10, 25, 12) / 100

# Conversión de unidades (psi a kgf/cm2)
psi_to_kgcm2 = 0.070307
fv = f_viento_psi * psi_to_kgcm2
fp = f_peso_psi * psi_to_kgcm2

# =================================================================
# 4. MOTOR DE CÁLCULO
# =================================================================

# A. BITE POR CARGA DE VIENTO (Bv)
# Fórmula estándar de la industria (ASTM C1401)
bite_viento_mm = (p_viento * lado_menor) / (2 * fv * 100) * 10

# B. BITE POR PESO PROPIO (Bp)
# Aplicable solo si la silicona soporta el peso sin calzos permanentes
peso_total = ancho * alto * (t_vidrio / 1000) * 2500  # kg (Densidad vidrio = 2500 kg/m3)
perimetro_cm = 2 * (ancho + alto) * 100
bite_peso_mm = (peso_total / (perimetro_cm * fp)) * 10

# C. GLUELINE THICKNESS (gt)
# Dilatación diferencial entre Aluminio (23.2e-6) y Vidrio (9.0e-6)
L_max_mm = max(ancho, alto) * 1000
mov_termico = L_max_mm * abs(23.2e-6 - 9.0e-6) * delta_T
glueline_mm = mov_termico / strain_limit

# =================================================================
# 5. DESPLIEGUE DE RESULTADOS
# =================================================================
st.subheader("📊 Resultados de Análisis Estructural")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Bite (Viento)", f"{bite_viento_mm:.2f} mm")
with c2:
    st.metric("Bite (Peso Propio)", f"{bite_peso_mm:.2f} mm")
with c3:
    st.metric("Glueline Thickness", f"{glueline_mm:.2f} mm")

# --- FICHA DE ESPECIFICACIÓN FINAL ---
bite_final = max(math.ceil(bite_viento_mm), math.ceil(bite_peso_mm), 6) # Mínimo constructivo 6mm
gt_final = max(math.ceil(glueline_mm), 6)



st.markdown(f"""
<div class="result-box">
    <h3>✅ Especificación de Diseño:</h3>
    <p style="font-size: 1.25em;">
        <strong>Structural Bite Mínimo:</strong> <span style="color: #d9534f;">{bite_final} mm</span><br>
        <strong>Glueline Thickness (gt):</strong> <span style="color: #0056b3;">{gt_final} mm</span>
    </p>
    <hr>
    <strong>Notas de Diseño:</strong>
    <ul>
        <li>El Bite estructural se rige por la succión de viento como carga crítica.</li>
        <li>Se asume el uso de siliconas bicomponentes de alto desempeño (tipo Dow 983 o similar).</li>
        <li>El espesor de junta (Glueline) es vital para absorber los movimientos diferenciales sin fatigar la adhesión.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# =================================================================
# 6. GRÁFICO DE SENSIBILIDAD
# =================================================================
st.subheader("📈 Sensibilidad de la Bite vs Carga de Viento")

p_rango = np.linspace(50, 400, 30)
b_rango = [(p * lado_menor) / (2 * fv * 100) * 10 for p in p_rango]

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(p_rango, b_rango, color='#0056b3', lw=2.5, label='Bite requerido')
ax.axhline(6, color='red', ls='--', label='Mínimo constructivo (6mm)')
ax.fill_between(p_rango, b_rango, 6, where=(np.array(b_rango) > 6), color='#0056b3', alpha=0.1)

ax.set_xlabel("Presión de Diseño (kgf/m²)", fontsize=10)
ax.set_ylabel("Bite Mínimo (mm)", fontsize=10)
ax.grid(True, which="both", alpha=0.3, ls='--')
ax.legend()
st.pyplot(fig)

# =================================================================
# 7. CRÉDITOS Y CIERRE
# =================================================================
st.markdown("---")
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; color: #444; font-size: 0.9em;">
        <div>
            <strong>Ingeniero Responsable:</strong> Mauricio Riquelme <br>
            <em>Proyectos Estructurales EIRL | PUC</em>
        </div>
        <div style="text-align: right;">
            <strong>Contacto:</strong> <a href="mailto:mriquelme@proyectosestructurales.com">mriquelme@proyectosestructurales.com</a>
        </div>
    </div>
    <div style="text-align: center; margin-top: 50px; margin-bottom: 20px;">
        <p style="font-family: 'Georgia', serif; font-size: 1.4em; color: #003366; font-style: italic; letter-spacing: 1px;">
            "Programming is understanding"
        </p>
    </div>
    """, unsafe_allow_html=True)