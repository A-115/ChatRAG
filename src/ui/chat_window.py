import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, 
                            QHBoxLayout, QLineEdit, QPushButton, 
                            QFileDialog, QLabel, QTextEdit, QApplication)
from PySide6.QtCore import Qt, QThread, Signal
from database.database_manager import insertar_mensaje_db
from src.logic.ia_engine import procesar_pregunta_ia
from src.logic.document_processor import extraer_texto_pdf, dividir_texto_en_chunks, encontrar_mejores_chunks

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.chunk_documento = []  # Variable para almacenar los chunks del texto extraído del documento

        self.layout_principal = QHBoxLayout(self)

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
        self.btn_cargar.clicked.connect(self.seleccionar_archivo)
        self.btn_enviar.clicked.connect(self.enviar_mensaje)


    def enviar_mensaje(self):
        texto = self.campo_texto.text()
        if texto:
            self.area_visualizacion.append(f"<b>Usuario:</b> {texto}")
            self.campo_texto.clear()
            #por el momento sera 1 como ID de conversación fijo, luego se implementará la lógica para manejar múltiples conversaciones
            insertar_mensaje_db(1, "Usuario", texto)
            # Aquí conectarás con el OrquestadorRAG después
            self.area_visualizacion.append("<b>Sistema:</b> <i>Procesando...</i>")
            self.campo_texto.setEnabled(False)  # Deshabilitar el campo de texto mientras la IA procesa la pregunta

            self.worker = IAThread(texto, self.chunk_documento) 
            self.worker.respuesta_recibida.connect(self.mostrar_respuesta_ia)
            self.worker.start()


    def mostrar_respuesta_ia(self, respuesta):
        self.area_visualizacion.append(f"<b>Sistema:</b> {respuesta}")
        self.campo_texto.setEnabled(True)  # Volver a habilitar el campo de texto después de recibir la respuesta
        self.campo_texto.setFocus()  # Enfocar el campo de texto para que el usuario pueda escribir la siguiente pregunta


    def seleccionar_archivo(self):
        #Funcion para abrir el buscador de archivos y extraer el texto del PDF seleccionado
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "", "Archivos (*.pdf *.txt)")
        if file_path:
            nombre = file_path.split("/")[-1]
            self.lbl_archivo.setText(f"Archivo: {nombre}")
            contenido_extraido = extraer_texto_pdf(file_path)

            if contenido_extraido:
                self.chunk_documento = dividir_texto_en_chunks(contenido_extraido)  # Dividir el texto en chunks para su procesamiento
                self.area_visualizacion.append(f"<b>Sistema:</b> Documento '{nombre}' cargado exitosamente.")
            else:
                self.area_visualizacion.append(f"<b>Sistema:</b> Error al cargar el documento '{nombre}'.")



#Ejecutar el procesamiento de la IA en un hilo separado para evitar bloquear la interfaz
#Si se ejecuta directamente en el hilo principal, la interfaz se congelará durante el tiempo que la IA esté "pensando"
#Al usar QThread, la interfaz seguirá siendo responsiva y se actualizará con la respuesta de la IA una vez que esté lista
class IAThread(QThread):
    respuesta_recibida = Signal(str)

    def __init__(self, pregunta, chunks=None):
        super().__init__()
        self.pregunta = pregunta
        self.chunks = chunks if chunks is not None else []

    def run(self):
        mejor_contexto = encontrar_mejores_chunks(self.pregunta, self.chunks)  
        respuesta = procesar_pregunta_ia(self.pregunta, mejor_contexto)
        insertar_mensaje_db(1, "Sistema", respuesta)  # Guardar la respuesta de la IA en la base de datos
        self.respuesta_recibida.emit(respuesta)




    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())