# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO
st.set_page_config(page_title="Cálculo Silicone Bite | Mauricio Riquelme", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stMetric { background-color: #f0f2f6; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .result-box { background-color: #e1f5fe; padding: 25px; border-left: 6px solid #01579b; border-radius: 8px; margin: 20px 0; }
    h1 { color: #01579b; }
    h3 { color: #0277bd; }
    </style>
    """, unsafe_allow_html=True)

# 2. ENCABEZADO
st.title("🧪 Cálculo de Silicona Estructural")
st.markdown("### Determinación de Bite y Glueline Thickness (ASTM C1184)")
st.divider()

# 3. ENTRADA DE DATOS (SIDEBAR)
st.sidebar.header("📐 Parámetros del Panel")
ancho = st.sidebar.number_input("Ancho del Vidrio (m)", value=1.50, min_value=0.1, step=0.05)
alto = st.sidebar.number_input("Alto del Vidrio (m)", value=2.50, min_value=0.1, step=0.05)
espesor_vidrio = st.sidebar.number_input("Espesor del Vidrio (mm)", value=10.0, min_value=4.0, step=1.0)

st.sidebar.header("🌪️ Carga de Viento")
p_viento = st.sidebar.number_input("Presión de Diseño (kgf/m²)", value=180.0, min_value=10.0, step=10.0)

st.sidebar.header("🧪 Propiedades Silicona")
f_viento_psi = st.sidebar.number_input("Esfuerzo Admisible Viento (psi)", value=20.0, help="Estándar ASTM: 20 psi")
f_peso_psi = st.sidebar.number_input("Esfuerzo Admisible Peso (psi)", value=1.0, help="Estándar ASTM: 1 psi")

# Conversión a kgf/cm²
psi_to_kgcm2 = 0.070307
fv = f_viento_psi * psi_to_kgcm2
fp = f_peso_psi * psi_to_kgcm2

# 4. CÁLCULOS TÉCNICOS
# A. Bite por Viento (Bv)
lado_menor = min(ancho, alto)
bite_viento_cm = (p_viento * lado_menor) / (2 * fv * 100)
bite_v_mm = bite_viento_cm * 10

# B. Bite por Peso Propio (Bp)
peso_vidrio = ancho * alto * (espesor_vidrio / 1000) * 2500 # kg
perimetro_cm = 2 * (ancho + alto) * 100
bite_peso_cm = peso_vidrio / (perimetro_cm * fp)
bite_p_mm = bite_peso_cm * 10

# C. Glueline Thickness (gt) - Dilatación Térmica
dt = 50 # Diferencial térmico estándar (°C)
alfa_al = 23.2e-6 # Aluminio
alfa_vidrio = 9.0e-6 # Vidrio
l_max_mm = max(ancho, alto) * 1000
deformacion_adm = 0.12 # 12.5% de deformación máxima admisible

movimiento_termico = l_max_mm * abs(alfa_al - alfa_vidrio) * dt
glueline_mm = movimiento_termico / deformacion_adm

# 5. RESULTADOS VISUALES
st.subheader("📊 Resultados de Diseño")
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Bite (Viento)", f"{bite_v_mm:.2f} mm")
with c2:
    st.metric("Bite (Peso)", f"{bite_p_mm:.2f} mm")
with c3:
    st.metric("Glueline Min.", f"{glueline_mm:.2f} mm")

# Recomendación Final
bite_final = max(math.ceil(bite_v_mm), math.ceil(bite_p_mm), 6) # Mínimo constructivo 6mm

st.markdown(f"""
<div class="result-box">
    <h3>Especificación Final:</h3>
    <p>Utilizar una mordida (Bite) de <strong>{bite_final} mm</strong> y un espesor de junta (Glueline) de <strong>{math.ceil(glueline_mm)} mm</strong>.</p>
    <small>* El diseño cumple con el límite de mordida mínima de 6mm para asegurar adherencia adecuada.</small>
</div>
""", unsafe_allow_html=True)

# 6. GRÁFICO DE COMPORTAMIENTO
st.subheader("📈 Relación Mordida vs Presión")
rango_p = np.linspace(50, 400, 20)
rango_b = [(p * lado_menor) / (2 * fv * 100) * 10 for p in rango_p]

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(rango_p, rango_b, color='#0277bd', label='Bite requerido por Viento')
ax.axhline(6, color='red', linestyle='--', label='Mínimo Constructivo (6mm)')
ax.set_xlabel("Presión de Viento (kgf/m²)")
ax.set_ylabel("Bite (mm)")
ax.grid(True, alpha=0.3)
ax.legend()
st.pyplot(fig)

# 7. CRÉDITOS Y CIERRE
st.markdown("---")
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; color: #555; font-size: 0.9em;">
        <div><strong>Autor:</strong> Mauricio Riquelme | Ing. Civil Estructural PUC</div>
        <div><strong>Contacto:</strong> mriquelme@proyectosestructurales.com</div>
    </div>
    <div style="text-align: center; margin-top: 40px;">
        <p style="font-family: 'Georgia', serif; font-size: 1.3em; color: #01579b; font-style: italic;">
            "Programming is understanding"
        </p>
    </div>
""", unsafe_allow_html=True)