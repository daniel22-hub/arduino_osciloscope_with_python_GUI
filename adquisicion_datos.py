from matplotlib import animation
import serial
import serial.tools.list_ports
import time
from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#******************************** INICIALIZACION DE VARIABLES globales
puerto_baud = 9600
arduino = None  # Creamos el objeto vacío para usarlo globalmente
graficando = False #Bandera para controlar el estado de la gráfica (play/pause)

#******************************** FUNCIONES PROPIAS
def escanear_puertos():
    puertos_detectados = serial.tools.list_ports.comports()
    lista_puertos = [puerto.device for puerto in puertos_detectados]
    
    if lista_puertos:
        com_list['values'] = lista_puertos
        com_list.current(0)
        lbl_com.config(text="Puertos detectados con éxito.", fg="green")
    else:
        com_list['values'] = ["Sin conexión"]
        com_list.current(0)

def obtener_seleccion():
    global arduino  # Usamos la variable global
    valor = com_list.get()
    
    if valor and valor != "Sin conexión":
        try:    
            lbl_com.config(text=f"Conectando a: {valor}...", fg="blue")
            window.update() # Forzamos a la GUI a actualizar el texto inmediatamente
            
            # 1. Abrimos el puerto que el usuario seleccionó en la lista
            arduino = serial.Serial(valor, puerto_baud, timeout=1)
            time.sleep(2) # Pausa necesaria porque el Arduino se reinicia al conectar el puerto serie
            arduino.reset_input_buffer()
            lbl_com.config(text=f"Conexión exitosa a: {valor}", fg="green")
            
            # 2. Enviamos la letra 'I'
            arduino.write("I".encode('utf-8'))
            
            # 3. Programamos la lectura para no bloquear la interfaz.
            # En 500 ms, Tkinter llamará automáticamente a la función 'leer_id'
            window.after(500, leer_id)
            
        except serial.SerialException:
            lbl_com.config(text=f"Error: No se pudo abrir {valor}", fg="red")
    else:
        lbl_com.config(text="Selección inválida", fg="red")

def leer_id():
    global arduino
    if arduino and arduino.is_open:
        num_respuestas = arduino.in_waiting
        if num_respuestas > 0:
            # Leemos la respuesta
            respuesta = arduino.readline().decode('utf-8').rstrip()
            lbl_id.config(text=f"ID: {respuesta}", fg="black")
        else:
            # Si el Arduino aún no contesta, volvemos a intentar en 100 ms
            window.after(100, leer_id)

def iniciar_grafica():
    global graficando
    if arduino and arduino.is_open:
        # Limpiamos el buffer para no leer restos del ID por accidente
        arduino.reset_input_buffer()
        graficando = True
    else:
        print("Conectar Arduino")

def play(frame):
    global arduino, graficando
    # 1. Si la bandera es False, la animación no hace nada y retorna inmediatamente
    if not graficando:
        return linea,
        
    if arduino and arduino.is_open:
        arduino.write("M".encode('utf-8'))
        num_respuestas = arduino.in_waiting
        if num_respuestas > 0:
            respuesta = arduino.read(num_respuestas).decode('utf-8').rstrip()
            valores = respuesta.split(',')
            if len(valores) == 6:
                v1, v2, v3, v4, v5, v6 = map(float, valores)
                y_data1.append(v1)
                y_data2.append(v2)
                y_data3.append(v3)
                y_data4.append(v4)
                y_data5.append(v5)
                y_data6.append(v6)
                x_data.append(frame) 

def pausar_grafica():
    global graficando
    graficando = False

def pause():
    global arduino, graficando

def detener_grafica():
    global graficando, x_data, y_data1, y_data2, y_data3, y_data4, y_data5, y_data6
    graficando = False
    x_data.clear()
    y_data1.clear()
    y_data2.clear()
    y_data3.clear()
    y_data4.clear()
    y_data5.clear()
    y_data6.clear()
    linea1.set_data(x_data, y_data1)
    linea2.set_data(x_data, y_data2)
    linea3.set_data(x_data, y_data3)
    linea4.set_data(x_data, y_data4)
    linea5.set_data(x_data, y_data5)
    linea6.set_data(x_data, y_data6)
    ax.set_xlim(0, MAX_PUNTOS)
    ax.set_ylim(-2, 7)

