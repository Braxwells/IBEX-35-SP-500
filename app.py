import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- Cargar datos simulados ---
@st.cache_data
def cargar_datos():
    df_ibex = pd.read_csv('predicciones_ibex.csv')
    df_sp = pd.read_csv('predicciones_rnn_sp.csv')
    return df_ibex, df_sp

df_ibex, df_sp = cargar_datos()

# --- Estado inicial de sesión ---
if 'modo_activado' not in st.session_state:
    st.session_state.modo_activado = False
if 'saldo' not in st.session_state:
    st.session_state.saldo = 10000.0
if 'inversion' not in st.session_state:
    st.session_state.inversion = 0.0
if 'ganancias' not in st.session_state:
    st.session_state.ganancias = 0.0
if 'historial' not in st.session_state:
    st.session_state.historial = []

# --- Sidebar navegación ---
pagina = st.sidebar.radio("Navegación", ["📊 Visualizar", "🤖 Modo Automático", "📈 Posiciones", "💰 Depositar / Retirar"])

# --- Cabecera de estado ---
col1, col2, col3 = st.columns(3)
col1.metric("💰 Saldo Actual", f"€{st.session_state.saldo:,.2f}")
col2.metric("🏦 Inversión Activa", f"€{st.session_state.inversion:,.2f}")
col3.metric("📈 Ganancias Totales", f"€{st.session_state.ganancias:,.2f}")

st.title("Aplicación de Inversión con IA - RNN")

# --- Visualizar ---
if pagina == "📊 Visualizar":
    st.header("Visualización de Predicciones")
    indice = st.selectbox("Selecciona el índice:", ["IBEX 35", "S&P 500"])
    df = df_ibex if indice == "IBEX 35" else df_sp

    # Mostrar tabla con precios reales y predicciones
    st.subheader("Vista de Datos")


    # Rango de fechas
    inicio = st.slider("Día inicial", 0, len(df)-100, 0)
    fin = st.slider("Día final", inicio+50, len(df), len(df))
    df = df.iloc[inicio:fin]

    # Gráfico
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df['Precio_Real'].values, label='Real', color='red')
    ax.plot(df['Prediccion_RNN'].values, label='Predicción RNN', color='cyan')
    ax.set_title(f'Predicción con RNN - {indice}')
    ax.set_xlabel('Días')
    ax.set_ylabel('Precio')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.dataframe(
        df[['Price', 'Precio_Real', 'Prediccion_RNN']]
        .rename(columns={'Price': 'Día'}),
        use_container_width=True
    )

# --- Modo Automático ---
elif pagina == "🤖 Modo Automático":
    st.header("Modo IA Automático")
    activado = st.toggle("Activar IA para detectar oportunidades de inversión", value=st.session_state.modo_activado)
    st.session_state.modo_activado = activado

    if activado:
        st.success("✅ Modo IA activado. Analizando tendencias para decisiones de short o long en tramos de 1 a 3 horas.")

        # Simulador de señal
        if st.button("Iniciar inversión simulada"):
            direccion = st.radio("Dirección de la apuesta:", ['Long', 'Short'])
            cantidad = st.slider("Cantidad a invertir (€):", 100, int(st.session_state.saldo), 500)
            precio_entrada = df_sp['Precio_Real'].iloc[-1]
            st.session_state.saldo -= cantidad
            st.session_state.inversion += cantidad
            st.session_state.historial.append({
                'Hora Inicio': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Hora Fin': '',
                'Inversión (€)': cantidad,
                'Profit (€)': '',
                'Cambio Precio': '',
                'Estado': 'Abierta',
                'Dirección': direccion,
                'Precio Entrada': precio_entrada
            })
    else:
        st.warning("⚠️ El modo automático está desactivado.")

# --- Posiciones ---
elif pagina == "📈 Posiciones":
    st.header("Historial de Inversiones")
    if not st.session_state.historial:
        st.info("No hay posiciones realizadas.")
    else:
        for i, pos in enumerate(st.session_state.historial):
            with st.expander(f"Posición #{i+1} - {pos['Estado']}"):
                st.write(pos)
                if pos['Estado'] == 'Abierta':
                    if st.button(f"Cerrar Posición #{i+1}"):
                        precio_actual = df_sp['Precio_Real'].iloc[-1]
                        cambio = precio_actual - pos['Precio Entrada']
                        if pos['Dirección'] == 'Short':
                            cambio *= -1
                        ganancia = cambio * 100  # factor arbitrario de escala
                        st.session_state.ganancias += ganancia
                        st.session_state.inversion -= pos['Inversión (€)']
                        st.session_state.saldo += pos['Inversión (€)'] + ganancia
                        pos['Hora Fin'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        pos['Profit (€)'] = f"{ganancia:.2f}"
                        pos['Cambio Precio'] = f"{cambio:.4f}"
                        pos['Estado'] = 'Cerrada'

# --- Depositar / Retirar ---
elif pagina == "💰 Depositar / Retirar":
    st.header("Gestión de Fondos")
    deposito = st.number_input("Cantidad a depositar (€):", min_value=0)
    retiro = st.number_input("Cantidad a retirar (€):", min_value=0)

    if st.button("Actualizar saldo"):
        st.session_state.saldo += deposito - retiro
        st.success(f"Saldo actualizado: €{st.session_state.saldo:,.2f}")

# --- Chat flotante inferior derecha ---
with st.container():
    st.markdown("""
    <div style='position:fixed; bottom:20px; right:20px; background:#f1f3f5; padding:15px 20px; border-radius:10px; box-shadow:0 2px 6px rgba(0,0,0,0.2); width:300px;'>
        <h4>🤖 Ayuda IA</h4>
        <p style='font-size:14px;'>Hola! Soy tu asistente IA. ¿Necesitas ayuda para navegar o invertir?</p>
        <input type='text' placeholder='Escribe aquí...' style='width:100%; padding:5px; border:none; border-radius:5px; margin-top:5px;'>
    </div>
    """, unsafe_allow_html=True)
