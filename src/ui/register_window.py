import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                                QLabel, QLineEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Qt
from database.database_manager import registrar_usuario

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro") # Cambiar el titulo para mostrar el nombre del chatbot
        self.resize(350, 450)

        #Layout principal
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #Titulo
        self.lbl_title = QLabel("Crea tu cuenta")
        self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(self.lbl_title)

        #Campo de correo
        self.lbl_correo = QLabel("Correo:")
        self.input_correo = QLineEdit()
        self.input_correo.setPlaceholderText("Ingresa tu correo")
        layout.addWidget(self.lbl_correo)
        layout.addWidget(self.input_correo)

        #Contraseña
        self.lbl_password = QLabel("Contraseña:")
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Crea tu contraseña")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password) # Oculta el texto ingresado para la contraseña
        layout.addWidget(self.lbl_password)
        layout.addWidget(self.input_password)

        #Confirmar contraseña
        self.lbl_confirm_password = QLabel("Confirmar Contraseña:")
        self.input_confirm_password = QLineEdit()
        self.input_confirm_password.setPlaceholderText("Confirma tu contraseña")
        self.input_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.lbl_confirm_password)
        layout.addWidget(self.input_confirm_password)

        #Boton de registro
        self.btn_registrar = QPushButton("Crear Cuenta")
        self.btn_registrar.setStyleSheet("background-color: #28a745; color: white; padding: 8px; margin-top: 15px; border-radius: 4px;")
        self.btn_registrar.clicked.connect(self.procesar_registro)
        layout.addWidget(self.btn_registrar)


        #Boton de registro
        self.btn_volver = QPushButton("¿Ya tienes cuenta? Inicia sesión")
        self.btn_volver.setFlat(True)
        self.btn_volver.setStyleSheet("color: #0078D7; text-decoration: underline;")
        layout.addWidget(self.btn_volver)

        self.setLayout(layout)

    
    def procesar_registro(self):
        #Se ejecuta al hacer click en el boton de registrar, valida el registro utilizando la funcion del database_manager
        correo = self.input_correo.text().strip()
        password = self.input_password.text().strip()
        confirm_password = self.input_confirm_password.text().strip()

        # Validar que no esten vacios
        if not correo or not password or not confirm_password:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos.")
            return
        # Validar que las contraseñas coincidan
        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
            return
        
        # Se guarda en la base de datos
        exito, mensaje = registrar_usuario(correo, password)
        if exito:
            QMessageBox.information(self, "Exito", "Usuario registrado exitosamente. Ahora puedes iniciar sesión.")
            # Limpiar los campos
            self.input_correo.clear()
            self.input_password.clear()
            self.input_confirm_password.clear()
        else:
            QMessageBox.warning(self, "Error", mensaje)

#Prueba de la ventana de registro
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_registro = RegisterWindow()
    ventana_registro.show()
    sys.exit(app.exec())
