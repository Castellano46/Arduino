import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import threading
from rfid.RFID import recargar_datos, agregar_cliente_excel, eliminar_cliente_excel, manejar_acceso, iniciar_serial
import time

def leer_uid(callback):
    """Función para leer un UID del lector RFID de forma asíncrona."""
    def tarea_lectura():
        ser = iniciar_serial()
        if ser:
            time.sleep(2)
            while True:
                if ser.in_waiting > 0:
                    uid = ser.readline().decode('utf-8').strip()
                    if uid:
                        ser.close()
                        callback(uid)
                        return
                time.sleep(0.1)
        callback(None)

    hilo_lectura = threading.Thread(target=tarea_lectura)
    hilo_lectura.start()

def manejar_alta():
    """Función para manejar el proceso de alta de un nuevo usuario."""
    def aceptar_alta():
        nuevo_uid = entry_uid_var.get()
        nuevo_nombre = entry_nombre.get()
        if nuevo_uid and nuevo_nombre:
            df = recargar_datos()
            if df[df['UID'] == nuevo_uid].empty:
                nuevo_cliente = pd.DataFrame({'UID': [nuevo_uid], 'Nombre': [nuevo_nombre]})
                agregar_cliente_excel(nuevo_cliente)
                messagebox.showinfo("Alta", f"Nuevo UID registrado: {nuevo_uid} con el nombre: {nuevo_nombre}")
                ventana_alta.destroy()
            else:
                messagebox.showwarning("Error", f"UID {nuevo_uid} ya está registrado.")
                ventana_alta.destroy()

    def cancelar_alta():
        ventana_alta.destroy()

    def procesar_uid(uid):
        if uid:
            entry_uid_var.set(uid)
            entry_nombre.config(state='normal')
            btn_aceptar.config(state='normal')
            lbl_status.config(text="Tarjeta detectada. Ingrese el nombre del usuario.")
        else:
            messagebox.showerror("Error", "No se pudo leer el UID. Intente de nuevo.")
            ventana_alta.destroy()

    ventana_alta = tk.Toplevel(root)
    ventana_alta.title("Dar de alta")
    ventana_alta.geometry("400x200")

    lbl_instruccion = tk.Label(ventana_alta, text="Pase su tarjeta", font=("Arial", 12))
    lbl_instruccion.pack(pady=10)

    entry_uid_var = tk.StringVar()
    entry_uid = tk.Entry(ventana_alta, textvariable=entry_uid_var, state='readonly', justify='center', font=("Arial", 12))
    entry_uid.pack(pady=10)

    lbl_nombre = tk.Label(ventana_alta, text="Nombre del usuario:", font=("Arial", 12))
    lbl_nombre.pack(pady=10)

    entry_nombre = tk.Entry(ventana_alta, state='disabled', justify='center', font=("Arial", 12))
    entry_nombre.pack(pady=10)

    lbl_status = tk.Label(ventana_alta, text="Esperando lectura de tarjeta...", font=("Arial", 10))
    lbl_status.pack(pady=5)

    btn_aceptar = tk.Button(ventana_alta, text="Aceptar", state='disabled', command=aceptar_alta)
    btn_aceptar.pack(side='left', padx=20, pady=20)

    btn_cancelar = tk.Button(ventana_alta, text="Cancelar", command=cancelar_alta)
    btn_cancelar.pack(side='right', padx=20, pady=20)

    leer_uid(procesar_uid)

def manejar_baja():
    def procesar_uid_baja(uid):
        if uid:
            resultado = eliminar_cliente_excel(uid)
            messagebox.showinfo("Baja", resultado)
        else:
            messagebox.showerror("Error", "No se pudo leer el UID. Intente de nuevo.")

    leer_uid(procesar_uid_baja)

def mostrar_clientes():
    df_clientes = recargar_datos()
    df_registros = pd.read_excel('registros.xlsx', sheet_name='Registros')

    ventana_clientes = tk.Toplevel(root)
    ventana_clientes.title("Clientes y Registros")
    ventana_clientes.geometry("800x600")

    estilo = ttk.Style()
    estilo.configure("Treeview.Heading", font=("Arial", 10, "bold"))
    estilo.configure("Treeview", rowheight=25)

    tabla_clientes = ttk.Treeview(ventana_clientes, columns=("UID", "Nombre"), show='headings', style="Treeview")
    tabla_clientes.heading("UID", text="UID")
    tabla_clientes.heading("Nombre", text="Nombre")
    
    tabla_clientes.column("UID", anchor="center")
    tabla_clientes.column("Nombre", anchor="center")
    
    tabla_clientes.pack(fill=tk.BOTH, expand=True)

    for _, row in df_clientes.iterrows():
        tabla_clientes.insert("", tk.END, values=(row["UID"], row["Nombre"]))

    tabla_registros = ttk.Treeview(ventana_clientes, columns=("FECHA-HORA", "UID", "NOMBRE", "ESTADO", "ENTRADA-SALIDA"), show='headings', style="Treeview")
    tabla_registros.heading("FECHA-HORA", text="Fecha y Hora")
    tabla_registros.heading("UID", text="UID")
    tabla_registros.heading("NOMBRE", text="Nombre")
    tabla_registros.heading("ESTADO", text="Estado")
    tabla_registros.heading("ENTRADA-SALIDA", text="Entrada/Salida")

    tabla_registros.column("FECHA-HORA", anchor="center")
    tabla_registros.column("UID", anchor="center")
    tabla_registros.column("NOMBRE", anchor="center")
    tabla_registros.column("ESTADO", anchor="center")
    tabla_registros.column("ENTRADA-SALIDA", anchor="center")
    
    tabla_registros.pack(fill=tk.BOTH, expand=True)

    for _, row in df_registros.iterrows():
        tabla_registros.insert("", tk.END, values=(row["FECHA-HORA"], row["UID"], row["NOMBRE"], row["ESTADO"], row["ENTRADA-SALIDA"]))

root = tk.Tk()
root.title("Sistema de Control de Acceso")
root.geometry("500x400")

label_bienvenida = tk.Label(root, text="Bienvenido a estética Mari, donde tú eres lo primero", font=("Arial", 14))
label_bienvenida.pack(pady=20)

btn_alta = tk.Button(root, text="Dar de alta", command=manejar_alta)
btn_alta.pack(pady=10)

btn_baja = tk.Button(root, text="Dar de baja", command=manejar_baja)
btn_baja.pack(pady=10)

btn_ver_clientes = tk.Button(root, text="Ver clientes y registros", command=mostrar_clientes)
btn_ver_clientes.pack(pady=10)

hilo_acceso = threading.Thread(target=manejar_acceso)
hilo_acceso.daemon = True
hilo_acceso.start()

root.mainloop()
