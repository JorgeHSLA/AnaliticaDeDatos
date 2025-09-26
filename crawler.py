import requests
from urllib.parse import urlparse
from typing import Optional, List
import re
from collections import deque
from bs4 import BeautifulSoup
from bs4.element import Tag
from webdriver_manager.chrome import ChromeDriverManager
from collections import Counter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
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
    """
    Rastrea hasta n_paginas del catálogo de cursos y construye un índice
    con las 6 palabras más repetidas en título, presentación y objetivos.
    """

    domain = "educacionvirtual.javeriana.edu.co"
    cola = queue(n_paginas)  # Cola de URLs ya preparada con los cursos
    visitados = set()
    paginas_visitadas = 0

    # Diccionario de índices, palabra -> set(course_id)
    index = {}

    # Palabras a excluir
    lesswords = {
        "un", "una", "tu", "de", "precio", 
        # Artículos y determinantes
        "una","unos","unas","el","la","los","las","lo",
        "este","esta","estos","estas","ese","esa","esos","esas",
        "aquel","aquella","aquellos","aquellas","al","del","cual","cuales",

        # Pronombres
        "yo","tú","vos","usted","él","ella","nosotros","nosotras",
        "ustedes","ellos","ellas","me","te","se","nos","les","le",
        "lo","la","los","las","mi","mis","tu","tus","su","sus","nuestro",
        "nuestra","vuestro","vuestra",

        # Preposiciones y conjunciones
        "a","ante","bajo","cabe","con","contra","de","desde","durante",
        "en","entre","hacia","hasta","mediante","para","por","según",
        "sin","so","sobre","tras","y","o","u","ni","pero","sino",
        "aunque","porque","pues","ya","además","también","entonces",
        "donde","cuando","como","mientras","si","que","quien","quienes",

        # Verbos muy comunes
        "ser","soy","eres","es","somos","son","fui","fue","eran","será",
        "estar","estoy","estás","está","están","estuve","estaba",
        "haber","hay","había","hubo","habrán","he","has","ha","han",
        "tener","tengo","tienes","tiene","tenemos","tienen","tuve","tenía",
        "hacer","hago","haces","hace","hacen","hacía","hizo",
        "poder","puedo","puede","pueden","podemos","podía","podrán",
        "deber","debe","deben","debía","querer","quiero","quiere","quieren",
        "ir","voy","vas","va","vamos","van","iba",

        
    }

    # --------- Bucle principal ---------
    while cola and paginas_visitadas < n_paginas:
        url_actual = cola.popleft()
        if not util.is_url_ok_to_follow(url_actual, domain):
            continue
        if url_actual in visitados:
            continue

        req = util.get_request(url_actual)
        if req is None:
            continue

        html = util.read_request(req)
        if not html:
            continue

        paginas_visitadas += 1
        visitados.add(url_actual)
        print(f"[{paginas_visitadas}] Visitando: {url_actual}")

        soup = BeautifulSoup(html, "html5lib")

        # ---------- EXTRACCIÓN DE TEXTO ----------
        texts = []

        # 1. Título del curso
        titulo_h2 = soup.find("h2", class_="font-weight-bold mb-md-0")
        if titulo_h2:
            texts.append(titulo_h2.get_text(" ", strip=True))

        # 2. Presentación del programa
        presentacion = soup.find_all("div", style=re.compile("text-align:justify"))
        for div in presentacion:
            texts.append(div.get_text(" ", strip=True))

          #3. Objetivos del curso
        objetivos = soup.find("div", class_=re.compile(r"course-wrapper-content--objectives"))
        if objetivos:
            texts.append(objetivos.get_text(" ", strip=True))

        #Texto combinado
        texto = " ".join(texts).lower()

        # ---------- TOKENIZACIÓN ----------
        palabras = re.findall(r"[a-zA-Záéíóúñ][\w\d_áéíóúñ]+", texto)
        palabras_limpias = [
            p.rstrip("!:.,;") for p in palabras
            if len(p) > 1 and p not in lesswords
        ]

        # ---------- TOP 6 PALABRAS ----------
        counter = Counter(palabras_limpias)
        top6 = [w for w, _ in counter.most_common(15)]

        # Guardar en el índice
        course_id = url_actual.rstrip("/").split("/")[-1]
        for palabra in top6:
            index.setdefault(palabra, set()).add(course_id)

    # --------- Fin del rastreo ---------
    print(f"Total páginas visitadas: {paginas_visitadas}")
    print("Total palabras indexadas:", len(index))

    # --------- Guardar CSV ---------
    with open(output, "w", encoding="utf-8") as f:
        for palabra, cursos in index.items():
            for cid in cursos:
                f.write(f"{cid}|{palabra}\n")

    csv_to_sql(output, "output.sql")


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

    # webdriver-manager se encarga de bajar y configurar ChromeDriver
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
def queue(max_anchors: int):
    url = "https://educacionvirtual.javeriana.edu.co/nuestros-programas-nuevo"
    fetch_dynamic_html(url, "pagina_dinamica.html")
    # Suponiendo que ya tienes el HTML cargado
    with open("pagina_dinamica.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    base_url = "https://educacionvirtual.javeriana.edu.co/"

    anchors = extract_anchors_from_li(html_content, base_url, max_anchors)
    print("Enlaces extraídos:")
    for link in anchors:
        print(link)
    return anchors


def csv_to_sql(csv_path: str, sql_path: str, table_name: str = "indexador"):
    """
    Convierte un archivo CSV (course_id|palabra) a un archivo SQL con CREATE TABLE e INSERTS para cumplir el enunciado.
    """
    with open(csv_path, "r", encoding="utf-8") as f, open(sql_path, "w", encoding="utf-8") as sql_file:
        reader = csv.reader(f, delimiter="|")

        # Crear tabla
        sql_file.write(f"DROP TABLE IF EXISTS {table_name};\n")
        sql_file.write(f"""
                        CREATE TABLE {table_name} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            course_id TEXT NOT NULL,
                            palabra TEXT NOT NULL
                        );
                        \n""")

        # Insertar filas
        for row in reader:
            if len(row) != 2:
                continue
            course_id, palabra = row
            # Escapar comillas simples en caso de que existan
            course_id = course_id.replace("'", "''")
            palabra = palabra.replace("'", "''")
            sql_file.write(f"INSERT INTO {table_name} (course_id, palabra) VALUES ('{course_id}', '{palabra}');\n")

    print(f"✅ Archivo SQL generado en: {sql_path}")

if __name__ == "__main__":
    # Parámetros de ejemplo para la función go
    n_paginas = 33  # Número de páginas a rastrear
    dictionary = "dictionary.json"  # Archivo de diccionario
    output = "output.csv"  # Archivo de salida

    # Ejecutar la función go con los parámetros
    go(n_paginas, dictionary, output)

    print("Ejecución completada. Revisa el archivo de salida.")



