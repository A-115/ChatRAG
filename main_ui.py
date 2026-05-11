import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                            QFileDialog, QLabel, QListWidget)
from PySide6.QtCore import Qt
from database_manager import insertar_mensaje_db, inicializar_datos_prueba  # Eliminar inicializar_datos_prueba en producción, es solo para pruebas iniciales

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI RAG Assistant - Prototipo")
        self.resize(800, 600)
        inicializar_datos_prueba()  # Llenar la base de datos con datos de prueba (eliminar en producción)

        # Widget Principal
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout_principal = QHBoxLayout(self.main_widget)

        # --- Panel Lateral (Opciones) ---
        self.panel_lateral = QVBoxLayout()
        self.lbl_archivo = QLabel("Archivo: Ninguno")
        self.btn_cargar = QPushButton("Cargar Documento (PDF/TXT)")
        self.btn_exportar = QPushButton("Exportar JSON/XML")
        
        self.panel_lateral.addWidget(self.lbl_archivo)
        self.panel_lateral.addWidget(self.btn_cargar)
        self.panel_lateral.addStretch() # Empuja los botones hacia arriba
        self.panel_lateral.addWidget(self.btn_exportar)

        # --- Área de Chat ---
        self.layout_chat = QVBoxLayout()
        self.area_visualizacion = QTextEdit()
        self.area_visualizacion.setReadOnly(True)
        
        self.layout_entrada = QHBoxLayout()
        self.campo_texto = QLineEdit()
        self.campo_texto.setPlaceholderText("Escribe tu pregunta aquí...")
        self.btn_enviar = QPushButton("Enviar")
        
        self.layout_entrada.addWidget(self.campo_texto)
        self.layout_entrada.addWidget(self.btn_enviar)

        self.layout_chat.addWidget(self.area_visualizacion)
        self.layout_chat.addLayout(self.layout_entrada)

        # Unir todo
        self.layout_principal.addLayout(self.panel_lateral, 1)
        self.layout_principal.addLayout(self.layout_chat, 3)

        # Conexiones (Slots)
        self.btn_cargar.clicked.connect(self.seleccionar_archivo)
        self.btn_enviar.clicked.connect(self.enviar_mensaje)

    def seleccionar_archivo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "", "Archivos (*.pdf *.txt)")
        if file_path:
            nombre = file_path.split("/")[-1]
            self.lbl_archivo.setText(f"Archivo: {nombre}")

    def enviar_mensaje(self):
        texto = self.campo_texto.text()
        if texto:
            self.area_visualizacion.append(f"<b>Usuario:</b> {texto}")
            self.campo_texto.clear()
            #por el momento sera 1 como ID de conversación fijo, luego se implementará la lógica para manejar múltiples conversaciones
            insertar_mensaje_db(1, "Usuario", texto)
            # Aquí conectarás con el OrquestadorRAG después
            self.area_visualizacion.append("<b>Sistema:</b> <i>Procesando...</i>")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())