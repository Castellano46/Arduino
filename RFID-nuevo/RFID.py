import pandas as pd
import serial
import time
import openpyxl
import os

excel_file = os.path.join(os.getcwd(), 'clientes.xlsx')
sheet_name = 'Hoja1'

def recargar_datos():
    global df
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name, engine='openpyxl')
    except FileNotFoundError:
        print(f"Archivo {excel_file} no encontrado.")
        exit()

# Agregar un nuevo cliente al archivo Excel
def agregar_cliente_excel(nuevo_cliente):
    try:
        book = openpyxl.load_workbook(excel_file)
        sheet = book[sheet_name]

        startrow = sheet.max_row

        for row in nuevo_cliente.itertuples(index=False, name=None):
            sheet.append(row)

        book.save(excel_file)
        print("Cliente agregado exitosamente.")
    except Exception as e:
        print(f"Error al agregar cliente al archivo Excel: {e}")
        exit()

# Eliminar un cliente del archivo Excel
def eliminar_cliente_excel(uid):
    global df
    try:
        df = df[df['UID'] != uid]

        # Guardar los cambios en el Excel
        df.to_excel(excel_file, sheet_name=sheet_name, index=False, engine='openpyxl')
        print(f"Cliente con UID {uid} eliminado exitosamente.")
    except Exception as e:
        print(f"Error al eliminar cliente del archivo Excel: {e}")
        exit()

recargar_datos()

# Conectar al puerto serie
try:
    ser = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)
except serial.SerialException as e:
    print(f"Error al conectar con el puerto serie: {e}")
    exit()

# UID maestro
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

                # Verificar si el UID ya existe en la base de datos
                if buscar_nombre_por_uid(nuevo_uid) is not None:
                    ser.write(f"UID ya registrado: {nuevo_uid}\n".encode('utf-8'))
                    print(f"Error: El UID {nuevo_uid} ya está registrado.")
                else:
                    # Solicitar nombre del nuevo usuario
                    nuevo_nombre = input("Ingrese el nombre del nuevo usuario: ")

                    # Agregar nuevo UID y nombre al archivo Excel
                    nuevo_cliente = pd.DataFrame({'UID': [nuevo_uid], 'Nombre': [nuevo_nombre]})
                    agregar_cliente_excel(nuevo_cliente)

                    # Notificar que el UID se ha registrado
                    ser.write(f"Nuevo UID registrado: {nuevo_uid}\n".encode('utf-8'))
                    print(f"Nuevo UID registrado: {nuevo_uid} con el nombre: {nuevo_nombre}")
                    
                    recargar_datos()

            elif "Baja UID:" in uid:
                uid_a_borrar = uid.split(":")[1].strip()
                print(f"Solicitud de eliminación de UID: {uid_a_borrar}")

                # Verificar si el UID existe en la base de datos
                if buscar_nombre_por_uid(uid_a_borrar) is None:
                    ser.write(f"UID no encontrado: {uid_a_borrar}\n".encode('utf-8'))
                    print(f"Error: El UID {uid_a_borrar} no está registrado.")
                else:
                    # Eliminar el UID del Excel
                    eliminar_cliente_excel(uid_a_borrar)

                    # Notificar que el UID se ha eliminado
                    ser.write(f"UID eliminado: {uid_a_borrar}\n".encode('utf-8'))
                    print(f"UID eliminado: {uid_a_borrar}")
                    
                    recargar_datos()

            elif uid == master_uid:
                ser.write(f"Acceso permitido\n".encode('utf-8'))
                print("Acceso permitido al UID maestro")
            else:
                recargar_datos()

                nombre = buscar_nombre_por_uid(uid)
                if nombre is not None:
                    # Mensaje personalizado a Arduino
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
