import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                                QPushButton, QFileDialog, QLabel, QScrollArea, 
                                QApplication, QFrame, QTextEdit, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QKeyEvent
from database.database_manager import (crear_conversacion_db, insertar_mensaje_db, 
                                       obtener_conversacion_por_archivo, obtener_mensajes_db, 
                                       obtener_datos_completos_conversacion)
from src.logic.ia_engine import procesar_pregunta_ia
from src.logic.document_processor import extraer_texto_pdf, dividir_texto_en_chunks, encontrar_mejores_chunks
from src.logic.export_manager import exportar_a_json, exportar_a_xml
import os

class CajaTextoChat(QTextEdit):
    enter_presionado = Signal() 
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
            self.enter_presionado.emit()
            return True
        else:
            super().keyPressEvent(event)

class CargarDocumentoThread(QThread):
    exito = Signal(list, str) # chunks, nombre_archivo
    error = Signal(str) # mensaje de error
    def __init__(self, ruta_archivo):
        super().__init__()
        self.ruta_archivo = ruta_archivo

    def run(self):
        try:
            nombre_archivo = os.path.basename(self.ruta_archivo)
            texto_completo = extraer_texto_pdf(self.ruta_archivo)
            
            if not texto_completo:
                self.error.emit("No se pudo extraer texto del archivo.")
                return
            chunks = dividir_texto_en_chunks(texto_completo)

            if not chunks:
                self.error.emit("No se pudieron generar chunks del documento.")
                return
            
            self.exito.emit(chunks, nombre_archivo)
        except Exception as e:
            self.error.emit(f"Error al procesar el documento: {str(e)}")

class ChatWindow(QWidget):
    logout_solicitado = Signal()  # Señal para indicar que se ha solicitado el logout
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)  # Permite aplicar estilos personalizados al fondo del widget
        self.chunk_documento = []  # Variable para almacenar los chunks del texto extraído del documento

        self.id_usuario_actual = 1 
        self.correo_usuario = "No identificado"  # Almacena el correo del usuario
        self.id_conversacion_actual = None
        self.modo_oscuro = True

        # Layout Principal Horizontal (Izquierda: Opciones, Derecha: Chat)
        self.layout_principal = QHBoxLayout(self)
        self.layout_principal.setContentsMargins(10, 10, 10, 10)
        self.layout_principal.setSpacing(10)

