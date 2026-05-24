import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QStackedWidget)
from src.ui.login_window import LoginWindow
from src.ui.register_window import RegisterWindow
from src.ui.chat_window import ChatWindow
from database.database_manager import inicializar_base_de_datos

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI RAG Assistant - Prototipo") # Cambiar el titulo para mostrar el nombre del chatbot
        self.resize(800, 600)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        #Iniciar las ventanas
        self.vista_login = LoginWindow()
        self.vista_register = RegisterWindow()
        self.vista_chat = ChatWindow()

        #Agregar las ventanas al stack
        self.stack.addWidget(self.vista_login)  # Índice 0
        self.stack.addWidget(self.vista_register)  # Índice 1
        self.stack.addWidget(self.vista_chat)  # Índice 2

        #Conectar señales para navegar entre ventanas
        self.vista_login.btn_registrar.clicked.connect(self.mostrar_registro)
        self.vista_register.btn_volver.clicked.connect(self.mostrar_login)
        self.vista_login.login_exitoso.connect(self.mostrar_chat)  # Conectar la señal de login exitoso a la función que muestra la vista de chat
        self.vista_chat.btn_logout.clicked.connect(self.cerrar_sesion)  # Botón para cerrar sesión y volver al login    

    def mostrar_registro(self):
        self.stack.setCurrentWidget(self.vista_register)
    def mostrar_login(self):
        self.stack.setCurrentWidget(self.vista_login)
    def mostrar_chat(self, id_usuario, correo):
        self.vista_chat.id_usuario_actual = id_usuario
        self.vista_chat.correo_usuario = correo
        primera_letra = correo[0].upper()
        
        # El círculo azul se queda con la letra pura y perfectamente centrada
        self.vista_chat.lbl_icono_perfil.setText(primera_letra)
        
        # El texto se queda solo con el correo
        self.vista_chat.lbl_usuario.setText(correo)
        
        self.stack.setCurrentWidget(self.vista_chat)
        print(f"Sesión iniciada para el usuario: {correo} (ID: {id_usuario})")

    # Función para cerrar sesión y volver al login
    def cerrar_sesion(self):
        # Limpiar cualquier estado relacionado con la sesión actual si es necesario
        self.vista_chat.id_usuario_actual = None
        self.vista_chat.correo_usuario = "No identificado"
        self.vista_chat.id_conversacion_actual = None
        self.vista_chat.chunk_documento =[]

        #Reiniciar la interfaz visual del chat
        self.vista_chat.lbl_archivo.setText("📄 Archivo: Ninguno")
        self.vista_chat.lbl_usuario.setText(f"👤 {self.vista_chat.correo_usuario}")
        self.vista_chat.limpiar_pantalla_chat()

        #Limpiar los campos de texto
        self.vista_login.input_correo.clear()
        self.vista_login.input_password.clear()

        self.mostrar_login()
        print("Sesión cerrada. Volviendo al login.")

if __name__ == "__main__":
    inicializar_base_de_datos()  # Crea las tablas si no existen
    app = QApplication(sys.argv)
    # --- ESTILO GLOBAL PARA ALERTAS Y MENSAJES (QMessageBox)
    app.setStyleSheet("""
        QMessageBox {
            background-color: #252526;
            border: 1px solid #3c3c3c;
        }
        QMessageBox QLabel {
            color: #f5f5f5;
            font-size: 13px;
            font-family: 'Segoe UI', Arial;
        }
        QMessageBox QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 6px 15px;
            border-radius: 4px;
            font-weight: bold;
            min-width: 60px;
        }
        QMessageBox QPushButton:hover {
            background-color: #106ebe;
        }
    """)
    ventana_principal = MainWindow()
    ventana_principal.show()
    sys.exit(app.exec())
