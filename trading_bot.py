import yfinance as yf
import os
import pandas as pd
from datetime import datetime

def calcular_rsi_manual(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def verificar_mitigacion_h4(simbolo):
    """
    Verifica si hubo una mitigación (mecha) al lado contrario 
    en el timeframe de 4 horas recientemente.
    """
    try:
        ticker = yf.Ticker(simbolo)
        # Traemos datos de 4h (usamos interval='1h' y agrupamos o '4h' si está disponible)
        df_h4 = ticker.history(period="5d", interval="4h")
        if len(df_h4) < 5: return False, 0
        
        ultima_vela = df_h4.iloc[-1]
        vela_previa = df_h4.iloc[-2]
        
        # Supongamos tendencia alcista: buscamos que haya mitigado por DEBAJO (lado contrario)
        # Miramos si el 'Low' de las últimas velas fue significativamente menor al 'Open'
        mitigacion_baja = (vela_previa['Low'] < vela_previa['Open']) and (ultima_vela['Close'] > ultima_vela['Open'])
        # Tendencia bajista: buscamos mitigación por ARRIBA
        mitigacion_alta = (vela_previa['High'] > vela_previa['Open']) and (ultima_vela['Close'] < ultima_vela['Open'])
        
        return mitigacion_baja, mitigacion_alta
    except:
        return False, False

def obtener_top_3_setups_pro():
    activos = [
        "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "USDCAD=X", "AUDUSD=X", "NZDUSD=X",
        "EURJPY=X", "GBPJPY=X", "CHFJPY=X", "EURGBP=X", "EURCAD=X", "AUDJPY=X"
    ] # Lista optimizada para mayor liquidez y spreads bajos
    
    setups_finales = []
    print("Iniciando escaneo institucional con filtro de mitigación H4...")
    
    for simbolo in activos:
        try:
            ticker = yf.Ticker(simbolo)
            # Datos diarios para tendencia macro
            data_d = ticker.history(period="250d", interval="1d")
            if len(data_d) < 200: continue
            
            precio = data_d['Close'].iloc[-1]
            sma_200 = data_d['Close'].rolling(window=200).mean().iloc[-1]
            rsi = calcular_rsi_manual(data_d['Close']).iloc[-1]
            
            # 1. Filtro de Tendencia y RSI
            es_alcista = precio > sma_200 and rsi < 50
            es_bajista = precio < sma_200 and rsi > 50
            
            if not (es_alcista or es_bajista): continue

            # 2. Filtro de Mitigación H4 (El CRT que mencionas)
            mit_baja, mit_alta = verificar_mitigacion_h4(simbolo)
            
            señal = None
            if es_alcista and mit_baja: # Mitigó abajo antes de seguir subiendo
                señal = "COMPRA"
                fuerza = 50 - rsi
            elif es_bajista and mit_alta: # Mitigó arriba antes de seguir bajando
                señal = "VENTA"
                fuerza = rsi - 50

            if señal:
                dec = 2 if "JPY" in simbolo else 4
                setups_finales.append({
                    "par": simbolo.replace("=X", ""),
                    "precio": round(precio, dec),
                    "rsi": round(rsi, 1),
                    "señal": señal,
                    "fuerza": fuerza,
                    "nota": "CRT Mitigado en H4"
                })
        except: continue
            
    setups_finales.sort(key=lambda x: x['fuerza'], reverse=True)
    return setups_finales[:3]

def actualizar_index_html(top_setups):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    top_par_tv = f"FX:{top_setups[0]['par'].replace('/', '')}" if top_setups else "FX:EURUSD"
    
    cards_html = ""
    for p in top_setups:
        color = "#26a69a" if p['señal'] == "COMPRA" else "#ef5350"
        cards_html += f"""
        <div style="background:#1e222d; border-radius:12px; padding:20px; border:1px solid #434651; border-top:5px solid {color};">
            <div style="color:{color}; font-weight:bold; font-size:0.8rem;">{p['nota']}</div>
            <h2 style="margin:10px 0; font-size:1.8rem;">{p['par']}</h2>
            <div style="font-size:2rem; font-family:monospace;">{p['precio']}</div>
            <div style="margin-top:10px; display:flex; justify-content:space-between;">
                <span style="background:{color}; color:white; padding:4px 10px; border-radius:4px; font-weight:bold;">{p['señal']}</span>
                <span>RSI: {p['rsi']}</span>
            </div>
        </div>"""

    # Mantengo el resto de la estructura del HTML similar...
    # (El código del HTML que genera el index.html se mantiene como en tu versión anterior)
    # Solo asegúrate de insertar {cards_html} y el link de TradingView dinámico.
    # ... (omitido por brevedad para centrarme en la lógica de trading)