# ========================
        # --- PANEL LATERAL (Opciones del Sistema) ---
        self.contenedor_lateral = QFrame()
        self.contenedor_lateral.setObjectName("panelLateral")
        self.panel_lateral = QVBoxLayout(self.contenedor_lateral)
        self.panel_lateral.setContentsMargins(12, 12, 12, 12)
        self.panel_lateral.setSpacing(15)

        self.layout_perfil = QHBoxLayout()
        self.layout_perfil.setSpacing(10)
        
        self.lbl_icono_perfil = QLabel("👤")
        self.lbl_icono_perfil.setStyleSheet("""
            background-color: #0078d4; 
            color: white; 
            border-radius: 15px; 
            font-size: 16px;
        """)
        self.lbl_icono_perfil.setFixedSize(30, 30)
        self.lbl_icono_perfil.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_usuario = QLabel("No identificado") 
        self.lbl_usuario.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        self.layout_perfil.addWidget(self.lbl_icono_perfil)
        self.layout_perfil.addWidget(self.lbl_usuario)
        self.layout_perfil.addStretch() # Empuja el perfil a la izquierda
        self.panel_lateral.addLayout(self.layout_perfil)

        # --- ESTADO DEL ARCHIVO Y BOTONES ---
        self.lbl_archivo = QLabel("📄 Archivo: Ninguno")
        self.lbl_archivo.setWordWrap(True)
        self.panel_lateral.addWidget(self.lbl_archivo)

        self.btn_cargar = QPushButton("Cargar Documento")
        self.btn_exportar = QPushButton("Exportar Historial")
        self.btn_exportar.setEnabled(False)  # Deshabilitado hasta que se cargue un documento
        self.panel_lateral.addWidget(self.btn_cargar)
        self.panel_lateral.addWidget(self.btn_exportar)

        # --- ESPACIADOR PRINCIPAL (Empuja el logout y tema hacia abajo) ---
        self.panel_lateral.addStretch() 
        
        #Control de personalizacion de la interfaz (modo oscuro/claro)
        self.btn_tema = QPushButton("☀️ Cambiar a Modo Claro")
        self.btn_tema.setObjectName("btnTema")
        self.panel_lateral.addWidget(self.btn_tema)

        # Botón de Salida / Cerrar Sesión
        self.btn_logout = QPushButton("🚪 Cerrar Sesión")
        self.btn_logout.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold;")
        self.panel_lateral.addWidget(self.btn_logout)

        # --- Área de Chat ---
        self.layout_chat = QVBoxLayout()
        self.layout_chat.setSpacing(10)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scrollChat")
        
        # Contenedor interno donde se irán apilando las burbujas verticalmente
        self.contenido_chat = QWidget()
        self.contenido_chat.setObjectName("contenidoChat")
        self.layout_burbubas = QVBoxLayout(self.contenido_chat)
        self.layout_burbubas.setContentsMargins(10, 10, 10, 10)
        self.layout_burbubas.setSpacing(12)
        self.layout_burbubas.addStretch() # Mantiene los mensajes pegados abajo
        
        self.scroll_area.setWidget(self.contenido_chat)
        self.layout_chat.addWidget(self.scroll_area)

        # --- Barra Inferior de Entrada de Texto ---
        self.layout_entrada = QHBoxLayout()
        self.layout_entrada.setSpacing(8)
        
        self.campo_texto = CajaTextoChat()
        self.campo_texto.setFixedHeight(60)
        self.campo_texto.setPlaceholderText("Escribe tu pregunta sobre el documento aquí...")
        self.campo_texto.setObjectName("campoTexto")
        
        self.btn_enviar = QPushButton("Enviar")
        self.btn_enviar.setObjectName("btnEnviar")
        self.btn_enviar.setFixedSize(90, 32)
        
        self.layout_entrada.addWidget(self.campo_texto)
        self.layout_entrada.addWidget(self.btn_enviar)
        self.layout_chat.addLayout(self.layout_entrada)

        # Ensamblar los dos bloques maestros de la ventana
        self.layout_principal.addWidget(self.contenedor_lateral, 1)
        self.layout_principal.addLayout(self.layout_chat, 3)

        # Conexiones de Eventos
        self.btn_cargar.clicked.connect(self.seleccionar_archivo)
        self.btn_enviar.clicked.connect(self.enviar_mensaje)
        self.btn_exportar.clicked.connect(self.ejecutar_exportacion)
        self.btn_tema.clicked.connect(self.alternar_tema_grafico)
        self.campo_texto.enter_presionado.connect(self.enviar_mensaje)  
        self.btn_logout.clicked.connect(self.confirmar_logout)  # Emitir la señal de logout cuando se presione el botón

        # Aplicar Estilos iniciales (Modo Oscuro Completo por Defecto)
        self.aplicar_estilos_base()
        self.mostrar_mensaje_bienvenida()
    def mostrar_mensaje_bienvenida(self):
        self.limpiar_pantalla_chat()

        mensaje = ("Hola, Bienvenido al asistente IA de Cuervos Negros Salvajes. 🦅\n\n"
            "Para comenzar, por favor utiliza el botón de 'Cargar Documento' en el panel "
            "lateral para subir tu archivo (PDF o TXT).\n\n"
            "Una vez cargado, podré ayudarte a resumir, analizar y responder "
            "cualquier duda sobre tu información.")

        self.agregar_burbuja_mensaje("Sistema", mensaje)

    #MÉTODOS DE RENDERIZADO VISUAL Y BURBUJAS

    def agregar_burbuja_mensaje(self, remitente, texto):
        """Crea e inserta un bloque visual diferenciado en el scroll del chat"""
        # Crear la estructura de la burbuja
        contenedor_mensaje = QWidget()
        layout_mensaje = QHBoxLayout(contenedor_mensaje)
        layout_mensaje.setContentsMargins(0, 0, 0, 0)

        label_burbuja = QLabel(texto)
        label_burbuja.setWordWrap(True)
        label_burbuja.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        if remitente == "Usuario":
            # Burbuja del usuario alineada a la derecha
            label_burbuja.setStyleSheet("""
                background-color: #0078d4; color: white; border-radius: 12px;
                padding: 10px 14px; font-size: 13px; margin-left: 50px;
            """)
            layout_mensaje.addStretch()
            layout_mensaje.addWidget(label_burbuja)
            #Icoono de usuario al lado derecho de su burbuja
            lbl_icono = QLabel("👤")
            lbl_icono.setStyleSheet("font-size: 16px; margin-left: 5px;")
            layout_mensaje.addWidget(lbl_icono)
        else:
            # Burbuja del sistema/IA alineada a la izquierda
            lbl_icono = QLabel("🦅")
            lbl_icono.setStyleSheet("font-size: 16px; margin-right: 5px;")
            layout_mensaje.addWidget(lbl_icono)
            
            bg_color = "#2d2d30" if self.modo_oscuro else "#e1dfdd"
            text_color = "white" if self.modo_oscuro else "black"
            label_burbuja.setStyleSheet(f"""
                background-color: {bg_color}; color: {text_color}; border-radius: 12px;
                padding: 10px 14px; font-size: 13px; margin-right: 50px;
            """)
            layout_mensaje.addWidget(label_burbuja)
            layout_mensaje.addStretch()

        # Insertar la burbuja justo arriba del espacio flexible (stretch) para mantenerlas pegadas abajo
        indice = self.layout_burbubas.count() - 1
        self.layout_burbubas.insertWidget(indice, contenedor_mensaje)
        
        # Auto-scroll hacia el final para mantener el mensaje nuevo visible
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def limpiar_pantalla_chat(self):
        """Elimina todos los componentes del área de visualización del chat"""
        while self.layout_burbubas.count() > 1:
            item = self.layout_burbubas.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    #INTERRUPTORES DE ESTILO
    def alternar_tema_grafico(self):
        """Invierte los colores de la interfaz dinámica de manera responsiva"""
        self.modo_oscuro = not self.modo_oscuro
        self.aplicar_estilos_base()
        
        # Re-renderizar el texto del botón informativo
        if self.modo_oscuro:
            self.btn_tema.setText("☀️ Cambiar a Modo Claro")
        else:
            self.btn_tema.setText("🌙 Cambiar a Modo Oscuro")
            
        # Forzar recarga visual del historial si hay una sesión activa para pintar las burbujas con los nuevos colores
        if self.id_conversacion_actual:
            self.cargar_historial_visual(self.id_conversacion_actual)

    def aplicar_estilos_base(self):
        """Carga las directivas QSS de la hoja de estilos global con diseño moderno"""
        if self.modo_oscuro:
            # Paleta de color Oscura profesional (Estilo Flat)
            self.setStyleSheet("""
                QWidget { background-color: #1e1e1e; color: #f5f5f5; font-family: 'Segoe UI', Arial; }
                QFrame#panelLateral { background-color: #252526; border-right: 1px solid #3c3c3c; }
                
                /* Estilo general para todos los botones del panel */
                QPushButton { 
                    background-color: #3e3e42; 
                    color: white; 
                    border: none; 
                    padding: 10px; 
                    border-radius: 6px; 
                    font-weight: 500; 
                }
                QPushButton:hover { background-color: #505050; }
                
                /* Excepciones específicas */
                QPushButton#btnEnviar { background-color: #0078d4; border: none; font-weight: bold; }
                QPushButton#btnEnviar:hover { background-color: #106ebe; }
                
                QTextEdit#campoTexto { background-color: #333337; border: 1px solid #434346; color: white; padding: 10px; border-radius: 6px; }
                QScrollArea#scrollChat { border: none; background-color: #1e1e1e; }
                QWidget#contenidoChat { background-color: #1e1e1e; }
                
                /* Scrollbar moderno oscuro */
                QScrollBar:vertical { border: none; background: #1e1e1e; width: 8px; margin: 0px; }
                QScrollBar::handle:vertical { background: #434346; min-height: 30px; border-radius: 4px; }
                QScrollBar::handle:vertical:hover { background: #555558; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            """)
        else:
            # Paleta de color Clara profesional (Estilo Flat)
            self.setStyleSheet("""
                QWidget { background-color: #f3f2f1; color: #323130; font-family: 'Segoe UI', Arial; }
                QFrame#panelLateral { background-color: #ffffff; border-right: 1px solid #edebe9; }
                
                /* Estilo general para todos los botones del panel */
                QPushButton { 
                    background-color: #ffffff; 
                    color: #323130; 
                    border: 1px solid #edebe9; 
                    padding: 10px; 
                    border-radius: 6px; 
                    font-weight: 500; 
                }
                QPushButton:hover { background-color: #e1dfdd; }
                
                /* Excepciones específicas */
                QPushButton#btnEnviar { background-color: #0078d4; color: white; border: none; font-weight: bold; }
                QPushButton#btnEnviar:hover { background-color: #106ebe; }
                
                QTextEdit#campoTexto { background-color: #ffffff; border: 1px solid #a19f9d; color: #323130; padding: 10px; border-radius: 6px; }
                QScrollArea#scrollChat { border: none; background-color: #f3f2f1; }
                QWidget#contenidoChat { background-color: #f3f2f1; }
                
                /* Scrollbar moderno claro */
                QScrollBar:vertical { border: none; background: #f3f2f1; width: 8px; margin: 0px; }
                QScrollBar::handle:vertical { background: #c8c6c4; min-height: 30px; border-radius: 4px; }
                QScrollBar::handle:vertical:hover { background: #a19f9d; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            """)

    # --- LOGICA INTEGRADA REUTILIZADA (BACKEND ADAPTADO) ---
    def enviar_mensaje(self):
        if not self.id_conversacion_actual:
            self.agregar_burbuja_mensaje("Sistema", "Por favor, carga un documento para iniciar la conversación.")
            return
        
        texto = self.campo_texto.toPlainText().strip()
        if texto:
            self.agregar_burbuja_mensaje("Usuario", texto)
            self.campo_texto.clear()

            insertar_mensaje_db(self.id_conversacion_actual, "Usuario", texto)
            self.agregar_burbuja_mensaje("Sistema", "Procesando respuesta...")
            self.campo_texto.setEnabled(False)  

            self.worker = IAThread(texto, self.chunk_documento, self.id_conversacion_actual)
            self.worker.respuesta_recibida.connect(self.mostrar_respuesta_ia)
            self.worker.start()

    def mostrar_respuesta_ia(self, respuesta):
        # Limpiar el mensaje de Procesando removiendo la última burbuja temporal si fuera necesario
        self.cargar_historial_visual(self.id_conversacion_actual)
        self.campo_texto.setEnabled(True)  
        self.campo_texto.setFocus()  

    def seleccionar_archivo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "", "Archivos (*.pdf *.txt)")
        if not file_path:
            return # El usuario canceló
        
        # Confirmación antes de cambiar documento si hay una conversación activa
        if self.id_conversacion_actual:
            respuesta = QMessageBox.question(
                self, 
                "Cambiar Documento", 
                "Ya tienes un documento cargado con una conversación activa.\n\n¿Descartas la conversación actual y cargas el nuevo documento?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if respuesta == QMessageBox.StandardButton.No:
                return  # El usuario decidió no cambiar de documento
        
        nombre = file_path.split("/")[-1]
        
        #Feedback visual inmediato en la interfaz
        self.agregar_burbuja_mensaje("Sistema", f"⏳ Procesando '{nombre}'...\nPor favor espera, esto puede tardar dependiendo del tamaño del archivo.")
        
        #Bloqueamos los botones y cambiamos el texto
        self.btn_cargar.setEnabled(False)
        self.btn_cargar.setText("⏳ Cargando...")
        self.btn_exportar.setEnabled(False)  # Deshabilitar exportar mientras carga
        self.lbl_archivo.setText(f"📄 Archivo: Cargando {nombre}...")

        #Lanzamos el trabajo pesado al hilo en segundo plano
        self.hilo_documento = CargarDocumentoThread(file_path)
        self.hilo_documento.exito.connect(self.documento_procesado_exito)
        self.hilo_documento.error.connect(self.documento_procesado_error)
        self.hilo_documento.start()

    def documento_procesado_exito(self, chunks, nombre_archivo):
        """Se ejecuta cuando el hilo termina de procesar el PDF correctamente"""
        self.chunk_documento = chunks
        
        # Restaurar la interfaz
        self.lbl_archivo.setText(f"📄 Archivo: {nombre_archivo}")
        self.btn_cargar.setEnabled(True)
        self.btn_cargar.setText("Cargar Documento")  # Restaurar texto original
        self.btn_exportar.setEnabled(True)  # Habilitar exportar cuando hay documento
        
        id_conv_existente = obtener_conversacion_por_archivo(self.id_usuario_actual, nombre_archivo)  
        if id_conv_existente:
            self.id_conversacion_actual = id_conv_existente
            self.cargar_historial_visual(self.id_conversacion_actual)  
        else:
            id_conv_nuevo = crear_conversacion_db(self.id_usuario_actual, nombre_archivo)  
            if id_conv_nuevo:
                self.id_conversacion_actual = id_conv_nuevo
                self.limpiar_pantalla_chat()
                self.agregar_burbuja_mensaje("Sistema", f"Documento '{nombre_archivo}' cargado con éxito. ¡Nueva conversación iniciada!\n¿En qué te puedo ayudar?")
            else:
                self.agregar_burbuja_mensaje("Sistema", "Error al registrar la sesión en base de datos.")

    def documento_procesado_error(self, mensaje_error):
        """Sebtn_cargar.setText("Cargar Documento")  # Restaurar texto original
        self.btn_exportar.setEnabled(False)  # Mantener deshabilitado si hay error
        self. ejecuta si el PDF está corrupto o hubo un error en la lectura"""
        self.btn_cargar.setEnabled(True)
        self.lbl_archivo.setText("📄 Archivo: Ninguno")
        self.agregar_burbuja_mensaje("Sistema", f"❌ {mensaje_error}")

    def cargar_historial_visual(self, id_conversacion):
        self.limpiar_pantalla_chat()
        historial = obtener_mensajes_db(id_conversacion)

        if historial:
            for fila in historial:
                fila_lista = list(fila)  
                if "Usuario" in fila_lista:
                    remitente = "Usuario"
                    texto = fila_lista[fila_lista.index("Usuario") + 1]
                elif "Sistema" in fila_lista:
                    remitente = "Sistema"
                    texto = fila_lista[fila_lista.index("Sistema") + 1]
                else:
                    remitente = fila[0] 
                    texto = fila[1]
                
                self.agregar_burbuja_mensaje(remitente, texto)
        else:
            self.agregar_burbuja_mensaje("Sistema", "No se encontraron mensajes en esta conversación. Comienza a interactuar haciendo una pregunta sobre el documento.")

    def ejecutar_exportacion(self):
        if not self.id_conversacion_actual: 
            return  

        ruta, filtro = QFileDialog.getSaveFileName(self, "Exportar Conversación", f"Chat_{self.id_conversacion_actual}",
                                                    "Archivos JSON (*.json);;Archivos XML (*.xml)")
        if ruta:
            # Feedback visual: cambiar texto y deshabilitar
            self.btn_exportar.setEnabled(False)
            self.btn_exportar.setText("⏳ Exportando...")
            
            datos = obtener_datos_completos_conversacion(self.id_conversacion_actual)  
            try:
                if ruta.endswith(".json") or "JSON" in filtro:
                    exportar_a_json(datos, ruta)
                    self.agregar_burbuja_mensaje("Sistema", "✅ Historial exportado con éxito a archivo JSON.")
                elif ruta.endswith(".xml") or "XML" in filtro:
                    exportar_a_xml(datos, ruta)
                    self.agregar_burbuja_mensaje("Sistema", "✅ Historial exportado con éxito a archivo XML.")
            except Exception as e:
                self.agregar_burbuja_mensaje("Sistema", f"❌ Error al exportar: {str(e)}")
            finally:
                # Restaurar el botón
                self.btn_exportar.setEnabled(True)
                self.btn_exportar.setText("Exportar Historial")

    def confirmar_logout(self):
        respuesta = QMessageBox.question(self, "Confirmar Cierre de Sesión", "¿Estás seguro de que deseas cerrar sesión?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if respuesta == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Sesión Cerrada", "Has cerrado sesión exitosamente.")
            self.logout_solicitado.emit()  # Emitir la señal para que MainWindow maneje el cambio de vista al login

            # Limpiar estado interno del chat para la próxima sesión
            self.id_conversacion_actual = None
            self.lbl_archivo.setText("📄 Archivo: Ninguno")
            self.limpiar_pantalla_chat()
            self.mostrar_mensaje_bienvenida()

class IAThread(QThread):
    respuesta_recibida = Signal(str)

    def __init__(self, pregunta, chunks=None, id_conversacion=None):
        super().__init__()
        self.pregunta = pregunta
        self.chunks = chunks if chunks is not None else []
        self.id_conversacion_actual = id_conversacion  

    def run(self):
        mejor_contexto = encontrar_mejores_chunks(self.pregunta, self.chunks)  
        respuesta = procesar_pregunta_ia(self.pregunta, mejor_contexto)
        insertar_mensaje_db(self.id_conversacion_actual, "Sistema", respuesta)  
        self.respuesta_recibida.emit(respuesta)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())