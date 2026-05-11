import sqlite3

conexion = sqlite3.connect('chatbot_rag.db')
cursor = conexion.cursor()

#Creación de la tabla para los usuarios.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Usuarios (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Correo TEXT NOT NULL UNIQUE,
        Password_Hash TEXT NOT NULL
    )
''')


#Creación de la tabla para las conversaciones.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Conversaciones (
        ID_Conversación INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Usuario INTEGER NOT NULL,
        Nombre_Archivo TEXT NOT NULL,
        FOREIGN KEY (ID_Usuario) REFERENCES Usuarios(ID)
    )
''')


# Creación de la tabla para los mensajes.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Mensajes (
        ID_Mensaje INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Conversacion INTEGER NOT NULL,
        Emisor TEXT NOT NULL,
        Texto TEXT NOT NULL,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ID_Conversacion) REFERENCES Conversaciones(ID_Conversacion)
    )
''')

#Se guardan los cambios de la base de datos y se cierra la conexión.
conexion.commit()
conexion.close()
print("Base de datos creada exitosamente.")