def actualizar_canales():
    global channel1, channel2, channel3, channel4, channel5, channel6
    linea1.set_visible(channel1.get())
    linea2.set_visible(channel2.get())
    linea3.set_visible(channel3.get())
    linea4.set_visible(channel4.get())
    linea5.set_visible(channel5.get())
    linea6.set_visible(channel6.get())
    
    lineas_activas = []
    etiquetas = []

    if channel1.get():
        lineas_activas.append(linea1)
        etiquetas.append("Canal 1")
    if channel2.get():
        lineas_activas.append(linea2)
        etiquetas.append("Canal 2")
    if channel3.get():
        lineas_activas.append(linea3)
        etiquetas.append("Canal 3")
    if channel4.get():
        lineas_activas.append(linea4)
        etiquetas.append("Canal 4")
    if channel5.get():
        lineas_activas.append(linea5)
        etiquetas.append("Canal 5")
    if channel6.get():
        lineas_activas.append(linea6)
        etiquetas.append("Canal 6")
    
    if lineas_activas:
        # Si hay al menos una línea, creamos la leyenda con esas líneas
        ax.legend(lineas_activas, etiquetas, loc="upper right")
    else:
        # Si el usuario apagó todas las líneas, eliminamos el cuadro de leyenda
        leyenda_actual = ax.get_legend()
        if leyenda_actual:
            leyenda_actual.remove()
    canvas.draw_idle()  # Redibujamos la gráfica para actualizar la leyenda

#******************************** MAIN GUI
window = Tk()
window.geometry("1000x600+10+10")
window.resizable(False, False)
window.title("GUI Voltimetro")
window.configure(bg="#b8b8b8")

# ==========================================
# SECCIÓN IZQUIERDA: Panel de Controles
# ==========================================
panel_izquierdo = Frame(window, width=250, bg="#e0e0e0", relief=SUNKEN, borderwidth=2)
panel_izquierdo.pack(side=LEFT, fill=Y, padx=5, pady=5)
panel_izquierdo.pack_propagate(False)

# ------------------------------------------ PANEL DE COMUNICACION
frame_comunicacion = Frame(panel_izquierdo, bg="lightblue") 
frame_comunicacion.pack(side=TOP, fill=X, padx=10, pady=10)

comunicacion_lbl = Label(frame_comunicacion, text="COMUNICACION", bg="lightblue")
comunicacion_lbl.pack(pady=5)

frame_puerto_com = Frame(frame_comunicacion, bg="lightblue")
frame_puerto_com.pack(side=TOP, fill=X, padx=5, pady=5)

com_list = ttk.Combobox(frame_puerto_com, state="readonly", width=15)
com_list.pack(side=LEFT, pady=5)

btn_actualizar_com = ttk.Button(frame_puerto_com, text="🔄 Buscar", command=escanear_puertos, width=8)
btn_actualizar_com.pack(side=RIGHT, pady=5)

btn_conectar = ttk.Button(frame_comunicacion, text="Conectar Óhmetro", command=obtener_seleccion)
btn_conectar.pack(pady=5)

lbl_com = Label(frame_comunicacion, text="Esperando...", fg="black", bg="lightblue")
lbl_com.pack(pady=5)

lbl_id = Label(frame_comunicacion, text="ID: ", bg="lightblue")
lbl_id.pack(pady=5)

# ------------------------------------------ PANEL DE PLAY/PASUA/STOP
panel_control = Frame(panel_izquierdo, bg="lightgreen")
panel_control.pack(fill=X, padx=10, pady=10)

