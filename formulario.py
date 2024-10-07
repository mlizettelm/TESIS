import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import cv2
import os
from PIL import Image, ImageTk
import time
import pymysql  # Asegúrate de que este módulo esté instalado

from config import DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE


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

# Función para insertar datos en la tabla "datos_personales"
def insert_data(nombre, apellido_p, apellido_m, edad, sexo, padecimiento, grupo, hemoglobina, hematocrito, clave_paciente):
    connection = None  # Inicializar la variable de conexión
    try:
        # Establecer la conexión con el charset utf8mb4
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # Consulta para insertar datos
            insert_query = """
            INSERT INTO datos_personales (nombre, apellido_p, apellido_m, edad, sexo, padecimiento, grupo, hemoglobina, hematocrito, clave_paciente)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            data_tuple = (nombre, apellido_p, apellido_m, edad, sexo, padecimiento, grupo, hemoglobina, hematocrito, clave_paciente)

            # Ejecutar la consulta
            cursor.execute(insert_query, data_tuple)
            connection.commit()  # Confirmar cambios

            # Obtener el ID de la inserción
            inserted_id = cursor.lastrowid

            print(f"Datos insertados correctamente. ID de la inserción: {inserted_id}")
            return inserted_id  # Devolver el ID del registro insertado

    except pymysql.Error as err:
        print(f"Error al insertar datos: {err}")
        return None  # Devolver None en caso de error

    finally:
        if connection:
            connection.close()  # Cerrar la conexión
# Función para mostrar el resumen de datos
def show_summary():
    nombre = nombre_entry.get()
    apellido_p = apellido_p_entry.get()
    apellido_m = apellido_m_entry.get()
    edad = edad_entry.get()
    sexo = sexo_combo.get()
    padecimiento = padecimiento_combo.get()
    grupo = grupo_combo.get()
    hemoglobina = hemoglobina_entry.get()
    hematocrito = hematocrito_entry.get()
    clave_clinica = clave_clinica_entry.get()
    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not all([nombre, apellido_p, apellido_m, edad, sexo, padecimiento, grupo, hemoglobina, hematocrito]):
        messagebox.showerror("Error", "Por favor, completa todos los campos requeridos.")
        return

    summary = (
        f"Nombre: {nombre}\n"
        f"Apellido Paterno: {apellido_p}\n"
        f"Apellido Materno: {apellido_m}\n"
        f"Edad: {edad}\n"
        f"Sexo: {sexo}\n"
        f"Padecimiento: {padecimiento}\n"
        f"Grupo: {grupo}\n"
        f"Hemoglobina: {hemoglobina}\n"
        f"Hematocrito: {hematocrito}\n"
        f"Clave Clínica: {clave_clinica}\n"
        f"Fecha y Hora: {fecha_hora}"
    )

    result = messagebox.askquestion("Resumen de Datos", summary + "\n¿Deseas confirmar o editar?")
    
    if result == 'yes':
        id_paciente = insert_data(nombre, apellido_p, apellido_m, edad, sexo, padecimiento, grupo, hemoglobina, hematocrito, clave_clinica)
        global user_id
        if id_paciente is not None:
            user_id = id_paciente  # Asignar el ID del paciente a la variable global
            print(f"ID del paciente: {id_paciente}")
            print("Valor de user_id:", user_id) 
            messagebox.showinfo("Éxito", f"Datos insertados correctamente. ID del paciente: {id_paciente}")
            photos_total, interval = getParametrosDB()
            #imprimir los valores de photos_total e interval
            print(photos_total, interval)
            if photos_total is not None and interval is not None:
                start_camera('uña', photos_total, interval, id_paciente) 
        else:
            messagebox.showerror("Error", "No se pudo insertar los datos en la base de datos.")
    else:
        messagebox.showinfo("Edición", "Puedes editar los datos en el formulario.")

def insert_images_to_db(image_names, user_id):
    connection = None
    try:
        # Establecer la conexión con la base de datos
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Insertar los nombres de las imágenes en la tabla 'imagenes'
            insert_query = """
                INSERT INTO imagenes (id_paciente, tipo, ruta)
                VALUES (%s, %s, %s)
            """
            
            # Recorrer el array de nombres de imágenes
            for image_name in image_names:
                # Obtener el tipo (phase) de la imagen a partir del nombre del archivo
                tipo = image_name.split('_')[0]  # Esto asume que el tipo es la primera parte antes del "_"
                ruta = f"{photo_folder}/{image_name}"  # Construir la ruta completa de la imagen
                
                # Ejecutar la consulta de inserción
                cursor.execute(insert_query, (user_id, tipo, ruta))
            
            # Confirmar los cambios en la base de datos
            connection.commit()
            print(f"Se insertaron {len(image_names)} imágenes en la base de datos para el usuario ID {user_id}.")
    
    except pymysql.Error as err:
        print(f"Error al insertar las imágenes en la base de datos: {err}")
    
    finally:
        if connection:
            connection.close()  # Cerrar la conexión

# Función para obtener las cámaras disponibles
def get_available_cameras():
    cameras = []
    for i in range(10): 
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cameras.append((str(i), f"Cámara {i}"))
            cap.release()
    return cameras

# Variables globales
cap = None
camera_frame = None
capture_index = 0
total_captures = 10
capture_timer = None
photo_folder = "Fotos"
form_window = None  # Mover la definición de form_window aquí
preview_window = None
user_id = ""
image_names = []

# Función para mostrar la vista previa de la cámara
def show_camera_preview(camera_index):
    global camera_frame, cap

    cap = cv2.VideoCapture(int(camera_index))

    camera_frame = tk.Frame(preview_window)
    camera_frame.pack()

    img_label = tk.Label(camera_frame)
    img_label.pack()

    def update_frame():
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))

            img = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(image=img)

            img_label.img_tk = img_tk
            img_label.config(image=img_tk)
            
        camera_frame.after(10, update_frame)

    update_frame()


def getParametrosDB():
    connection = None
    try:
        # Establecer la conexión con el charset utf8mb4
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # Consulta para obtener el primer registro de la tabla "tiempo"
            select_query = "SELECT num_fotos, intervalo FROM tiempo LIMIT 1"
            cursor.execute(select_query)
            result = cursor.fetchone()  # Obtener el primer registro

            if result:
                return result['num_fotos'], result['intervalo']
            else:
                print("No se encontraron registros en la tabla 'tiempo'.")
                return None, None

    except pymysql.Error as err:
        print(f"Error al obtener parámetros de la base de datos: {err}")
        return None, None  # Devolver None en caso de error

    finally:
        if connection:
            connection.close()  # Cerrar la conexión


def start_camera(phase, photos_total, interval, id_user):
    # Retirar la ventana de formulario en lugar de destruir
    if form_window is not None and form_window.winfo_exists():
        form_window.withdraw()  # Ocultar la ventana del formulario

    global preview_window
    preview_window = tk.Tk()
    preview_window.title("Vista Previa de Cámara")
    
    # Establecer un estilo para la ventana
    preview_window.configure(bg="#f0f0f0")
    
    tk.Label(preview_window, text="Selecciona la cámara:", bg="#f0f0f0", font=("Arial", 12)).pack(padx=5, pady=5)
    
    cameras = get_available_cameras()
    camera_combo = ttk.Combobox(preview_window, values=[name for _, name in cameras])
    camera_combo.pack(padx=5, pady=5)
    camera_combo.current(0)

    preview_button = tk.Button(preview_window, text="Vista Previa", command=lambda: show_camera_preview(cameras[camera_combo.current()][0]), bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))

    preview_button.pack(pady=10)

    # Etiquetas para mostrar información
    tk.Label(preview_window, text=f"ID de usuario: {id_user}", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
    tk.Label(preview_window, text=f"Número de fotos: {photos_total}", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
    tk.Label(preview_window, text=f"Intervalo entre fotos: {interval} segundos", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
    tk.Label(preview_window, text=f"Captura de {phase.capitalize()}", bg="#f0f0f0", font=("Arial", 14, "bold")).pack(pady=10)

    global progress_bar
    progress_bar = ttk.Progressbar(preview_window, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)

    # Iniciar captura pasando los parámetros photos_total e interval
    start_button = tk.Button(preview_window, text="Iniciar", command=lambda: start_capture(camera_combo.get().split()[1], phase, photos_total, interval), bg="#008CBA", fg="white", font=("Arial", 10, "bold"))
    start_button.pack(pady=10)

    preview_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(preview_window))

    preview_window.mainloop()

def on_closing(preview_window):
    # Asegúrate de liberar recursos de la cámara y cerrar correctamente
    if cap is not None:
        cap.release()
    preview_window.destroy()
    form_window.deiconify()  # Mostrar nuevamente la ventana del formulario

# Función para iniciar la captura de fotos
def start_capture(camera_index, phase, photos_total, interval):
    global capture_index, total_captures, capture_timer

    os.makedirs(photo_folder, exist_ok=True)
    capture_index = 0
    progress_bar['maximum'] = photos_total  # Ajustar barra de progreso al total de fotos
    progress_bar['value'] = 0

    messagebox.showinfo("Captura", f"Iniciando captura de fotos de {phase} con cámara {camera_index}.")

    capture_timer = time.time()
    capture_photos(camera_index, phase, photos_total, interval)  # Pasar los nuevos parámetros

# Función para capturar fotos
# Función para capturar fotos
def capture_photos(camera_index, phase, photos_total, interval):
    global capture_index, cap, capture_timer, preview_window, camera_frame, image_names

    if capture_index < photos_total:  # Controlar con el total de fotos
        ret, frame = cap.read()
        if ret:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            photo_name = f"{phase}_{timestamp}_{capture_index + 1}.jpg"
            photo_path = os.path.join(photo_folder, photo_name)
            cv2.imwrite(photo_path, frame)

            # Agregar el nombre de la imagen al array
            image_names.append(photo_name)

            capture_index += 1
            progress_bar['value'] = capture_index

            # Usar `interval` para determinar el tiempo de espera entre capturas
            preview_window.after(interval * 1000, lambda: capture_photos(camera_index, phase, photos_total, interval))
        else:
            messagebox.showerror("Error", "No se pudo leer el frame de la cámara.")
    else:
        # Captura finalizada, liberar la cámara y eliminar la vista previa
        cap.release()
        if camera_frame:
            camera_frame.destroy()  # Asegurarse de que camera_frame sea destruido

        # Preguntar si desea guardar las fotos o descartarlas
        ask_to_save_photos(phase, photos_total, interval, user_id)

def ask_to_save_photos(phase, photos_total, interval, user_id,):
    result = messagebox.askquestion("Fotos Capturadas", "¿Deseas guardar las fotos?")
    
    if result == 'yes':
        messagebox.showinfo("Guardado", "Las fotos han sido guardadas exitosamente.")
        if phase == 'uña':
            # Aquí puedes cerrar la ventana de la cámara de la uña
            preview_window.destroy()  # Cierra la ventana de la cámara de la uña
            # Iniciar la captura de yema
            start_camera('yema', photos_total, interval, user_id)   # Lanza la cámara para la yema
        else:
            #imprimir id del usuario
            print("Valor de user_id:", user_id)
            insert_images_to_db(image_names, user_id)
            messagebox.showinfo("Proceso Completo", "Capturas completadas. Puedes cerrar la aplicación.")
            on_capture_complete()
        
    else:
        messagebox.showinfo("Descartado", "Las fotos han sido descartadas.")
        # Dejar la ventana abierta para volver a tomar las fotos
        # Puedes usar el mismo `phase` para volver a iniciar la captura
        start_camera(phase, photos_total, interval, user_id)

def reset_form():
    nombre_entry.delete(0, tk.END)
    apellido_p_entry.delete(0, tk.END)
    apellido_m_entry.delete(0, tk.END)
    edad_entry.delete(0, tk.END)
    sexo_combo.set('')  # Reiniciar el combo de selección
    padecimiento_combo.set('')
    grupo_combo.set('')
    hemoglobina_entry.delete(0, tk.END)
    hematocrito_entry.delete(0, tk.END)
    clave_clinica_entry.delete(0, tk.END)


def on_capture_complete():
    # Restablecer el formulario
    reset_form()

    # Cerrar la ventana de vista previa y restaurar el formulario
    preview_window.destroy()  # Cierra la ventana de vista previa
    form_window.deiconify()  # Muestra nuevamente el formulario


# Crear la ventana del formulario
form_window = tk.Tk()
form_window.title("Formulario de Datos Personales")

# Labels y entradas
tk.Label(form_window, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
nombre_entry = tk.Entry(form_window)
nombre_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form_window, text="Apellido Paterno:").grid(row=1, column=0, padx=5, pady=5)
apellido_p_entry = tk.Entry(form_window)
apellido_p_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(form_window, text="Apellido Materno:").grid(row=2, column=0, padx=5, pady=5)
apellido_m_entry = tk.Entry(form_window)
apellido_m_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(form_window, text="Edad:").grid(row=3, column=0, padx=5, pady=5)
edad_entry = tk.Entry(form_window)
edad_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Label(form_window, text="Sexo:").grid(row=4, column=0, padx=5, pady=5)
sexo_combo = ttk.Combobox(form_window, values=["Masculino", "Femenino"])
sexo_combo.grid(row=4, column=1, padx=5, pady=5)

tk.Label(form_window, text="Padecimiento:").grid(row=5, column=0, padx=5, pady=5)
padecimiento_combo = ttk.Combobox(form_window, values=["Daño renal", "Ninguno"])
padecimiento_combo.grid(row=5, column=1, padx=5, pady=5)

tk.Label(form_window, text="Grupo:").grid(row=6, column=0, padx=5, pady=5)
grupo_combo = ttk.Combobox(form_window, values=["Anemia", "Control"])
grupo_combo.grid(row=6, column=1, padx=5, pady=5)

tk.Label(form_window, text="Hemoglobina:").grid(row=7, column=0, padx=5, pady=5)
hemoglobina_entry = tk.Entry(form_window)
hemoglobina_entry.grid(row=7, column=1, padx=5, pady=5)

tk.Label(form_window, text="Hematocrito:").grid(row=8, column=0, padx=5, pady=5)
hematocrito_entry = tk.Entry(form_window)
hematocrito_entry.grid(row=8, column=1, padx=5, pady=5)

tk.Label(form_window, text="Clave Clínica:").grid(row=9, column=0, padx=5, pady=5)
clave_clinica_entry = tk.Entry(form_window)
clave_clinica_entry.grid(row=9, column=1, padx=5, pady=5)

#mostra imagen de la camara
camera_group = tk.LabelFrame(form_window, text="Prueba de Cámara", padx=10, pady=10)
camera_group.grid(row=11, columnspan=2, padx=10, pady=10, sticky="we")


# Botón para mostrar el resumen
submit_button = tk.Button(form_window, text="Confirmar Datos", command=show_summary)
submit_button.grid(row=10, columnspan=2, pady=10)

form_window.mainloop()
