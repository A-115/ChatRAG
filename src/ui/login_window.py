import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                                QLabel, QLineEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Qt, Signal
from database.database_manager import validar_login

class LoginWindow(QWidget):

    login_exitoso = Signal(int)  # Señal personalizada para indicar que el login fue exitoso

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login") # Cambiar el titulo para mostrar el nombre del chatbot
        self.resize(350, 450)

        #Layout principal
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #Titulo
        self.lbl_title = QLabel("Bienvenido al sistema") # Cambiar el titulo para mostrar el nombre del chatbot
        self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(self.lbl_title)

        #Campo de correo
        self.lbl_correo = QLabel("Correo:")
        self.input_correo = QLineEdit()
        self.input_correo.setPlaceholderText("Ingresa tu correo")
        layout.addWidget(self.lbl_correo)
        layout.addWidget(self.input_correo)

        #Campo de contraseña
        self.lbl_password = QLabel("Contraseña:")
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Ingresa tu contraseña")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password) # Oculta el texto ingresado para la contraseña
        layout.addWidget(self.lbl_password)
        layout.addWidget(self.input_password)

        #Boton de login
        self.btn_ingresar = QPushButton("Ingresar")
        self.btn_ingresar.setStyleSheet("background-color: #2b5797; color: white; padding: 8px; margin-top: 15px; border-radius: 4px;")
        #Conectar el boton a la funcion de login
        self.btn_ingresar.clicked.connect(self.procesar_login)
        layout.addWidget(self.btn_ingresar)

        #Enlace a registro
        self.btn_registrar = QPushButton("¿No tienes una cuenta? Regístrate")
        self.btn_registrar.setFlat(True)
        self.btn_registrar.setStyleSheet("color: #0078D7; text-decoration: underline;")
        layout.addWidget(self.btn_registrar)

        self.setLayout(layout)

    def procesar_login(self):
        #Se ejecuta al hacer click en el boton de ingresar, valida el login utilizando la funcion del database_manager
        correo = self.input_correo.text().strip()
        password = self.input_password.text().strip()

        # Validar que no esten vacios
        if not correo or not password:
            QMessageBox.warning(self, "Error", "Por favor, ingresa tu correo y contraseña.")
            return
        
        # Llamar a la función de validación de login del database_manager
        exito, mensaje, id_usuario = validar_login(correo, password)
        if exito:
            QMessageBox.information(self, "Éxito", "¡Login exitoso!")
            self.login_exitoso.emit(id_usuario)  # Emitir la señal de login exitoso con el ID del usuario
            self.input_correo.clear()  # Limpiar el campo de correo
            self.input_password.clear()  # Limpiar el campo de contraseña

            # Aquí podrías abrir la ventana principal de tu aplicación después del login exitoso
        else:
            QMessageBox.warning(self, "Error de acceso", mensaje)

#Prueba de la ventana de login
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_login = LoginWindow()
    ventana_login.show()
    sys.exit(app.exec())