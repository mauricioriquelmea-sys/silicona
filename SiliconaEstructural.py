# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
import math

# 1. CONFIGURACIÓN CORPORATIVA
st.set_page_config(page_title="Cálculo Silicone Bite | Proyectos Estructurales", layout="wide")

st.markdown("""
    <style>
    .main > div { padding-left: 2rem; padding-right: 2rem; max-width: 100%; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; }
    .result-box { background-color: #eef6ff; padding: 20px; border-left: 5px solid #007BFF; border-radius: 5px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧮 Cálculo de Bite de Silicona Estructural")
st.subheader("Diseño según ASTM C1184 y Criterios ETAG 002")
st.caption("Cálculo de Mordida por Viento, Peso Propio y Espesor de Junta (Glueline)")

# 2. SIDEBAR - PARÁMETROS DE DISEÑO
st.sidebar.header("📐 Geometría del Panel")
W = st.sidebar.number_input("Ancho del vidrio (m)", value=1.5, step=0.1)
H = st.sidebar.number_input("Alto del vidrio (m)", value=2.5, step=0.1)
t_glass = st.sidebar.number_input("Espesor del vidrio (mm)", value=10.0, step=1.0)
dens_glass = 2500 # kg/m3

st.sidebar.header("🌪️ Cargas de Diseño")
p_wind = st.sidebar.number_input("Presión de viento diseño (kgf/m²)", value=150.0, step=10.0)

st.sidebar.header("🧪 Propiedades de la Silicona")
f_viento = st.sidebar.number_input("Esfuerzo admisible Viento (psi)", value=20.0, help="Típico: 20 psi (0.14 MPa)")
f_peso = st.sidebar.number_input("Esfuerzo admisible Peso Propio (psi)", value=1.0, help="Típico: 1 psi (0.007 MPa)")

# Conversión de unidades (psi a kgf/cm2)
psi_to_kgcm2 = 0.070307
fv = f_viento * psi_to_kgcm2
fp = f_peso * psi_to_kgcm2

with st.sidebar.expander("🌡️ Parámetros Térmicos (Glueline Thickness)"):
    L_max = max(W, H)
    delta_T = st.number_input("Diferencial de Temp. (°C)", value=50)
    alpha_glass = 0.000009 # m/m°C
    alpha_alum = 0.000023  # m/m°C
    strain_limit = st.slider("Límite de deformación silicona (%)", 12, 25, 12) / 100

# 3. MOTOR DE CÁLCULO
# A. BITE POR CARGA DE VIENTO (Bv)
# Fórmula: Bite = (Presión * Lado Menor) / (2 * Esfuerzo Admisible)
bite_viento = (p_wind * min(W, H)) / (2 * fv * 100) # cm
bite_viento_mm = bite_viento * 10

# B. BITE POR PESO PROPIO (Bp) - Solo si la silicona soporta el peso
peso_vidrio = W * H * (t_glass / 1000) * dens_glass # kg
perimetro = 2 * (W + H) * 100 # cm
bite_peso = peso_vidrio / (perimetro * fp) # cm
bite_peso_mm = bite_peso * 10

# C. GLUELINE THICKNESS (t)
# Basado en el movimiento térmico diferencial entre vidrio y aluminio
delta_L = L_max * abs(alpha_alum - alpha_glass) * delta_T * 1000 # mm
glueline_thickness = delta_L / strain_limit # mm

# 4. DESPLIEGUE DE RESULTADOS
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Bite por Viento", f"{bite_viento_mm:.2f} mm")
    st.caption("Determinado por la succión crítica del viento.")

with col2:
    st.metric("Bite por Peso Propio", f"{bite_peso_mm:.2f} mm")
    st.caption("Solo aplica si no hay calzos de apoyo (setting blocks).")

with col3:
    st.metric("Glueline Thickness", f"{glueline_thickness:.2f} mm")
    st.caption("Espesor mínimo para absorber dilatación térmica.")

# 5. RESUMEN TÉCNICO Y NOTAS
st.markdown("---")
bite_final = math.ceil(max(bite_viento_mm, bite_peso_mm))
if bite_final < 6: bite_final = 6 # Mínimo constructivo recomendado

st.markdown(f"""
<div class="result-box">
    <h3>Recomendación de Diseño:</h3>
    <ul>
        <li><strong>Structural Bite Mínimo:</strong> {bite_final} mm</li>
        <li><strong>Glueline Thickness Sugerido:</strong> {math.ceil(glueline_thickness)} mm</li>
    </ul>
    <p><em>Nota: El Bite nunca debe ser menor al espesor de la junta (Glueline) ni menor a 6 mm por razones constructivas.</em></p>
</div>
""", unsafe_allow_html=True)

# 6. GRÁFICO DE SENSIBILIDAD
st.subheader("📈 Sensibilidad del Bite vs Presión de Viento")
presiones = np.linspace(50, 300, 20)
bites = [(p * min(W, H)) / (2 * fv * 100) * 10 for p in presiones]

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(presiones, bites, color='blue', lw=2, label='Bite requerido')
ax.axhline(6, color='red', ls='--', label='Mínimo constructivo (6mm)')
ax.set_xlabel("Presión de Viento (kgf/m²)")
ax.set_ylabel("Bite (mm)")
ax.grid(True, alpha=0.3)
ax.legend()
st.pyplot(fig)

# 7. CRÉDITOS
st.markdown("---")
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; color: #555; font-size: 0.9em;">
        <div><strong>Desarrollado por:</strong> Mauricio Riquelme, Ingeniero Civil Estructural</div>
        <div style="text-align: right;"><strong>Contacto:</strong> mriquelme@proyectosestructurales.com</div>
    </div>
    <div style="text-align: center; margin-top: 30px;">
        <p style="font-family: 'Georgia', serif; font-size: 1.2em; color: #003366; font-style: italic;">
            "Programming is understanding"
        </p>
    </div>
""", unsafe_allow_html=True)