import cv2

for i in range(4):  # Prueba desde 0 hasta 3
    cap = cv2.VideoCapture(i)

    if not cap.isOpened():
        print(f"Error: No se pudo abrir la cámara en /dev/video{i}.")
        continue

    print(f"Cámara abierta en /dev/video{i}. Presiona 'q' para salir.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo leer el frame.")
            break

        cv2.imshow(f'Video en /dev/video{i}', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
