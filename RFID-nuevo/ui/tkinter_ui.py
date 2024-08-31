import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import threading
from rfid.RFID import recargar_datos, agregar_cliente_excel, eliminar_cliente_excel, manejar_acceso

def manejar_alta():
    nuevo_uid = simpledialog.askstring("Alta", "Escanee la tarjeta para dar de alta:")
    if nuevo_uid:
        df = recargar_datos()
        if df[df['UID'] == nuevo_uid].empty:
            nuevo_nombre = simpledialog.askstring("Alta", "Ingrese el nombre del nuevo usuario:")
            if nuevo_nombre:
                nuevo_cliente = pd.DataFrame({'UID': [nuevo_uid], 'Nombre': [nuevo_nombre]})
                agregar_cliente_excel(nuevo_cliente)
                messagebox.showinfo("Alta", f"Nuevo UID registrado: {nuevo_uid} con el nombre: {nuevo_nombre}")
        else:
            messagebox.showwarning("Error", f"UID {nuevo_uid} ya está registrado.")

def manejar_baja():
    uid_a_borrar = simpledialog.askstring("Baja", "Escanee la tarjeta para dar de baja:")
    if uid_a_borrar:
        resultado = eliminar_cliente_excel(uid_a_borrar)
        messagebox.showinfo("Baja", resultado)

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
