import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QStackedWidget)
from src.ui.login_window import LoginWindow
from src.ui.register_window import RegisterWindow
from src.ui.chat_window import ChatWindow

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

    def mostrar_registro(self):
        self.stack.setCurrentWidget(self.vista_register)
    def mostrar_login(self):
        self.stack.setCurrentWidget(self.vista_login)
    def mostrar_chat(self):
        self.stack.setCurrentWidget(self.vista_chat)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_principal = MainWindow()
    ventana_principal.show()
    sys.exit(app.exec())