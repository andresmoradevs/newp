import flet as ft
from binance.client import Client
from binance.enums import *
import threading
import time

# Configura tus credenciales de API de Binance
api_key = '0'
api_secret = '0'

# Conectar a Binance
client = Client(api_key, api_secret)

# Configurar apalancamiento (20x en este ejemplo)
def configurar_apalancamiento():
    try:
        client.futures_change_leverage(symbol='DENTUSDT', leverage=20)
        print("Apalancamiento configurado a 20x")
    except Exception as e:
        print(f"Error al configurar el apalancamiento: {e}")

# Función para obtener saldo
def obtener_saldo():
    balance = client.futures_account_balance()
    for asset in balance:
        if asset['asset'] == 'USDT':
            return float(asset['balance'])

# Función para obtener el precio actual del par
def obtener_precio(par):
    ticker = client.futures_symbol_ticker(symbol=par)
    return float(ticker['price'])

# Función para ejecutar una orden
def ejecutar_orden(par, lado, cantidad):
    order = client.futures_create_order(
        symbol=par,
        side=lado,
        type=ORDER_TYPE_MARKET,
        quantity=cantidad
    )
    return order

# Estrategia básica del bot
def estrategia_bot():
    while bot_running:
        try:
            # Obtener el precio actual del par
            precio = obtener_precio('DENTUSDT')
            # Calcular la cantidad mínima para cumplir con el requisito de 5 USDT usando apalancamiento
            cantidad_minima = (5 / precio) / 20  # Usando 20x apalancamiento
            cantidad_minima = round(cantidad_minima, 0)  # Redondear a la unidad más cercana
            
            if bot_running:
                orden = ejecutar_orden('DENTUSDT', SIDE_BUY, cantidad_minima)
                actualizar_historial(f"Comprado: {orden}")
                time.sleep(10)
            if bot_running:
                orden = ejecutar_orden('DENTUSDT', SIDE_SELL, cantidad_minima)
                actualizar_historial(f"Vendido: {orden}")
                time.sleep(10)
        except Exception as e:
            actualizar_historial(f"Error: {e}")

# Variables para controlar el estado del bot
bot_thread = None
bot_running = False

# Función para iniciar el bot
def iniciar_bot(e):
    global bot_thread, bot_running
    if not bot_running:
        bot_running = True
        bot_thread = threading.Thread(target=estrategia_bot)
        bot_thread.start()
        actualizar_historial("Bot iniciado.")

# Función para detener el bot
def detener_bot(e):
    global bot_running
    if bot_running:
        bot_running = False
        if bot_thread:
            bot_thread.join()
        actualizar_historial("Bot detenido.")

# Función para actualizar el historial de órdenes
def actualizar_historial(mensaje):
    historial_view.controls.append(ft.Text(mensaje))
    historial_view.update()

# Función para actualizar el saldo
def actualizar_saldo():
    saldo_actual = obtener_saldo()
    saldo_text.value = f"Saldo actual: {saldo_actual:.2f} USDT"
    saldo_text.update()
    # Reprogramar el temporizador para actualizar el saldo nuevamente en 10 segundos
    threading.Timer(10, actualizar_saldo).start()

# Función para limpiar el historial
def limpiar_historial(e):
    historial_view.controls.clear()
    historial_view.update()

# Función para cambiar entre modo claro y oscuro
def cambiar_tema(e, page):
    if page.theme_mode == ft.ThemeMode.LIGHT:
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.LIGHT
    page.update()

# Crear la interfaz con Flet
def main(page: ft.Page):
    page.title = "Bot de Trading con Binance"
    page.theme_mode = ft.ThemeMode.LIGHT  # Establece el modo inicial en claro
    
    global historial_view, saldo_text
    
    historial_view = ft.Column()
    saldo_text = ft.Text("Saldo actual: 1.76 USDT")  # Inicialmente mostrando el saldo actual
    
    boton_iniciar = ft.ElevatedButton("Iniciar Bot", on_click=iniciar_bot)
    boton_detener = ft.ElevatedButton("Detener Bot", on_click=detener_bot)
    boton_actualizar_saldo = ft.ElevatedButton("Actualizar Saldo", on_click=lambda e: actualizar_saldo())
    boton_limpia_historial = ft.ElevatedButton("Limpiar Historial", on_click=limpiar_historial)
    boton_cambiar_tema = ft.ElevatedButton("Cambiar Tema", on_click=lambda e: cambiar_tema(e, page))
    
    page.add(
        saldo_text,
        boton_iniciar,
        boton_detener,
        boton_actualizar_saldo,
        boton_limpia_historial,
        boton_cambiar_tema,
        ft.Divider(),
        historial_view
    )

    # Configurar apalancamiento al iniciar la app
    configurar_apalancamiento()
    
    # Iniciar la actualización automática del saldo
    actualizar_saldo()

ft.app(target=main)
