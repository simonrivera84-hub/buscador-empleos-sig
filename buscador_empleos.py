import os
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from bs4 import BeautifulSoup
from google import genai

# --- 1. Configuración de credenciales (se leen desde los Secrets de GitHub) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# ⚠️ IMPORTANTE: Cambia esto por tu correo real de Gmail
EMAIL_SENDER = "simonrivera84@gmail.com" 
EMAIL_RECIPIENT = "simonrivera84@gmail.com" 

# --- 2. Función para buscar ofertas de empleo en LinkedIn ---
def buscar_ofertas(termino_busqueda):
    print(f"Buscando ofertas para: {termino_busqueda}...")
    url = f"https://www.linkedin.com/jobs/search?keywords={termino_busqueda}&location=Chile&position=1&pageNum=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        ofertas = []
        for tarjeta in soup.find_all('div', class_='base-card'):
            titulo_tag = tarjeta.find('h3', class_='base-search-card__title')
            empresa_tag = tarjeta.find('h4', class_='base-search-card__subtitle')
            link_tag = tarjeta.find('a', class_='base-card__full-link')
            
            if titulo_tag and empresa_tag and link_tag:
                ofertas.append({
                    "titulo": titulo_tag.get_text(strip=True),
                    "empresa": empresa_tag.get_text(strip=True),
                    "link": link_tag['href']
                })
        print(f"Se encontraron {len(ofertas)} ofertas.")
        return ofertas
    except Exception as e:
        print(f"Error al buscar ofertas: {e}")
        return []

# --- 3. Función para filtrar ofertas usando Gemini ---
def filtrar_ofertas_con_ia(ofertas, perfil_candidato):
    print("Filtrando ofertas con IA...")
    
    if not GEMINI_API_KEY or GEMINI_API_KEY == "prueba123":
        print("  -> ADVERTENCIA: GEMINI_API_KEY no está configurada o es de prueba. Se aceptarán todas las ofertas.")
        return ofertas

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"  -> Error al conectar con la IA: {e}")
        return ofertas

    ofertas_filtradas = []
    for oferta in ofertas:
        prompt = f"""
        Actúa como un reclutador técnico experto en geomática y software SIG.
        Evalúa la siguiente oferta de empleo:
        Título: {oferta['titulo']}
        Empresa: {oferta['empresa']}
        
        El candidato ideal tiene experiencia en: {perfil_candidato}.
        
        Responde únicamente con la palabra "SI" si la oferta es relevante para el perfil, o "NO" si no lo es. No des explicaciones.
        """
try:
    response = client.models.generate_content(
    model='gemini-3.5-flash-lite',
        contents=prompt,
    )
    if "SI" in response.text.upper():
        print(f"  -> Oferta ACEPTADA: {oferta['titulo']}")
        ofertas_filtradas.append(oferta)
    else:
        print(f"  -> Oferta descartada: {oferta['titulo']}")
    
    # --- AÑADE ESTA LÍNEA ---
    time.sleep(13) # Pausa de 13 segundos para respetar el límite de 5 RPM
    # -------------------------

except Exception as e:
    print(f"  -> Error al filtrar con IA: {e}")
    ofertas_filtradas.append(oferta)
        except Exception as e:
            print(f"  -> Error al filtrar con IA: {e}")
            # Si hay error, la aceptamos para no perderla
            ofertas_filtradas.append(oferta)
            
    return ofertas_filtradas

# --- 4. Función para enviar el correo electrónico ---
def enviar_correo(ofertas):
    if not ofertas:
        print("No hay ofertas para enviar.")
        return

    if EMAIL_SENDER == "tu_correo@gmail.com" or EMAIL_RECIPIENT == "tu_correo@gmail.com":
        print("  -> ERROR: Debes cambiar 'tu_correo@gmail.com' por tu correo real en el código.")
        return

    print("Preparando y enviando correo...")
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = f"🔍 {len(ofertas)} Ofertas de Empleo Geomática Encontradas"
    
    cuerpo_html = "<h2>Ofertas de Empleo Relevantes</h2><ul>"
    for oferta in ofertas:
        cuerpo_html += f"<li><strong>{oferta['titulo']}</strong> en {oferta['empresa']} - <a href='{oferta['link']}'>Ver oferta</a></li>"
    cuerpo_html += "</ul>"
    
    msg.attach(MIMEText(cuerpo_html, 'html'))
    
    try:
        # Usamos el puerto 587 con starttls, que es el estándar moderno para Gmail
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            server.starttls() # Inicia conexión segura
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        print("¡Correo enviado exitosamente!")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

# --- 5. Función principal que ejecuta todo ---
def main():
    print("Iniciando agente buscador de empleos...")
    
    terminos = ["Geomatica", "GIS", "ArcGIS", "Civil 3D", "SIG"]
    perfil = "Geomática, SIG, ArcGIS, AutoCAD Civil 3D, teledetección, Python"
    
    todas_las_ofertas = []
    for termino in terminos:
        ofertas_encontradas = buscar_ofertas(termino)
        todas_las_ofertas.extend(ofertas_encontradas)
    
    # Eliminamos duplicados
    ofertas_unicas = [dict(t) for t in {tuple(d.items()) for d in todas_las_ofertas}]
    print(f"Total de ofertas únicas encontradas: {len(ofertas_unicas)}")
    
    if ofertas_unicas:
        ofertas_relevantes = filtrar_ofertas_con_ia(ofertas_unicas, perfil)
        enviar_correo(ofertas_relevantes)
    else:
        print("No se encontraron ofertas en esta ejecución.")

if __name__ == "__main__":
    main()
