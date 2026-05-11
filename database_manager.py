import sqlite3

#Funcion para abrir la base de datos y cerrarla
def insertar_mensaje_db(id_conversacion, emisor, texto):
    conexion = sqlite3.connect("chatbot_rag.db")
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO Mensajes (ID_Conversacion, Emisor, Texto) VALUES (?, ?, ?)", #los signos de interrogacion son placeholders para evitar inyecciones SQL
        (id_conversacion, emisor, texto)
    )
    conexion.commit()
    conexion.close()

    print(f"Mensaje de {emisor} guardado exitosamente en la base de datos.")


#Prueba para ver si la conexion a la base de datos funciona correctamente
def inicializar_datos_prueba():
    conexion = sqlite3.connect("chatbot_rag.db")
    cursor = conexion.cursor()

    # 1. Creamos un usuario de prueba si no hay ninguno
    cursor.execute("SELECT COUNT(*) FROM Usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO Usuarios (Correo, Password_Hash) VALUES (?, ?)",
            ("test@udg.mx", "hash_prueba")
        )
        print("Usuario de prueba creado.")

    # 2. Creamos una conversación de prueba si no hay ninguna
    cursor.execute("SELECT COUNT(*) FROM Conversaciones")
    if cursor.fetchone()[0] == 0:
        # Nota: Usamos ID_Usuario = 1 porque es el que acabamos de crear arriba
        cursor.execute(
            "INSERT INTO Conversaciones (ID_Usuario, Nombre_Archivo) VALUES (?, ?)",
            (1, "documento_demo.pdf")
        )
        print("Conversación de prueba creada.")

    conexion.commit()
    conexion.close()