import requests
from urllib.parse import urlparse
from typing import Optional, List

from collections import deque
from bs4 import BeautifulSoup
from bs4.element import Tag
from webdriver_manager.chrome import ChromeDriverManager

import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------- util ----------
class util:
    @staticmethod
    def get_request(url):
        # Se realiza petición HTTP GET y devuelve objeto response
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Error al hacer la solicitud: {e}")
            #Rerona None en caso de error
            return None

    @staticmethod
    def read_request(request):
        # Lee el cuerpo de la petición y lo devuelve
        if request is None:
            return None
        return request.text

    @staticmethod
    def is_url_ok_to_follow(url: str, domain: str) -> bool:
        # Devuelve True si la URL es correcta
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        if not parsed.netloc.endswith(domain):
            return False
        if "@" in url or url.startswith("mailto:"):
            return False
        path = parsed.path.lower()
        if path and not (path.endswith(".html") or "." not in path):
            return False
        return True


def go(n_paginas: int, dictionary: str, output: str):
    #  Rastrea hasta n_paginas del catálogo de cursos, construye un índice

    ## URL de inicio
    start_url = "https://educacionvirtual.javeriana.edu.co/nuestros-programas-nuevo"
    ## Dominio permitido
    domain = "educacionvirtual.javeriana.edu.co"

    ### Cola de URLs que garantiza el orden de visita
    cola = deque([start_url])
    ###Conjunto de URLs visitadas (evita repeticiones)
    visitados = set()
    paginas_visitadas = 0

    ### Diccionario de índices, palabra -> set(course_id)
    index = {} 
    ### Palabras excluidas
    stopwords = {"un", "una", "y", "o","tu", "de", "la","precio", "el", "curso", "estudiantes", "profesionales", "para", "con", "que", "en", "los", "las", "del", "su", "sus", "se", "por", "al", "lo", "es", "su", "sus", "duración","horas","en"}

    

    ### Bucle principal
    while cola and paginas_visitadas < n_paginas:
        url_actual = cola.popleft()
        if url_actual in visitados:
            continue

        # Solicitud HTTP
        req = util.get_request(url_actual)
        if req is None:
            continue
        # Leer HTML
        html = util.read_request(req)
        if not html:
            continue

        # Marcar URL como visitada
        paginas_visitadas += 1
        visitados.add(url_actual)
        print(f"[{paginas_visitadas}] Visitando: {url_actual}")

        soup = BeautifulSoup(html, "html5lib")

        # ---------- EXTRACCIÓN Y TOKENIZACIÓN ----------
        for div in soup.find_all("div", class_="card-body"):
            # Enlace al curso
            enlace = div.find("a", href=True)
            if not enlace:
                continue

            # Se construye la url absoluta y se obtiene el id_curso
            course_url = requests.compat.urljoin(url_actual, enlace["href"])
            course_id = course_url.rstrip("/").split("/")[-1]

            titulo = enlace.get_text(strip=True)
            descripcion = " ".join(p.get_text(strip=True) for p in div.find_all("p"))
            # Texto combinado en minúsculas
            texto = (titulo + " " + descripcion).lower()

            # tokens válidos: empiezan con letra, >1 char, letras/dígitos/_
            palabras = re.findall(r"[a-zA-Z][\w\d_]+", texto)
            palabras = [p.rstrip("!:.,") for p in palabras
                        if len(p) > 1 and p not in stopwords]

            # Agregar al índice cada palabra con su course_id
            for palabra in palabras:
                index.setdefault(palabra, set()).add(course_id)


    print(f"Total páginas visitadas: {paginas_visitadas}")

    print("Total palabras indexadas:", len(index))


    ### Guardar CSV con course_id|palabra
    with open(output, "w", encoding="utf-8") as f:
        for palabra, cursos in index.items():
            for cid in cursos:
                f.write(f"{cid}|{palabra}\n")



def extract_first_card_anchor(html: str) -> Optional[str]:
    """
    Extrae el primer enlace dentro de un elemento <div class="card-result ...">.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Buscar el primer div que contenga la clase "card-result"
    card = soup.select_one("div.card-result")
    if not isinstance(card, Tag):
        print("No se encontró ninguna tarjeta válida (class='card-result').")
        return None

    # Buscar el primer enlace dentro de esa tarjeta
    anchor = card.find("a", href=True)
    if not isinstance(anchor, Tag):
        print("No se encontró ningún enlace válido en la tarjeta.")
        return None

    href = anchor.get("href")
    if not isinstance(href, str):
        print("El atributo href no es válido.")
        return None

    return href


def fetch_dynamic_html(url, output_file):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # navegador invisible
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # 👇 webdriver-manager se encarga de bajar y configurar ChromeDriver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        driver.get(url)

        # Espera hasta que aparezca al menos una tarjeta
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.card-result"))
        )

        # Guardar el HTML ya renderizado
        html = driver.page_source
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ HTML guardado en {output_file}")
        return html
    finally:
        driver.quit()


def extract_anchors_from_li(html: str, base_url: str, max_anchors: int) -> deque:
    """
    Extrae los enlaces <a> dentro de los elementos <li> con la clase específica y los guarda en una cola.

    Args:
        html (str): El contenido HTML de la página.
        base_url (str): La URL base para completar enlaces relativos.
        max_anchors (int): El número máximo de enlaces a extraer.

    Returns:
        deque: Una cola con los enlaces completos extraídos.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Buscar todos los <li> con la clase específica
    li_elements = soup.find_all("li", class_="item-programa ais-Hits-item col-12 m-0 p-0 border-0 shadow-none")

    anchors_queue = deque()
    for li in li_elements:
        if len(anchors_queue) >= max_anchors:
            break

        # Buscar el primer <a> dentro del <li>
        anchor = li.find("a", href=True)
        if anchor:
            href = anchor["href"]
            # Completar el enlace si es relativo
            if not href.startswith("http"):
                href = requests.compat.urljoin(base_url, href)
            anchors_queue.append(href)

    return anchors_queue

# Ejemplo de uso
if __name__ == "__main__":
    url = "https://educacionvirtual.javeriana.edu.co/nuestros-programas-nuevo"
    fetch_dynamic_html(url, "pagina_dinamica.html")
    # Suponiendo que ya tienes el HTML cargado
    with open("pagina_dinamica.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    base_url = "https://educacionvirtual.javeriana.edu.co/"
    max_anchors = 5  # Cambia este valor según lo necesites

    anchors = extract_anchors_from_li(html_content, base_url, max_anchors)
    print("Enlaces extraídos:")
    for link in anchors:
        print(link)