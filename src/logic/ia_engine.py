# Simulación de un motor de IA para responder preguntas basadas en el contenido de un PDF
import time
import random

def procesar_pregunta_ia(pregunta, contexto_documento=""):
    """
    Simula el tiempo de respuesta de una IA real.
    """
    # Simulamos que la IA está "pensando" (latencia)
    # Esto detendría cualquier hilo donde se ejecute
    time.sleep(3) 
    
    if not contexto_documento:
        return "No se ha cargado ningún documento para proporcionar contexto. Por favor, carga un PDF para obtener respuestas basadas en su contenido."
    respuestas = [
        f"Basado en el documento cargado, la respuesta a '{pregunta}' es...",
        f"He leído los {len(contexto_documento)} caracteres del PDF. La respuesta es positiva.",
        "Según el contexto proporcionado, puedo confirmar ese dato.",
    ]
    
    return random.choice(respuestas)