lbl_control = Label(panel_control, text="PLAY/PAUSE/STOP", bg="lightgreen")
lbl_control.pack(pady=5)
btn_play = ttk.Button(panel_control, text="▶️ Play", width=10, command=iniciar_grafica)
btn_play.pack(side=LEFT, padx=5)
btn_pause = ttk.Button(panel_control, text="⏸️ Pause", width=10, command=pausar_grafica)
btn_pause.pack(side=LEFT, padx=5)
btn_stop = ttk.Button(panel_control, text="⏹️ Stop", width=10, command=detener_grafica)
btn_stop.pack(side=LEFT, padx=5)

# ------------------------------------------ PANEL CONFIGURACION
panel_configuracion = Frame(panel_izquierdo, bg="lightyellow")
panel_configuracion.pack(fill=X, padx=10, pady=10)

lbl_configuracion = Label(panel_configuracion, text="CONFIGURACIÓN", bg="lightyellow")
lbl_configuracion.pack(pady=5)
channel1 = BooleanVar(value=False)
check1 = ttk.Checkbutton(panel_configuracion, text="Canal 1", variable=channel1, command=actualizar_canales)
check1.pack(pady=5)
channel2 = BooleanVar(value=False)
check2 = ttk.Checkbutton(panel_configuracion, text="Canal 2", variable=channel2, command=actualizar_canales)
check2.pack(pady=5)
channel3 = BooleanVar(value=False)
check3 = ttk.Checkbutton(panel_configuracion, text="Canal 3", variable=channel3, command=actualizar_canales)
check3.pack(pady=5)
channel4 = BooleanVar(value=False)
check4 = ttk.Checkbutton(panel_configuracion, text="Canal 4", variable=channel4, command=actualizar_canales)
check4.pack(pady=5)
channel5 = BooleanVar(value=False)
check5 = ttk.Checkbutton(panel_configuracion, text="Canal 5", variable=channel5, command=actualizar_canales)
check5.pack(pady=5)
channel6 = BooleanVar(value=False)
check6 = ttk.Checkbutton(panel_configuracion, text="Canal 6", variable=channel6, command=actualizar_canales)
check6.pack(pady=5)
# ==========================================
# SECCIÓN DERECHA: Área de la Gráfica
# ==========================================
panel_derecho = Frame(window, bg="white", relief=SUNKEN, borderwidth=2)
panel_derecho.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)

# 1. Crear la "Figura" y los "Ejes" usando Matplotlib
# figsize ajusta la proporción (ancho, alto), dpi es la resolución
fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
ax.set_title("Mediciones en Tiempo Real")
ax.set_xlabel("Muestras")
ax.set_ylabel("Valor")
ax.grid(True, linestyle='--', alpha=0.7)

y_data1 = []
y_data2 = []
y_data3 = []
y_data4 = []
y_data5 = []
y_data6 = []
x_data = []
MAX_PUNTOS = 50 
linea1, = ax.plot(x_data, y_data1, 'b-') 
linea2, = ax.plot(x_data, y_data2, 'g-') 
linea3, = ax.plot(x_data, y_data3, 'r-') 
linea4, = ax.plot(x_data, y_data4, 'c-') 
linea5, = ax.plot(x_data, y_data5, 'm-') 
linea6, = ax.plot(x_data, y_data6, 'y-') 

# Preparamos una línea vacía que luego podremos actualizar con datos
linea, = ax.plot([], [], lw=2, color='blue')
ax.set_xlim(0, 50)    # Rango inicial del eje X (ej. 50 muestras)
ax.set_ylim(-2, 7)  # Rango inicial del eje Y (ej. valores del ADC del Arduino)
ani = animation.FuncAnimation(fig, play, interval=100, cache_frame_data=False)


# 2. Convertir la figura en un widget de Tkinter
canvas = FigureCanvasTkAgg(fig, master=panel_derecho)
canvas.draw()

# 3. Extraer el widget y empaquetarlo dentro del panel_derecho
# fill=BOTH y expand=True hacen que la gráfica crezca si agrandas la ventana
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

# Escaneamos los puertos al arrancar
escanear_puertos()

# Ejecutar la GUI
window.mainloop()