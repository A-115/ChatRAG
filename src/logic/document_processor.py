import fitz  # PyMuPDF

def extraer_texto_pdf(ruta_archivo):
    texto_completo = ""
    # Abre un archivo PDF, lee su contenido y lo devuelve como texto
    try:
        documento = fitz.open(ruta_archivo)
        for numero_pagina in range(documento.page_count):
            pagina = documento.load_page(numero_pagina)
            texto_completo += pagina.get_text()
        documento.close()

        print(f"Se extrayó el texto del PDF: {ruta_archivo}")
        return texto_completo
    except Exception as e:
        print(f"Error al extraer texto del PDF: {e}")
        return None


# Lista de palabras que harian que la IA no las tome en cuenta para encontrar el chunk más relevante, ya que son palabras comunes que no aportan información relevante para la pregunta
STOPWORDS_ESPANOL = {
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "y", "e", "o", "u", "ni", "que", "pero", "aunque", "mas",
    "a", "ante", "bajo", "cabe", "con", "contra", "de", "desde",
    "en", "entre", "hacia", "hasta", "para", "por", "segun", "sin",
    "sobre", "tras", "durante", "mediante",
    "yo", "tu", "el", "ella", "nosotros", "vosotros", "ellos", "ellas",
    "me", "te", "se", "nos", "os", "le", "les", "lo", "la",
    "mi", "tu", "su", "nuestro", "vuestro",
    "este", "ese", "aquel", "esta", "esa", "aquella", "estos", "esos", "aquellos",
    "cual", "quien", "cuanto", "cuando", "como", "donde",
    "es", "son", "fue", "ser", "estar", "tiene", "tienen", "hace", "hacen",
    "muy", "mucho", "poco", "aqui", "alli", "hoy", "manana",
    "si", "no", "asi"
}


def dividir_texto_en_chunks(texto, tamaño_chunk=1000, solapamiento=200):
    # Divide el texto en partes más pequeñas (chunks) para facilitar su procesamiento
    chunks = []
    inicio = 0

    while inicio < len(texto):
        fin = inicio + tamaño_chunk # Define el final del chunk
        chunk = texto[inicio:fin] # Extrae el chunk del texto
        chunks.append(chunk)
        inicio += tamaño_chunk - solapamiento # Avanza el inicio para el siguiente chunk
    return chunks


def limpiar_texto(texto):
    #Convertir a minúsculas 
    texto_limpio = texto.lower()
    
    #Reemplazar caracteres acentuados por sus equivalentes sin acento
    reemplazos = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"))
    for con_tilde, sin_tilde in reemplazos:
        texto_limpio = texto_limpio.replace(con_tilde, sin_tilde)
        
    #Quitar todos los signos
    texto_limpio = texto_limpio.replace("?", "").replace(".", "").replace("!", "").replace(",", "").replace(";", "").replace(":", "").replace("(", "").replace(")", "").replace("¿", "")
    
    #Separar y restar stopwords
    todas_palabras = set(texto_limpio.split())
    palabras_clave = todas_palabras - STOPWORDS_ESPANOL
    
    return palabras_clave

def encontrar_mejores_chunks(pregunta, chunks):
    #Busca cual de los chunks es el más relevante para la pregunta que se haga y devuelve ese chunk para que la IA lo procese
    if not chunks:
        return ""
    # Limpiar la pregunta y convertirla en un conjunto de palabras
    palabra_pregunta = limpiar_texto(pregunta)

    mejor_chunk = ""
    max_puntaje = 0
    chunk_limpio = " ".join(mejor_chunk.split())  # Eliminar espacios extras

    for chunk in chunks:
        # Limpiar el chunk y convertirlo en un conjunto de palabras
        texto_chunk_limpio = chunk.lower()
        remplazos = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"))
        for con_tilde, sin_tilde in remplazos:
            texto_chunk_limpio = texto_chunk_limpio.replace(con_tilde, sin_tilde)

        texto_chunk_limpio = texto_chunk_limpio.replace("?", "").replace(".", "").replace("!", "").replace(",", "").replace(";", "").replace(":", "").replace("(", "").replace(")", "").replace("¿", "")
        lista_palabras_chunk = texto_chunk_limpio.split()

        puntaje_chunk = 0
        for palabra in palabra_pregunta:
            puntaje_chunk += lista_palabras_chunk.count(palabra) # Incrementar el puntaje por cada coincidencia de palabra entre la pregunta y el chunk

        if puntaje_chunk > max_puntaje:
            max_puntaje = puntaje_chunk
            mejor_chunk = chunk
            
        
    print(f"El chunk más relevante para la pregunta '{pregunta}' es: {mejor_chunk[:100]}... con {max_puntaje} coincidencias.")
    if max_puntaje == 0:
        print("No se encontraron coincidencias relevantes entre la pregunta y los chunks del documento.")
        return ""
    return mejor_chunk
