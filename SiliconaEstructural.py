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
st.markdown("#### **Diseño de Bite y Glueline bajo Parámetros Elásticos**")
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

with st.sidebar.expander("🧪 Propiedades de la Silicona", expanded=True):
    f_viento_psi = st.number_input("Esfuerzo Adm. Viento (psi)", value=20.0)
    f_peso_psi = st.number_input("Esfuerzo Adm. Peso (psi)", value=1.0)
    # Nuevo parámetro: Módulo de Elasticidad (E)
    E_silicona_mpa = st.number_input("Módulo de Elasticidad E (MPa)", value=2.10, step=0.10)
    delta_T = st.slider("Diferencial Térmico ΔT (°C)", 10, 80, 50)

# Conversiones Técnicas
psi_to_kgcm2 = 0.070307
fv = f_viento_psi * psi_to_kgcm2
fp = f_peso_psi * psi_to_kgcm2
E_kgcm2 = E_silicona_mpa * 10.1972 # MPa a kgf/cm²

# =================================================================
# 4. MOTOR DE CÁLCULO (MECÁNICA DE MATERIALES)
# =================================================================

# 1. Masa del Vidrio
volumen_vidrio = ancho * alto * (t_vidrio / 1000)  # m³
densidad_vidrio = 2500  # kg/m³
peso_vidrio = volumen_vidrio * densidad_vidrio  # kgf

# 2. Bite por Viento (Bv)
bite_viento_mm = (p_viento * lado_menor) / (2 * fv * 100) * 10

# 3. Bite por Peso Propio (Bp)
perimetro_cm = 2 * (ancho + alto) * 100
bite_peso_mm = (peso_vidrio / (perimetro_cm * fp)) * 10

# 4. Glueline Thickness (gt) basado en Módulo E
# Delta L térmico (Coef. expansión térmica diferencial entre Vidrio y Aluminio)
L_max_mm = max(ancho, alto) * 1000
alfa_al = 23.2e-6
alfa_vi = 9.0e-6
delta_L = L_max_mm * abs(alfa_al - alfa_vi) * delta_T

# Glueline considerando el módulo de elasticidad considerado para absorber delta_L
# Bajo el criterio de esfuerzo cortante admisible derivado de E
glueline_mm = (delta_L * E_kgcm2) / (fv * 1.5) # Factor de seguridad sobre la rigidez
glueline_mm = max(glueline_mm, (delta_L / 0.25)) # Check de seguridad de no exceder deformación técnica

# =================================================================
# 5. DESPLIEGUE DE RESULTADOS
# =================================================================
st.subheader("📊 Resultados de Análisis Estructural")

st.markdown(f"""
<div class="weight-box">
    <p style="margin:5px 0; color:#555;">Peso Total Calculado</p>
    <p style="font-size: 1.5em; margin:0; color:#003366; font-weight:bold;">{peso_vidrio:.2f} kgf</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Bite (Viento)", f"{bite_viento_mm:.2f} mm")
with c2:
    st.metric("Bite (Peso)", f"{bite_peso_mm:.2f} mm")
with c3:
    st.metric("Glueline (E={E_silicona_mpa} MPa)", f"{glueline_mm:.2f} mm")

# --- ESPECIFICACIÓN TÉCNICA FINAL ---
bite_final = max(math.ceil(bite_viento_mm), math.ceil(bite_peso_mm), 6)
gt_final = max(math.ceil(glueline_mm), 6)



st.markdown(f"""
<div class="result-box">
    <h3>✅ Especificación Final de Carpintería:</h3>
    <p style="font-size: 1.3em; margin-bottom:10px;">
        <strong>Bite Estructural Mínimo:</strong> <span style="color: #d9534f;">{bite_final} mm</span><br>
        <strong>Espesor de Junta (Glueline):</strong> <span style="color: #003366;">{gt_final} mm</span>
    </p>
    <hr>
    <strong>Notas del Ingeniero:</strong>
    <ul>
        <li>Cálculo de Glueline optimizado según <strong>Módulo de Elasticidad de {E_silicona_mpa} MPa</strong>.</li>
        <li>Diferencial térmico considerado: {delta_T}°C.</li>
        <li>El diseño garantiza la transferencia de cargas sin exceder el esfuerzo admisible de {f_viento_psi} psi.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# =================================================================
# 6. GRÁFICO DE SENSIBILIDAD
# =================================================================
st.subheader("📈 Comportamiento del Diseño")
p_rango = np.linspace(50, 450, 50)
b_viento_rango = [(p * lado_menor) / (2 * fv * 100) * 10 for p in p_rango]

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(p_rango, b_viento_rango, color='#003366', lw=2.5, label='Bite (Viento)')
ax.axhline(bite_peso_mm, color='#d9534f', ls='--', label='Bite (Peso)')
ax.axhline(glueline_mm, color='#5cb85c', ls=':', label='Glueline Thickness')
ax.axhline(6, color='#333', lw=1, ls='-.', label='Mínimo Constructivo')
ax.fill_between(p_rango, [max(v, bite_peso_mm, glueline_mm, 6) for v in b_viento_rango], color='#003366', alpha=0.05)
ax.set_xlabel("Presión de Diseño (kgf/m²)")
ax.set_ylabel("Dimensión (mm)")
ax.legend()
st.pyplot(fig)

# =================================================================
# 7. CIERRE CORPORATIVO
# =================================================================
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; color: #666;">
        <strong>{ancho}m x {alto}m | {t_vidrio}mm | Proyectos Estructurales Lab</strong><br>
        <span style="font-style: italic; font-size: 1.2em; color: #003366;">"Programming is understanding"</span>
    </div>
    """, unsafe_allow_html=True)