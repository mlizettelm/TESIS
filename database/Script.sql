-- Crear la base de datos con una collation compatible
CREATE DATABASE IF NOT EXISTS tesis_db CHARACTER SET utf8 COLLATE utf8mb4_unicode_ci;
USE tesis_db;

-- Tabla datos_personales
CREATE TABLE datos_personales (
    id_paciente INT AUTO_INCREMENT PRIMARY KEY,  -- Llave primaria incremental
    nombre VARCHAR(255) NOT NULL,
    apellido_p VARCHAR(255) NOT NULL,
    apellido_m VARCHAR(255) NOT NULL,
    edad INT NOT NULL,
    sexo VARCHAR(50) NOT NULL,
    padecimiento VARCHAR(255) NOT NULL,
    grupo VARCHAR(100) NOT NULL,
    hemoglobina DECIMAL(5,2) NOT NULL,
    hematocrito DECIMAL(5,2) NOT NULL,
    observaciones TEXT,  -- Campo grande para texto
    clave_paciente VARCHAR(255) NULL  -- Acepta nulos
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci; -- Establecer collation para la tabla

-- Tabla imagenes
CREATE TABLE imagenes (
    id_img INT AUTO_INCREMENT PRIMARY KEY,  -- Llave primaria incremental
    id_paciente INT NOT NULL,  -- Llave foránea que hace referencia a la tabla datos_personales
    tipo VARCHAR(255) NOT NULL,
    ruta VARCHAR(500) NOT NULL,
    FOREIGN KEY (id_paciente) REFERENCES datos_personales(id_paciente)
        ON DELETE CASCADE  -- Si se borra un paciente, sus imágenes también se eliminan
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci; -- Establecer collation para la tabla

-- Tabla frecuencias
CREATE TABLE frecuencias (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Llave primaria incremental
    id_img INT NOT NULL,  -- Llave foránea que hace referencia a la tabla imagenes
    Red_x DECIMAL(10,6) NOT NULL,
    Red_y DECIMAL(10,6) NOT NULL,
    Green_x DECIMAL(10,6) NOT NULL,
    Green_y DECIMAL(10,6) NOT NULL,
    Blue_x DECIMAL(10,6) NOT NULL,
    Blue_y DECIMAL(10,6) NOT NULL,
    Gray_x DECIMAL(10,6) NOT NULL,
    Gray_y DECIMAL(10,6) NOT NULL,
    FOREIGN KEY (id_img) REFERENCES imagenes(id_img)
        ON DELETE CASCADE  -- Si se borra una imagen, sus frecuencias también se eliminan
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci; -- Establecer collation para la tabla

-- Crear un nuevo usuario con contraseña
CREATE USER 'python_db'@'localhost' IDENTIFIED BY 'PythonDB2024';

-- Otorgar todos los permisos sobre la base de datos tesis_db
GRANT ALL PRIVILEGES ON tesis_db.* TO 'python_db'@'localhost';

-- Aplicar los cambios
FLUSH PRIVILEGES;



