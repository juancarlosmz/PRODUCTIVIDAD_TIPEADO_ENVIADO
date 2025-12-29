import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. CONFIGURACIÓN DE NUEVAS URLs ---
# Tipeado
file_id_tipeado = '1zW0zclhDx1xvQMowInP0vpbbKailFY_b0QQDx1luJ6M' 
# Enviado
file_id_enviado = '1KkErjiyIx47YwEbCLF80YYTHQAjMC9UTLMzEkqpWPKY' 

urls = [
    f'https://docs.google.com/spreadsheets/d/{file_id_tipeado}/export?format=xlsx',
    f'https://docs.google.com/spreadsheets/d/{file_id_enviado}/export?format=xlsx'
]

try:
    # Carga de datos
    df_tipeado = pd.read_excel(urls[0])
    df_enviado = pd.read_excel(urls[1])
    
    meses_nombres = ["MAYO", "JUNIO", "JULIO", "AGOSTO", "SETIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    
    # Limpieza: Convertir a mayúsculas y quitar espacios en la columna USUARIO (asumida columna 0)
    for df in [df_tipeado, df_enviado]:
        df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.strip().str.upper()

    # Obtener lista de usuarios únicos (excluyendo "TOTAL" si existe)
    usuarios = [u for u in df_tipeado.iloc[:, 0].unique() if u != "TOTAL"]

    # --- 2. CREACIÓN DEL DASHBOARD (4 FILAS) ---
    fig = make_subplots(
        rows=4, cols=1, 
        vertical_spacing=0.05,
        subplot_titles=(
            "Semáforo: Tipeado por Usuario", "Tendencia Histórica de Tipeado",
            "Semáforo: Enviado por Usuario", "Tendencia Histórica de Enviado"
        ),
        specs=[[{"type": "bar"}], [{"type": "scatter"}], 
               [{"type": "bar"}], [{"type": "scatter"}]]
    )

    # --- 3. GENERAR TRACES ---

    # --- A. TIPEADO (Fila 1 y 2) ---
    for i, mes in enumerate(meses_nombres):
        val = pd.to_numeric(df_tipeado[mes], errors='coerce').fillna(0)
        # Color Verde si sube, Rojo si baja respecto al mes anterior
        col = ['#27AE60' if i>0 and a >= pd.to_numeric(df_tipeado[meses_nombres[i-1]], errors='coerce').fillna(0).iloc[idx] else '#E74C3C' for idx, a in enumerate(val)] if i>0 else '#3498DB'
        fig.add_trace(go.Bar(x=df_tipeado.iloc[:, 0], y=val, marker_color=col, visible=(mes=="DICIEMBRE"), text=val, textposition='outside', showlegend=False), row=1, col=1)

    for u in usuarios:
        data_u = df_tipeado[df_tipeado.iloc[:, 0] == u]
        y_vals = [data_u[m].values[0] if not data_u.empty else 0 for m in meses_nombres]
        fig.add_trace(go.Scatter(x=meses_nombres, y=y_vals, name=f"Tipeado: {u}", mode='lines+markers'), row=2, col=1)

    # --- B. ENVIADO (Fila 3 y 4) ---
    for i, mes in enumerate(meses_nombres):
        val = pd.to_numeric(df_enviado[mes], errors='coerce').fillna(0)
        col = ['#27AE60' if i>0 and a >= pd.to_numeric(df_enviado[meses_nombres[i-1]], errors='coerce').fillna(0).iloc[idx] else '#E74C3C' for idx, a in enumerate(val)] if i>0 else '#9B59B6'
        fig.add_trace(go.Bar(x=df_enviado.iloc[:, 0], y=val, marker_color=col, visible=(mes=="DICIEMBRE"), text=val, textposition='outside', showlegend=False), row=3, col=1)

    for u in usuarios:
        data_u = df_enviado[df_enviado.iloc[:, 0] == u]
        y_vals = [data_u[m].values[0] if not data_u.empty else 0 for m in meses_nombres]
        fig.add_trace(go.Scatter(x=meses_nombres, y=y_vals, name=f"Enviado: {u}", mode='lines+markers'), row=4, col=1)

    # --- 4. BOTONES DE FILTRADO (Lógica de visibilidad) ---
    num_usuarios = len(usuarios)
    num_meses = len(meses_nombres)
    
    botones = []
    for i, mes in enumerate(meses_nombres):
        m_final = [False] * len(fig.data)
        
        # Activar Bar Tipeado del mes i
        m_final[i] = True
        # Activar Scatters Tipeado (siempre visibles)
        start_scatter_tip = num_meses
        end_scatter_tip = num_meses + num_usuarios
        m_final[start_scatter_tip : end_scatter_tip] = [True] * num_usuarios
        
        # Activar Bar Enviado del mes i
        m_final[end_scatter_tip + i] = True
        # Activar Scatters Enviado (siempre visibles)
        start_scatter_env = end_scatter_tip + num_meses
        m_final[start_scatter_env:] = [True] * num_usuarios

        botones.append(dict(label=f"MES: {mes}", method="update", args=[{"visible": m_final}]))

    fig.update_layout(
        updatemenus=[dict(active=7, buttons=botones, x=0.01, y=1.03)],
        title='<b>REPORTE DE USUARIOS: TIPEADO Y ENVIADO</b>',
        height=1800, # Altura reducida ya que hay menos gráficos
        template='plotly_white',
        margin=dict(t=150, b=50)
    )

    #fig.update_layout(
    #    updatemenus=[dict(active=7, buttons=botones, x=0.01, y=1.03)],
    #    title='<b>TIPEADO - ENVIADO</b>',
    #    height=3800, template='plotly_white', margin=dict(t=150, b=50)
    #)
    #fig.show()
    fig.write_html("index.html", full_html=True, include_plotlyjs='cdn')
    print("¡Archivo index.html generado con éxito!")

except Exception as e:
    print(f"Error en la integración: {e}")
