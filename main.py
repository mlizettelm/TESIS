import tkinter as tk
from tkinter import ttk, messagebox
import pymysql  # Cambiado a pymysql
import cv2
import threading
from PIL import Image, ImageTk
import datetime
import subprocess
import os

from config import DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE

# Establecer la conexión con el charset utf8mb4
cnx = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_DATABASE,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# Variable global para la cámara
cap = None

# Función para probar la conexión a la base de datos
def test_db_connection():
    try:
        with cnx.cursor() as cursor:
            cursor.execute("SELECT 1")  # Probar una consulta simple
            messagebox.showinfo("Conexión Exitosa", "Se ha conectado correctamente a la base de datos")
    except pymysql.Error as err:  # Cambiado a pymysql.Error
        messagebox.showerror("Error de Conexión", f"Error: {err}")

# Función para crear la tabla "tiempo" si no existe
def create_table():
    try:
        with cnx.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tiempo (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    num_fotos INT NOT NULL,
                    tiempo_total INT NOT NULL,
                    intervalo INT NOT NULL
                )
            """)
        cnx.commit()
    except pymysql.Error as err:
        messagebox.showerror("Error", f"Error al crear la tabla: {err}")

# Función para insertar o actualizar los valores en la tabla "tiempo"
def update_tiempo(num_fotos, tiempo_total, intervalo):
    try:
        with cnx.cursor() as cursor:
            # Verificamos si existe un registro
            cursor.execute("SELECT COUNT(*) AS count FROM tiempo")
            result = cursor.fetchone()

            if result['count'] > 0:
                # Si existe, realizar la actualización
                cursor.execute("""
                    UPDATE tiempo
                    SET num_fotos = %s, tiempo_total = %s, intervalo = %s
                    WHERE id = 1
                """, (num_fotos, tiempo_total, intervalo))
                messagebox.showinfo("Actualización Exitosa", "Los datos se han actualizado correctamente.")
            else:
                # Si no existe, realizar la inserción
                cursor.execute("""
                    INSERT INTO tiempo (num_fotos, tiempo_total, intervalo)
                    VALUES (%s, %s, %s)
                """, (num_fotos, tiempo_total, intervalo))
                messagebox.showinfo("Inserción Exitosa", "Los datos se han insertado correctamente.")
        
        cnx.commit()  # Confirmar cambios

    except pymysql.Error as err:
        messagebox.showerror("Error", f"Error al insertar o actualizar la tabla: {err}")

# Aquí puedes seguir con el resto de tu código...


# Función para actualizar el video de la cámara en el label
def update_camera_feed(cap, video_label):
    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "No se pudo capturar el video. Verifica la cámara.")
            break
        
        # Convertir la imagen de OpenCV a un formato compatible con Tkinter
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk  # Guardar referencia para evitar recolección de basura
        video_label.config(image=imgtk)

        # Añadir un pequeño retraso
        video_label.update()
        cv2.waitKey(1)  # Esperar 1 ms

# Función para obtener cámaras disponibles y sus nombres
def get_available_cameras():
    cameras = []
    for i in range(10):  # Probar hasta 10 índices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cameras.append((str(i), f"Cámara {i}"))  # Agregar el índice y nombre de la cámara
            cap.release()  # Liberar la cámara después de comprobar
    return cameras

# Función para seleccionar la cámara y mostrar la vista previa
def test_camera():
    global cap  # Declarar la variable cap como global
    selected_camera = camera_combo.get().split(' - ')[0]  # Obtener solo el índice
    try:
        cap = cv2.VideoCapture(int(selected_camera))  # Convertir a entero para usar como índice de cámara
        if not cap.isOpened():
            messagebox.showerror("Error", "No se pudo acceder a la cámara seleccionada. Intenta con otra cámara.")
            return
        
        # Crear una ventana para mostrar el feed con tamaño reducido
        video_label = tk.Label(camera_group, width=320, height=240)
        video_label.grid(row=2, columnspan=2, pady=10)
        
        # Lanzar un hilo para actualizar el video
        threading.Thread(target=update_camera_feed, args=(cap, video_label), daemon=True).start()

    except Exception as e:
        messagebox.showerror("Error", f"Error al acceder a la cámara: {str(e)}")

# Función para mostrar los valores de configuración y liberar la cámara
def save_configuration():
    global cap  # Declarar la variable cap como global
    try:
        # Asignar valores predeterminados si los campos están vacíos
        num_photos = int(num_photos_entry.get() or 10)  # Default 10 photos
        total_time_minutes = int(total_time_entry.get() or 1)  # Default 1 minute
        total_time_seconds = total_time_minutes * 60  # Convertir a segundos
        interval_seconds = total_time_seconds // num_photos  # Calcular el intervalo entre fotos

        selected_camera = camera_combo.get()  # Guardar el dispositivo de cámara seleccionado

        messagebox.showinfo(
            "Configuración Guardada", 
            f"Cámara seleccionada: {selected_camera}\nCantidad de Fotos: {num_photos}\n"
            f"Tiempo total: {total_time_minutes} minutos\nIntervalo entre fotos: {interval_seconds} segundos"
        )

        # Actualizar la tabla "tiempo" con los nuevos valores
        update_tiempo(num_photos, total_time_seconds, interval_seconds)

        # Liberar la cámara si está abierta
        if cap is not None and cap.isOpened():
            cap.release()
            cap = None  # Reiniciar la variable cap

        # Habilitar el botón "Continuar" después de guardar la configuración
        continue_button.config(state=tk.NORMAL)

    except ValueError:
        messagebox.showerror("Error", "Por favor, introduce números válidos en los campos.")

# Función para continuar con el siguiente paso
def continue_action():
    # Ejecutar el segundo archivo que contiene el formulario
    subprocess.Popen(['python', 'formulario.py'])
    
    # Cerrar la ventana principal después de ejecutar el formulario
    #root.destroy()

# Crear la ventana principal
if __name__ == "__main__":
    root = tk.Tk()
    
    root.title("App de Pruebas")
    root.configure(bg='#003366')

    # Crear la tabla en la base de datos
    create_table()

    # GroupBox 1: Test de conexión a la base de datos
    db_group = tk.LabelFrame(root, text="Test de Conexión a la DB", padx=10, pady=10)
    db_group.pack(padx=10, pady=10, fill="both", expand="yes")

    # Botón para probar la conexión
    db_test_button = tk.Button(db_group, text="Probar Conexión", command=test_db_connection)
    db_test_button.grid(row=0, columnspan=2, pady=10)

    # GroupBox 2: Prueba de cámara
    camera_group = tk.LabelFrame(root, text="Prueba de Cámara", padx=10, pady=10)
    camera_group.pack(padx=10, pady=10, fill="both", expand="yes")

    tk.Label(camera_group, text="Selecciona Cámara:").grid(row=0, column=0, padx=5, pady=5)

    # Obtener cámaras disponibles y agregar al combo box
    available_cameras = get_available_cameras()
    camera_combo = ttk.Combobox(camera_group, values=[f"{index} - {name}" for index, name in available_cameras])
    camera_combo.grid(row=0, column=1, padx=5, pady=5)
    camera_combo.current(0)

    camera_test_button = tk.Button(camera_group, text="Probar Cámara", command=test_camera)
    camera_test_button.grid(row=1, columnspan=2, pady=10)

    # GroupBox 3: Configuración
    config_group = tk.LabelFrame(root, text="Configuración de Captura", padx=10, pady=10)
    config_group.pack(padx=10, pady=10, fill="both", expand="yes")

    tk.Label(config_group, text="Cantidad de Fotos:").grid(row=0, column=0, padx=5, pady=5)
    num_photos_entry = tk.Entry(config_group)
    num_photos_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(config_group, text="Tiempo Total (minutos):").grid(row=1, column=0, padx=5, pady=5)
    total_time_entry = tk.Entry(config_group)
    total_time_entry.grid(row=1, column=1, padx=5, pady=5)

    save_button = tk.Button(config_group, text="Guardar Configuración", command=save_configuration)
    save_button.grid(row=2, columnspan=2, pady=10)

    # Botón "Continuar", inicialmente deshabilitado
    continue_button = tk.Button(root, text="Continuar", state=tk.DISABLED, command=continue_action)
    continue_button.pack(pady=20)

    # Iniciar el loop de la aplicación
    root.mainloop()

    # Cerrar la conexión al finalizar la aplicación
    cnx.close()
