import streamlit as st
import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# --- 1. CONFIGURACIÓN BASE DE LA PÁGINA ---
st.set_page_config(
    page_title="Asistente Judicial - Juzgados de Familia", 
    page_icon="⚖️", 
    layout="centered"
)

# URL Real y definitiva entregada por Streamlit con la barra '/' al final
DIRECCION_RETORNO = "https://appfamiliagemini.streamlit.app/" 

# Estilos CSS personalizados para el diseño móvil y botones del portal
st.markdown("""
    <style>
    div[data-testid="stSidebar"] img {
        border-radius: 50% !important;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.15);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #2e59a8;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email"
]

# FUNCIÓN DE AUTENTICACIÓN DIRECTA POR SECRETS
@st.cache_resource
def obtener_configuracion_oauth():
    try:
        info_secrets = json.loads(st.secrets["CLIENT_SECRET_JSON"])
        return Flow.from_client_config(
            info_secrets,
            scopes=SCOPES,
            redirect_uri=DIRECCION_RETORNO
        )
    except Exception as e:
        st.error(f"Error al cargar configuraciones secretas: {e}")
        return None

# --- 2. GESTIÓN DE SESIÓN ---
if "usuario" not in st.session_state:
    st.session_state.usuario = None

parametros_url = st.query_params

if "code" in parametros_url and st.session_state.usuario is None:
    try:
        flow = obtener_configuracion_oauth()
        if flow is not None:
            flow.fetch_token(code=parametros_url["code"])
            credenciales = flow.credentials
            datos_perfil = id_token.verify_oauth2_token(
                credenciales.id_token,
                google_requests.Request(),
                flow.client_config["client_id"]
            )
            st.session_state.usuario = datos_perfil
            st.query_params.clear() 
            st.rerun()
    except Exception as e:
        st.error(f"Error en acceso seguro: {e}")

# --- 3. DIBUJAR PANTALLAS ---

if st.session_state.usuario is None:
    # ==========================================
    # PANTALLA ACCESO (Desconectado)
    # ==========================================
    st.title("⚖️ Asistente Judicial de Familia")
    st.markdown("### Portal IA para la comprensión de procedimientos en Chile")
    st.write("Para resguardar la privacidad de tus causas, escritos y e-books, ingresa con Google.")
    
    flow = obtener_configuracion_oauth()
    if flow is not None:
        url_autorizacion, _ = flow.authorization_url(prompt='select_account', access_type='offline')
        
        st.markdown(f"""
            <a href="{url_autorizacion}" target="_self" style="text-decoration: none;">
                <div style="
                    width: 100%; background-color: #ffffff; color: #202124; border: 1px solid #dadce0; 
                    padding: 12px; border-radius: 8px; font-size: 16px; font-weight: 500;
                    font-family: 'Roboto', sans-serif; cursor: pointer; display: flex; 
                    align-items: center; justify-content: center; gap: 12px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                ">
                    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="18px" height="18px" viewBox="0 0 48 48">
                        <g>
                            <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"></path>
                            <path fill="#4285F4" d="M46.5 24c0-1.55-.15-3.24-.47-4.77H24v9.03h12.75c-.55 2.97-2.22 5.5-4.74 7.2l7.38 5.73c4.32-3.99 7.11-9.86 7.11-17.16z"></path>
                            <path fill="#FBBC05" d="M10.54 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.98-6.19z"></path>
                            <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.38-5.73c-2.11 1.4-4.81 2.3-8.51 2.3-6.26 0-11.57-4.22-13.46-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"></path>
                        </g>
                    </svg>
                    Continuar con Google
                </div>
            </a>
            <br>
        """, unsafe_allow_html=True)
    else:
        st.warning("Verifica la carga del secreto CLIENT_SECRET_JSON en el panel de Streamlit.")

else:
    # ==========================================
    # PANTALLA INTERIOR (Tu diseño de pestañas)
    # ==========================================
    perfil = st.session_state.usuario
    
    with st.sidebar:
        st.markdown("### 👤 Mi Cuenta")
        if "picture" in perfil:
            st.image(perfil["picture"], width=90)
            
        st.write(f"**{perfil.get('name')}**")
        st.write(f"✉️ {perfil.get('email')}")
        st.markdown("---")
        st.caption("Asistente legal entrenado para Juzgados de Familia de Chile.")
        
        if st.button("Cerrar Sesión"):
            st.session_state.usuario = None
            st.query_params.clear()
            st.rerun()
            
    st.title("🤖 Asistente Virtual IA")
    st.subheader("Tribunales de Familia Chile")
    st.markdown("---")
    
    # Creación de pestañas basadas en tu bosquejo
    tab1, tab2, tab3 = st.tabs(["📄 Explicar Escrito", "📚 Resumir E-book", "✍️ Preparar Escrito"])
    
    with tab1:
        st.markdown("#### Sube una notificación o resolución de la causa")
        archivo_escrito = st.file_uploader("Cargar documento judicial (PDF)", type=["pdf"], key="escrito_pdf")
        if archivo_escrito:
            st.success("✅ Escrito cargado con éxito.")
            st.info("Aquí aparecerá el análisis de Gemini una vez que conectemos el motor de IA.")
                
    with tab2:
        st.markdown("#### Sube material doctrinal o un libro legal largo")
        archivo_ebook = st.file_uploader("Cargar e-book o ley (PDF)", type=["pdf"], key="ebook_pdf")
        if archivo_ebook:
            st.success("✅ Libro recibido por el asistente.")
            st.info("Aquí aparecerá el resumen del libro procesado por la IA.")

    with tab3:
        st.markdown("#### Generador de borradores legales")
        st.write("Cuéntale a la IA qué necesitas solicitarle al tribunal:")
        instruccion = st.text_area("Detalla tu solicitud aquí (Ej: Solicito liquidación de pensión de alimentos):")
        if st.button("Generar Borrador con IA"):
            if instruccion:
                st.success("Aquí Gemini redactará la plantilla formal con la estructura legal chilena.")
