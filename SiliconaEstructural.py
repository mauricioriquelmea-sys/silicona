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
    # Opción solicitada por el usuario (Desmarcada por defecto)
    toma_peso = st.checkbox("¿Silicona toma peso propio?", value=False, help="Marcar solo si NO se usan calzos de apoyo (setting blocks).")
    
    f_viento_psi = st.number_input("Esfuerzo Adm. Viento (psi)", value=20.0)
    f_peso_psi = st.number_input("Esfuerzo Adm. Peso (psi)", value=1.0)
    E_silicona_mpa = st.number_input("Módulo de Elasticidad E (MPa)", value=2.10, step=0.10)
    delta_T = st.slider("Diferencial Térmico ΔT (°C)", 10, 80, 50)

# Conversiones Técnicas
psi_to_kgcm2 = 0.070307
fv = f_viento_psi * psi_to_kgcm2
fp = f_peso_psi * psi_to_kgcm2
E_kgcm2 = E_silicona_mpa * 10.1972 

# =================================================================
# 4. MOTOR DE CÁLCULO
# =================================================================

# 1. Masa del Vidrio
volumen_vidrio = ancho * alto * (t_vidrio / 1000)
densidad_vidrio = 2500 
peso_vidrio = volumen_vidrio * densidad_vidrio

# 2. Bite por Viento (Bv)
bite_viento_mm = (p_viento * lado_menor) / (2 * fv * 100) * 10

# 3. Bite por Peso Propio (Bp) - Solo si aplica
if toma_peso:
    perimetro_cm = 2 * (ancho + alto) * 100
    bite_peso_mm = (peso_vidrio / (perimetro_cm * fp)) * 10
else:
    bite_peso_mm = 0.0  # El peso lo toman los calzos

# 4. Glueline Thickness (gt) basado en Módulo E
L_max_mm = max(ancho, alto) * 1000
alfa_al, alfa_vi = 23.2e-6, 9.0e-6
delta_L = L_max_mm * abs(alfa_al - alfa_vi) * delta_T

# Glueline Thickness mecánico
glueline_mm = (delta_L * E_kgcm2) / (fv * 1.5) 
glueline_mm = max(glueline_mm, (delta_L / 0.25)) # Mínimo por deformación técnica 25%

# ... (Todo el código anterior de cálculo se mantiene igual) ...


# =================================================================
# 5. DESPLIEGUE DE RESULTADOS CON POPUP DE CALZOS
# =================================================================
st.subheader("📊 Resultados de Análisis Estructural")

# Bloque de Peso del Vidrio con lógica de Calzos
if toma_peso:
    st.markdown(f"""
    <div class="weight-box">
        <p style="margin:5px 0; color:#555;">Peso Total del Vidrio</p>
        <p style="font-size: 1.5em; margin:0; color:#003366; font-weight:bold;">{peso_vidrio:.2f} kgf</p>
        <p style="color:#d9534f; font-weight:bold;">⚠️ Silicona CARGADA con peso propio</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Contenedor especial para calzos
    st.markdown(f"""
    <div class="weight-box" style="border-color: #28a745;">
        <p style="margin:5px 0; color:#555;">Peso Total del Vidrio</p>
        <p style="font-size: 1.5em; margin:0; color:#28a745; font-weight:bold;">{peso_vidrio:.2f} kgf</p>
        <p style="color:#28a745; font-weight:bold;">✅ Peso soportado por CALZOS (Setting Blocks)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Simulación de Popup mediante Expander técnico
    with st.expander("📍 Ver esquema de ubicación de calzos"):
        st.write("Según estándar de carpintería, los calzos deben ubicarse en los puntos de apoyo del borde inferior:")
        
        # Intentar cargar la imagen del esquema de calzos
        esquema_calzos = "ubicacion_calzos.png" # Nombre del archivo en tu repositorio
        if os.path.exists(esquema_calzos):
            st.image(esquema_calzos, caption="Ubicación típica de calzos a L/4", use_column_width=True)
        else:
            # Si no hay imagen, mostramos un diagrama instructivo
            st.warning("Esquema no encontrado. Asegúrate de subir 'ubicacion_calzos.png' a tu repositorio.")
            st.info("""
            **Referencia de Instalación:**
            - Ubicar 2 calzos en el borde inferior.
            - Distancia desde las esquinas: **L / 4** (donde L es el ancho del vidrio).
            - Material: Neopreno o EPDM (Dureza Shore A 80-90).
            """)



# Resto de métricas (Bite y Glueline)
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Bite (Viento)", f"{bite_viento_mm:.2f} mm")
with c2:
    st.metric("Bite (Peso)", f"{bite_peso_mm:.2f} mm" if toma_peso else "N/A (Calzos)")
with c3:
    st.metric("Glueline Thickness", f"{glueline_mm:.2f} mm")


# =================================================================
# 6. GRÁFICO DE SENSIBILIDAD
# =================================================================
st.subheader("📈 Comportamiento del Bite vs Viento")
p_rango = np.linspace(50, 450, 50)
b_v_rango = [(p * lado_menor) / (2 * fv * 100) * 10 for p in p_rango]

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(p_rango, b_v_rango, color='#003366', lw=2.5, label='Bite (Viento)')
if toma_peso:
    ax.axhline(bite_peso_mm, color='#d9534f', ls='--', label='Bite (Peso)')
ax.axhline(glueline_mm, color='#5cb85c', ls=':', label='Glueline Thickness')
ax.axhline(6, color='#333', lw=1, ls='-.', label='Mínimo 6mm')
ax.set_xlabel("Presión de Viento (kgf/m²)")
ax.set_ylabel("Dimensión (mm)")
ax.legend()
st.pyplot(fig)

# =================================================================
# 7. CIERRE CORPORATIVO
# =================================================================
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; color: #666;">
        <strong>Proyectos Estructurales Lab | Mauricio Riquelme</strong><br>
        <span style="font-style: italic; font-size: 1.2em; color: #003366;">"Programming is understanding"</span>
    </div>
    """, unsafe_allow_html=True)