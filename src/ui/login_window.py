import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                                QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from database.database_manager import validar_login

class LoginWindow(QWidget):
    # Emitimos el ID y el Correo para que el chat los reciba
    login_exitoso = Signal(int, str)  

    def __init__(self):
        super().__init__()
        # Activa el pintado de fondo para toda la ventana (evita marcos blancos)
        self.setAttribute(Qt.WA_StyledBackground, True)

        # --- LAYOUT MAESTRO (Para centrar la tarjeta en la pantalla) ---
        self.layout_maestro = QVBoxLayout(self)
        self.layout_maestro.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # =========================================================================
        # --- TARJETA DE LOGIN (CONTENEDOR CENTRAL) ---
        # =========================================================================
        self.tarjeta_login = QFrame()
        self.tarjeta_login.setObjectName("tarjetaLogin")
        # Esto evita que los campos se estiren por toda la pantalla de 800px
        self.tarjeta_login.setFixedWidth(400) 
        
        layout = QVBoxLayout(self.tarjeta_login)
        layout.setContentsMargins(35, 40, 35, 40)
        layout.setSpacing(15)

        # --- Ícono o Logo ---
        self.lbl_icono = QLabel("🦅") # Cuervo/Águila como logo del equipo
        self.lbl_icono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_icono.setStyleSheet("font-size: 50px; margin-bottom: 5px;")
        layout.addWidget(self.lbl_icono)

        # --- Títulos ---
        self.lbl_title = QLabel("Cuervos Negros Salvajes")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f5f5f5;")
        layout.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel("Inicia sesión en tu cuenta")
        self.lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_subtitle.setStyleSheet("font-size: 14px; color: #a19f9d; margin-bottom: 15px;")
        layout.addWidget(self.lbl_subtitle)

        # --- Campo de Correo ---
        self.lbl_correo = QLabel("Correo Electrónico")
        self.lbl_correo.setStyleSheet("color: #f5f5f5; font-weight: bold; font-size: 13px;")
        self.input_correo = QLineEdit()
        self.input_correo.setPlaceholderText("ejemplo@gmail.com")
        self.input_correo.setObjectName("inputCustom")
        layout.addWidget(self.lbl_correo)
        layout.addWidget(self.input_correo)

        # --- Campo de Contraseña ---
        self.lbl_password = QLabel("Contraseña")
        self.lbl_password.setStyleSheet("color: #f5f5f5; font-weight: bold; font-size: 13px;")
        layout.addWidget(self.lbl_password)

        self.layout_pwd = QHBoxLayout()
        self.layout_pwd.setSpacing(8)
        self.layout_pwd.setContentsMargins(0, 0, 0, 0)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Ingresa tu contraseña")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password) 
        self.input_password.setObjectName("inputCustom")
        self.layout_pwd.addWidget(self.input_password)

        self.btn_ver_pwd = QPushButton("👁️")
        self.btn_ver_pwd.setObjectName("btnVerPassword")
        self.btn_ver_pwd.setFixedSize(40, 40)
        self.btn_ver_pwd.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ver_pwd.clicked.connect(self.toggle_password)
        self.layout_pwd.addWidget(self.btn_ver_pwd)

        layout.addLayout(self.layout_pwd)

        # --- Botón de Ingresar ---
        self.btn_ingresar = QPushButton("Ingresar")
        self.btn_ingresar.setObjectName("btnPrimario")
        self.btn_ingresar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.input_correo.returnPressed.connect(self.procesar_login)
        self.input_password.returnPressed.connect(self.procesar_login)
        self.btn_ingresar.clicked.connect(self.procesar_login)
        layout.addWidget(self.btn_ingresar)

        # --- Enlace a Registro ---
        self.btn_registrar = QPushButton("¿No tienes una cuenta? Regístrate")
        self.btn_registrar.setFlat(True)
        self.btn_registrar.setObjectName("btnEnlace")
        self.btn_registrar.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_registrar)

        # Insertamos la tarjeta armada al layout maestro para que quede centrada
        self.layout_maestro.addWidget(self.tarjeta_login)

        # =========================================================================
        # --- ESTILOS MODERNOS CSS ---
        # =========================================================================
        self.setStyleSheet("""
            LoginWindow {
                background-color: #1e1e1e;
                font-family: 'Segoe UI', Arial;
            }
            QFrame#tarjetaLogin {
                background-color: #252526;
                border-radius: 12px;
                border: 1px solid #3c3c3c;
            }
            QLineEdit#inputCustom {
                background-color: #333337;
                border: 1px solid #434346;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton#btnVerPassword {
                background-color: #333337;
                border: 1px solid #434346;
                color: white;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton#btnVerPassword:hover {
                background-color: #505050;
            }
            QLineEdit#inputCustom:focus {
                border: 1px solid #0078d4;
            }
            QPushButton#btnPrimario {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 14px;
                margin-top: 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#btnPrimario:hover {
                background-color: #106ebe;
            }
            QPushButton#btnEnlace {
                color: #0078d4;
                margin-top: 10px;
                font-size: 13px;
                text-decoration: underline;
            }
            QPushButton#btnEnlace:hover {
                color: #4da6ff;
            }
        """)

    def procesar_login(self):
        correo = self.input_correo.text().strip()
        password = self.input_password.text().strip()

        if not correo or not password:
            QMessageBox.warning(self, "Campos incompletos", "Por favor, ingresa tu correo y contraseña.")
            return
        
        exito, mensaje, id_usuario = validar_login(correo, password)
        if exito:
            # Emitimos el ID y el Correo real
            self.login_exitoso.emit(id_usuario, correo)  
            self.input_correo.clear()  
            self.input_password.clear()  
        else:
            QMessageBox.warning(self, "Error de acceso", mensaje)

    def toggle_password(self):
        if self.input_password.echoMode() == QLineEdit.EchoMode.Password:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_ver_pwd.setText("🔒")
        else:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_ver_pwd.setText("👁️")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_login = LoginWindow()
    ventana_login.show()
    sys.exit(app.exec())