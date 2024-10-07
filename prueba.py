import pymysql

# Establecer la conexión con el charset utf8mb4
cnx = pymysql.connect(
    host='localhost',
    user='python_db',
    password='PythonDB2024',
    database='tesis_db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# Crear un cursor
with cnx.cursor() as cursor:
    # Ejecutar una consulta
    cursor.execute("SHOW TABLES")
    result = cursor.fetchall()
    
    # Imprimir los resultados
    for row in result:
        print(row)

# Cerrar la conexión
cnx.close()
