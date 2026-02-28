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
# 4. MOTOR DE CÁLCULO Y DEFINICIÓN DE CERRAMIENTO (RIGUROSO)
# =================================================================
st.sidebar.subheader("🏠 Clasificación del Cerramiento")

# Usamos el expander exactamente como el de Importancia para mantener consistencia
with st.sidebar.expander("ℹ️ Nota Explicativa: Clasificación de Cerramiento"):
    st.markdown("""
    **Definiciones según NCh 432 (Capítulo 2):**
    
    * **Edificio Abierto:** Un edificio que tiene cada pared abierta en al menos un 80%.
    * **Edificio Parcialmente Abierto:** Cumple con área de aberturas en una pared > suma del resto en > 10%, y aberturas > 0.37 m² o 1% de la pared.
    * **Edificio Cerrado:** No cumple los requisitos de abierto o parcialmente abierto. Es el estándar para estructuras estancas.
    """)

cerramiento_opcion = st.sidebar.selectbox(
    "Tipo de Cerramiento", 
    ["Cerrado", "Parcialmente Abierto", "Abierto"],
    index=0
)

# Diccionario técnico centralizado para evitar errores de referencia
# [Factor GCpi, Nota Técnica Detallada]
gcpi_data = {
    "Cerrado": [0.18, "Edificio que no cumple con los requisitos de abierto o parcialmente abierto. Se asume estanqueidad estándar."],
    "Parcialmente Abierto": [0.55, "Edificio con aberturas significativas que permiten una presurización interna mayor durante ráfagas."],
    "Abierto": [0.00, "Edificio con al menos 80% de apertura en cada pared; la presión interna se equilibra con la externa."]
}

# Asignación segura de variables
gc_pi_val = gcpi_data[cerramiento_opcion][0]
nota_tecnica_seleccionada = gcpi_data[cerramiento_opcion][1]

st.sidebar.info(f"**Factor GCpi asociado: ± {gc_pi_val}**")

# --- MOTOR DE CÁLCULO ---
def get_gcp(a, g1, g10):
    if a <= 1.0: return g1
    if a >= 10.0: return g10
    return g1 + (g10 - g1) * (np.log10(a) - np.log10(1.0))

imp_map = {'I': 1.0, 'II': 1.0, 'III': 1.0, 'IV': 1.0} # Según NCh 432-2025 (Riesgo en V)
exp_params = {'B': [7.0, 366.0], 'C': [9.5, 274.0], 'D': [11.5, 213.0]}
alpha, zg = exp_params[cat_exp]

# Kz calculado a la altura H
kz_h = 2.01 * ((max(H_edif, 4.6) / zg)**(2/alpha))
qh = (0.613 * kz_h * Kzt_val * Kd_val * (V**2) * imp_map[cat_imp]) * 0.10197

# =================================================================
# 5. DESPLIEGUE TÉCNICO DE RESULTADOS Y FORMULACIÓN
# =================================================================

# Ficha de Cerramiento Destacada (CORRECCIÓN DE CARGA)
st.markdown(f"""
<div class="classification-box">
    <strong>📋 Ficha Técnica de Cerramiento (NCh 432):</strong><br><br>
    <strong>Clasificación Seleccionada:</strong> {cerramiento_opcion}<br>
    <span style="font-size: 1.5em; color: #d9534f;"><strong>Factor de Presión Interna (GCpi): ± {gc_pi_val}</strong></span><br><br>
    <strong>Nota Normativa:</strong> {nota_tecnica_seleccionada}
</div>
""", unsafe_allow_html=True)

# Caja de Fórmulas y Ecuaciones con LaTeX Riguroso
st.markdown("### 📝 Ecuaciones de Diseño Aplicadas")
st.latex(r"q_h = 0.613 \cdot K_z \cdot K_{zt} \cdot K_d \cdot V^2 \cdot I")
st.latex(r"p = q_h \cdot [GC_p - GC_{pi}]")

st.info(f"**Presión de velocidad máxima (qh):** {qh:.2f} kgf/m²")

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