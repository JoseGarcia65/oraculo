import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def generar_pronostico():
    ticker = yf.Ticker("GBPUSD=X")
    # Pedimos datos de los últimos 2 días para calcular una media simple
    data = ticker.history(period="2d", interval="1h")
    precio_actual = round(data['Close'].iloc[-1], 5)
    media_movil = data['Close'].mean()
    
    # Lógica de decisión: 
    # Si el precio está por encima de la media de las últimas horas -> COMPRA
    # Si está por debajo -> VENTA
    if precio_actual > media_movil:
        accion = "COMPRA (LONG)"
        color_accion = "#26a69a" # Verde
        tp = round(precio_actual + 0.0045, 5)
        sl = round(precio_actual - 0.0025, 5)
    else:
        accion = "VENTA (SHORT)"
        color_accion = "#ef5350" # Rojo
        tp = round(precio_actual - 0.0045, 5)
        sl = round(precio_actual + 0.0025, 5)

    return {
        "par": "GBP/USD",
        "accion": accion,
        "color": color_accion,
        "precio": precio_actual,
        "tp": tp,
        "sl": sl,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def actualizar_index_html(p):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Forex Live Bot | Dashboard</title>
        <style>
            body {{ background-color: #131722; color: #d1d4dc; font-family: sans-serif; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }}
            .container {{ display: flex; flex-wrap: wrap; gap: 20px; max-width: 1200px; width: 100%; justify-content: center; }}
            .card {{ background: #1e222d; border: 1px solid #434651; padding: 25px; border-radius: 12px; flex: 1 1 300px; max-width: 350px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }}
            .signal-badge {{ background-color: {p['color']}; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 1.2rem; display: inline-block; margin-bottom: 15px; text-transform: uppercase; }}
            .price {{ font-size: 2.8rem; color: #ffffff; font-family: monospace; margin: 10px 0; }}
            .chart-container {{ flex: 2 1 600px; height: 500px; background: #1e222d; border: 1px solid #434651; border-radius: 12px; overflow: hidden; }}
            .label {{ color: #787b86; font-size: 0.9rem; }}
            .value {{ font-weight: bold; font-size: 1.3rem; }}
        </style>
    </head>
    <body>
        <h1 style="margin-bottom:30px;">Panel de Control Forex 2026</h1>
        <div class="container">
            <div class="card">
                <div class="signal-badge">{p['accion']}</div>
                <h2 style="margin:0;">{p['par']}</h2>
                <div class="price">{p['precio']}</div>
                <hr style="border: 0; border-top: 1px solid #434651; margin: 20px 0;">
                <p><span class="label">🎯 Take Profit:</span> <br><span class="value" style="color:#26a69a">{p['tp']}</span></p>
                <p><span class="label">🛑 Stop Loss:</span> <br><span class="value" style="color:#ef5350">{p['sl']}</span></p>
                <div class="label" style="margin-top:20px;">Actualizado: {p['fecha']} (UTC)</div>
            </div>

            <div class="chart-container">
                <div id="tradingview_widget" style="height:100%;width:100%"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                <script type="text/javascript">
                new TradingView.widget({{
                    "autosize": true,
                    "symbol": "FX:GBPUSD",
                    "interval": "60",
                    "theme": "dark",
                    "style": "1",
                    "locale": "es",
                    "container_id": "tradingview_widget"
                }});
                </script>
            </div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
if __name__ == "__main__":
    datos = generar_pronostico()
    actualizar_index_html(datos)
    print(f"Web actualizada con precio: {datos['precio']}")
    # Aquí podrías llamar también a tu función de enviar_correo(datos)
