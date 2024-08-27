import pandas as pd
import serial
import time
import openpyxl
import os

excel_file = 'clientes.xlsx'
sheet_name = 'Hoja1'

def cargar_datos():
    try:
        return pd.read_excel(excel_file, sheet_name=sheet_name, engine='openpyxl')
    except FileNotFoundError:
        print(f"Archivo {excel_file} no encontrado.")
        exit()

df = cargar_datos()

def agregar_cliente_excel(nuevo_cliente):
    book = openpyxl.load_workbook(excel_file)
    sheet = book[sheet_name]

    for row in nuevo_cliente.itertuples(index=False, name=None):
        sheet.append(row)

    book.save(excel_file)
    print("Cliente agregado exitosamente.")

def eliminar_cliente_excel(uid):
    global df
    df = df[df['UID'] != uid]
    df.to_excel(excel_file, sheet_name=sheet_name, index=False, engine='openpyxl')
    print(f"Cliente con UID {uid} eliminado exitosamente.")

ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)

master_uid = "5363f0757101"

def buscar_nombre_por_uid(uid):
    cliente = df[df['UID'] == uid]
    if not cliente.empty:
        return cliente.iloc[0]['Nombre']
    return None

try:
    while True:
        if ser.in_waiting > 0:
            uid = ser.readline().decode('utf-8').strip()

            if "Alta UID:" in uid:
                nuevo_uid = uid.split(":")[1].strip()
                print(f"Nuevo UID detectado: {nuevo_uid}")

                if buscar_nombre_por_uid(nuevo_uid) is not None:
                    ser.write(f"UID ya registrado: {nuevo_uid}\n".encode('utf-8'))
                    print(f"Error: El UID {nuevo_uid} ya está registrado.")
                else:
                    nuevo_nombre = input("Ingrese el nombre del nuevo usuario: ")
                    nuevo_cliente = pd.DataFrame({'UID': [nuevo_uid], 'Nombre': [nuevo_nombre]})
                    agregar_cliente_excel(nuevo_cliente)
                    ser.write(f"Nuevo UID registrado: {nuevo_uid}\n".encode('utf-8'))
                    print(f"Nuevo UID registrado: {nuevo_uid} con el nombre: {nuevo_nombre}")
                    df = cargar_datos()

            elif "Baja UID:" in uid:
                uid_a_borrar = uid.split(":")[1].strip()
                print(f"Solicitud de eliminación de UID: {uid_a_borrar}")

                if buscar_nombre_por_uid(uid_a_borrar) is None:
                    ser.write(f"UID no encontrado: {uid_a_borrar}\n".encode('utf-8'))
                    print(f"Error: El UID {uid_a_borrar} no está registrado.")
                else:
                    eliminar_cliente_excel(uid_a_borrar)
                    ser.write(f"UID eliminado: {uid_a_borrar}\n".encode('utf-8'))
                    print(f"UID eliminado: {uid_a_borrar}")
                    df = cargar_datos()

            else:
                nombre = buscar_nombre_por_uid(uid)
                if nombre is not None:
                    ser.write(f"Acceso permitido a: {nombre}\n".encode('utf-8'))
                    print(f"Acceso permitido a: {nombre}")
                else:
                    ser.write("Acceso denegado\n".encode('utf-8'))
                    print(f"Acceso denegado para UID: {uid}")

except KeyboardInterrupt:
    print("Script interrumpido.")
finally:
    ser.close()
    print("Puerto serie cerrado.")
