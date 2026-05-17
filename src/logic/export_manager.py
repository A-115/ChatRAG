import json
import xml.etree.ElementTree as ET

def exportar_a_json(datos, ruta):
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
        

def exportar_a_xml(datos, ruta):
    root = ET.Element("conversacion_exportada")
    ET.SubElement(root, "id_conversacion").text = str(datos["id_conversacion"])
    ET.SubElement(root, "nombre_archivo").text = datos["nombre_archivo"]

    nodo_mensajes = ET.SubElement(root, "mensajes")
    for msg in datos["mensajes"]:
        n = ET.SubElement(nodo_mensajes, "mensaje_nodo")
        ET.SubElement(n, "remitente").text = msg["remitente"]
        ET.SubElement(n, "contenido").text = msg["contenido"]
        ET.SubElement(n, "fecha").text = msg.get("fecha", "Sin fecha")
    
    ET.indent(root, space="  ", level=0)  # Para mejorar la legibilidad del XML
    tree = ET.ElementTree(root)
    with open(ruta, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)
