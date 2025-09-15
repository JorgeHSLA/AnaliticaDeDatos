import requests
from urllib.parse import urlparse

from collections import deque
from bs4 import BeautifulSoup

import re

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
    stopwords = {"un", "una", "y", "o", "de", "la", "el", "curso", "estudiantes", "profesionales"}

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

        # ---------- ENCOLAR NUEVOS ENLACES ----------
        for a in soup.find_all("a", href=True):
            href = a["href"]
            abs_url = requests.compat.urljoin(url_actual, href)
            if util.is_url_ok_to_follow(abs_url, domain):
                if abs_url not in visitados:
                    cola.append(abs_url)

    print(f"Total páginas visitadas: {paginas_visitadas}")

    print("Total palabras indexadas:", len(index))


    ### Guardar CSV con course_id|palabra
    with open(output, "w", encoding="utf-8") as f:
        for palabra, cursos in index.items():
            for cid in cursos:
                f.write(f"{cid}|{palabra}\n")


# ---------- EJECUCIÓN ----------
if __name__ == "__main__":
    go(n_paginas=5, dictionary="dummy.json", output="dummy.csv")