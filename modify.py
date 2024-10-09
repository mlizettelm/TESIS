import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading


# Función para mostrar la vista previa de la cámara en una ventana nueva
def show_camera_preview(camera_index):
    def update_frame():
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))

            img = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(image=img)

            img_label.img_tk = img_tk  # Mantener referencia para evitar que se elimine
            img_label.config(image=img_tk)

        img_label.after(10, update_frame)

    global cap
    cap = cv2.VideoCapture(int(camera_index))

    # Crear una nueva ventana para la vista previa
    preview_window = tk.Toplevel()
    preview_window.title("Vista Previa de la Cámara")
    
    img_label = tk.Label(preview_window)
    img_label.pack()

    update_frame()


# Función para iniciar la cámara desde el formulario principal
def start_camera_preview():
    selected_camera = camera_combo.get().split(' - ')[0]  # Obtener índice de la cámara seleccionada
    if selected_camera.isdigit():
        threading.Thread(target=show_camera_preview, args=(selected_camera,), daemon=True).start()
    else:
        messagebox.showerror("Error", "Selecciona una cámara válida.")


# Función para obtener las cámaras disponibles
def get_available_cameras():
    cameras = []
    for i in range(10):  # Probar los primeros 10 índices de cámaras
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cameras.append((str(i), f"Cámara {i}"))
            cap.release()
    return cameras


# Crear la ventana principal
root = tk.Tk()
root.title("Formulario Principal")

# Grupo de la cámara
camera_group = tk.Frame(root)
camera_group.pack(padx=10, pady=10)

tk.Label(camera_group, text="Selecciona la cámara:").grid(row=0, column=0)

# Obtener las cámaras disponibles
cameras = get_available_cameras()
camera_combo = ttk.Combobox(camera_group, values=[name for _, name in cameras])
camera_combo.grid(row=0, column=1)
camera_combo.current(0)

# Botón para iniciar la vista previa
preview_button = tk.Button(camera_group, text="Iniciar Vista Previa", command=start_camera_preview)
preview_button.grid(row=1, column=0, columnspan=2, pady=10)

# Mantener la ventana principal en ejecución
root.mainloop()
