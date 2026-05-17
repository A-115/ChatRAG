import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, 
                            QHBoxLayout, QLineEdit, QPushButton, 
                            QFileDialog, QLabel, QTextEdit, QApplication)
from PySide6.QtCore import Qt, QThread, Signal
from database.database_manager import crear_conversacion_db, insertar_mensaje_db, obtener_conversacion_por_archivo, obtener_mensajes_db
from src.logic.ia_engine import procesar_pregunta_ia
from src.logic.document_processor import extraer_texto_pdf, dividir_texto_en_chunks, encontrar_mejores_chunks

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.chunk_documento = []  # Variable para almacenar los chunks del texto extraído del documento

        self.id_usuario_actual = 1 
        self.id_conversacion_actual = None

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
        #Si no hay conversacion activa, no se permite enviar mensajes
        if not self.id_conversacion_actual:
            self.area_visualizacion.append("<b>Sistema:</b> Por favor, carga un documento para iniciar la conversación.")
            return
        
        texto = self.campo_texto.text()
        if texto:
            self.area_visualizacion.append(f"<b>Usuario:</b> {texto}")
            self.campo_texto.clear()

            insertar_mensaje_db(self.id_conversacion_actual, "Usuario", texto)
            # Aquí conectarás con el OrquestadorRAG después
            self.area_visualizacion.append("<b>Sistema:</b> <i>Procesando...</i>")
            self.campo_texto.setEnabled(False)  # Deshabilitar el campo de texto mientras la IA procesa la pregunta

            self.worker = IAThread(texto, self.chunk_documento, self.id_conversacion_actual)
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
                id_conv_existente = obtener_conversacion_por_archivo(self.id_usuario_actual, nombre)  # Verificar si ya existe una conversación para este archivo y usuario
                if id_conv_existente:
                    self.id_conversacion_actual = id_conv_existente
                    self.area_visualizacion.append(f"<b>Sistema:</b> Continuando conversación con el documento '{nombre}'.")
                    self.cargar_historial_visual(self.id_conversacion_actual)  # Cargar el historial de la conversación en la interfaz
                else:
                    id_conv_nuevo = crear_conversacion_db(self.id_usuario_actual, nombre)  # Crear una nueva conversación en la base de datos para este documento
                    if id_conv_nuevo:
                        self.id_conversacion_actual = id_conv_nuevo
                        self.area_visualizacion.clear()  # Limpiar el área de visualización para la nueva conversación
                        self.area_visualizacion.append(f"<b>Sistema:</b> Nueva conversación iniciada con el documento '{nombre}'")
                    else:
                        self.area_visualizacion.append(f"<b>Sistema:</b> Error al crear la conversación en la base de datos para el documento '{nombre}'.")                  
            else:
                self.area_visualizacion.append(f"<b>Sistema:</b> Error al cargar el documento '{nombre}'.")


    def cargar_historial_visual(self, id_conversacion):
        #Descarga los mensajes de la conversación desde la base de datos y los muestra en el área de visualización
        self.area_visualizacion.clear()
        self.area_visualizacion.append(f"<b>Sistema:</b> <i>Cargando historial de la conversación...</i>")

        #Se trae el historial de mensajes desde la base de datos utilizando la función obtener_mensajes_db
        historial = obtener_mensajes_db(id_conversacion)

        self.area_visualizacion.clear()  # Limpiar el mensaje de "Cargando historial" después de obtener los mensajes
        if historial:
            for fila in historial:
                fila_lista = list(fila)  # Convertir la tupla a lista para facilitar el acceso a los elementos
                if "Usuario" in fila_lista:
                    remitente = "Usuario"
                    texto = fila_lista[fila_lista.index("Usuario") + 1]
                elif "Sistema" in fila_lista:
                    remitente = "Sistema"
                    texto = fila_lista[fila_lista.index("Sistema") + 1]
                else:
                    # Si no se encuentra el remitente, se asigna un valor por defecto
                    remitente = fila[0] 
                    texto = fila[1]
                
                if remitente == "Usuario":
                    self.area_visualizacion.append(f"<b>Usuario:</b> {texto}")
                else:
                    self.area_visualizacion.append(f"<b>Sistema:</b> {texto}")
                
            self.area_visualizacion.append(f"<b>Sistema:</b> Historial cargado. Puedes continuar la conversación.")
        else:
            self.area_visualizacion.append(f"<b>Sistema:</b> No se encontraron mensajes en el historial de esta conversación.")


#Ejecutar el procesamiento de la IA en un hilo separado para evitar bloquear la interfaz
#Si se ejecuta directamente en el hilo principal, la interfaz se congelará durante el tiempo que la IA esté "pensando"
#Al usar QThread, la interfaz seguirá siendo responsiva y se actualizará con la respuesta de la IA una vez que esté lista
class IAThread(QThread):
    respuesta_recibida = Signal(str)

    def __init__(self, pregunta, chunks=None, id_conversacion=None):
        super().__init__()
        self.pregunta = pregunta
        self.chunks = chunks if chunks is not None else []
        self.id_conversacion_actual = id_conversacion  #Se guarda el id de la conversación para poder insertar la respuesta de la IA en la base de datos

    def run(self):
        mejor_contexto = encontrar_mejores_chunks(self.pregunta, self.chunks)  
        respuesta = procesar_pregunta_ia(self.pregunta, mejor_contexto)
        insertar_mensaje_db(self.id_conversacion_actual, "Sistema", respuesta)  # Guardar la respuesta de la IA en la base de datos
        self.respuesta_recibida.emit(respuesta)




    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())