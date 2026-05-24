import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                                QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QHBoxLayout)
from PySide6.QtCore import Qt
from database.database_manager import registrar_usuario

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Activa el pintado de fondo para toda la ventana
        self.setAttribute(Qt.WA_StyledBackground, True)

        # --- LAYOUT MAESTRO (Para centrar la tarjeta) ---
        self.layout_maestro = QVBoxLayout(self)
        self.layout_maestro.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # =========================================================================
        # --- TARJETA DE REGISTRO ---
        # =========================================================================
        self.tarjeta_registro = QFrame()
        self.tarjeta_registro.setObjectName("tarjetaRegistro")
        self.tarjeta_registro.setFixedWidth(400) 
        
        layout = QVBoxLayout(self.tarjeta_registro)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(12)

        # --- Títulos ---
        self.lbl_title = QLabel("Crear Cuenta")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f5f5f5;")
        layout.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel("Únete a Cuervos Negros Salvajes")
        self.lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_subtitle.setStyleSheet("font-size: 14px; color: #a19f9d; margin-bottom: 10px;")
        layout.addWidget(self.lbl_subtitle)

        # --- Campo de Correo ---
        self.lbl_correo = QLabel("Correo Electrónico")
        self.lbl_correo.setStyleSheet("color: #f5f5f5; font-weight: bold; font-size: 13px;")
        self.input_correo = QLineEdit()
        self.input_correo.setPlaceholderText("ejemplo@udg.mx")
        self.input_correo.setObjectName("inputCustom")
        layout.addWidget(self.lbl_correo)
        layout.addWidget(self.input_correo)

# --- Contraseña ---
        self.lbl_password = QLabel("Contraseña")
        self.lbl_password.setStyleSheet("color: #f5f5f5; font-weight: bold; font-size: 13px;")
        layout.addWidget(self.lbl_password)

        self.layout_pwd = QHBoxLayout()
        self.layout_pwd.setSpacing(5)
        
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Crea tu contraseña")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password) 
        self.input_password.setObjectName("inputCustom")
        self.layout_pwd.addWidget(self.input_password)

        self.btn_ver_pwd = QPushButton("👁️")
        self.btn_ver_pwd.setObjectName("btnOjo")
        self.btn_ver_pwd.setFixedSize(40, 40)
        self.btn_ver_pwd.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ver_pwd.clicked.connect(self.toggle_password)
        self.layout_pwd.addWidget(self.btn_ver_pwd)
        
        layout.addLayout(self.layout_pwd)

        # --- Confirmar Contraseña ---
        self.lbl_confirm_password = QLabel("Confirmar Contraseña")
        self.lbl_confirm_password.setStyleSheet("color: #f5f5f5; font-weight: bold; font-size: 13px;")
        layout.addWidget(self.lbl_confirm_password)

        self.layout_confirm = QHBoxLayout()
        self.layout_confirm.setSpacing(5)

        self.input_confirm_password = QLineEdit()
        self.input_confirm_password.setPlaceholderText("Repite tu contraseña")
        self.input_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirm_password.setObjectName("inputCustom")
        self.layout_confirm.addWidget(self.input_confirm_password)

        self.btn_ver_confirm = QPushButton("👁️")
        self.btn_ver_confirm.setObjectName("btnOjo")
        self.btn_ver_confirm.setFixedSize(40, 40)
        self.btn_ver_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ver_confirm.clicked.connect(self.toggle_confirm_password)
        self.layout_confirm.addWidget(self.btn_ver_confirm)

        layout.addLayout(self.layout_confirm)

        # --- Botón de Registro ---
        self.btn_registrar = QPushButton("Crear Cuenta")
        self.btn_registrar.setObjectName("btnExito")
        self.btn_registrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_registrar.clicked.connect(self.procesar_registro)
        self.input_confirm_password.returnPressed.connect(self.procesar_registro)
        self.input_password.returnPressed.connect(self.procesar_registro)
        self.input_correo.returnPressed.connect(self.procesar_registro)
        layout.addWidget(self.btn_registrar)

        # --- Botón Volver ---
        self.btn_volver = QPushButton("¿Ya tienes cuenta? Inicia sesión")
        self.btn_volver.setFlat(True)
        self.btn_volver.setObjectName("btnEnlace")
        self.btn_volver.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_volver)

        self.layout_maestro.addWidget(self.tarjeta_registro)

        # =========================================================================
        # --- ESTILOS MODERNOS CSS ---
        # =========================================================================
        self.setStyleSheet("""
            RegisterWindow {
                background-color: #1e1e1e;
                font-family: 'Segoe UI', Arial;
            }
            QFrame#tarjetaRegistro {
                background-color: #252526;
                border-radius: 12px;
                border: 1px solid #3c3c3c;
            }
            QLineEdit#inputCustom {
                background-color: #333337;
                border: 1px solid #434346;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton#btnOjo {
                background-color: #333337;
                border: 1px solid #434346;
                color: white;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton#btnOjo:hover {
                background-color: #505050;
            }
            QLineEdit#inputCustom:focus {
                border: 1px solid #28a745;
            }
            QPushButton#btnExito {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px;
                margin-top: 10px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#btnExito:hover {
                background-color: #218838;
            }
            QPushButton#btnEnlace {
                color: #0078d4;
                margin-top: 5px;
                font-size: 13px;
                text-decoration: underline;
            }
            QPushButton#btnEnlace:hover {
                color: #4da6ff;
            }
        """)

    def procesar_registro(self):
        correo = self.input_correo.text().strip()
        password = self.input_password.text().strip()
        confirm_password = self.input_confirm_password.text().strip()

        if not correo or not password or not confirm_password:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos.")
            return
            
        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
            return
        
        exito, mensaje = registrar_usuario(correo, password)
        if exito:
            QMessageBox.information(self, "Éxito", "Usuario registrado exitosamente. Ahora puedes iniciar sesión.")
            self.input_correo.clear()
            self.input_password.clear()
            self.input_confirm_password.clear()
            # Opcional: Podrías hacer que al registrarse exitosamente vuelva al login automático simulando un clic
            self.btn_volver.click()
        else:
            QMessageBox.warning(self, "Error", mensaje)
    
    def toggle_password(self):
        if self.input_password.echoMode() == QLineEdit.EchoMode.Password:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_ver_pwd.setText("🔒")
        else:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_ver_pwd.setText("👁️")
        
    def toggle_confirm_password(self):
        if self.input_confirm_password.echoMode() == QLineEdit.EchoMode.Password:
            self.input_confirm_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_ver_confirm.setText("🔒")
        else:
            self.input_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_ver_confirm.setText("👁️")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_registro = RegisterWindow()
    ventana_registro.show()
    sys.exit(app.exec())