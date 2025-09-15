import requests
from urllib.parse import urlparse

from collections import deque
from bs4 import BeautifulSoup


# Simulación de tus funciones wrapper
class util:
    @staticmethod
    def get_request(url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response   # esto es el objeto request
        except requests.RequestException as e:
            print(f"Error al hacer la solicitud: {e}")
            return None

    @staticmethod
    def read_request(request):
        if request is None:
            return None
        return request.text  # aquí está el HTML completo
    
    @staticmethod
    def is_url_ok_to_follow(url: str, domain: str) -> bool:
        parsed = urlparse(url)

        # 1. Debe ser absoluta (tiene esquema y netloc)
        if not parsed.scheme or not parsed.netloc:
            return False

        # 2. Debe caer dentro del dominio
        if not parsed.netloc.endswith(domain):
            return False

        # 3. No puede contener @ ni mailto
        if "@" in url or url.startswith("mailto:"):
            return False

        # 4. Extensión válida: vacía o .html
        path = parsed.path.lower()
        if path and not (path.endswith(".html") or "." not in path):
            return False

        return True


# Uso
#url = "https://educacionvirtual.javeriana.edu.co"
#req = util.get_request(url)
#
#if req:
#    html = util.read_request(req)
#    print("Longitud del HTML:", len(html))
#    print("Primeros 500 caracteres del HTML:\n")
#    print(html[:500])  # para que no te sature la consola
#else:
#    print("No se pudo obtener la página.")
#
#
#
#
#def go(nPaginas, dictionary:str, output:str):
#    req = util.get_request(url)
#    if req:
#        html = util.read_request(req)
#        return html
#    return None


def go(n_paginas: int, dictionary: str, output: str):
    start_url = "https://educacionvirtual.javeriana.edu.co/nuestros-programas-nuevo"
    domain = "educacionvirtual.javeriana.edu.co"

    cola = deque([start_url])
    visitados = set()
    paginas_visitadas = 0

    while cola and paginas_visitadas < n_paginas:
        url_actual = cola.popleft()
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

        for a in soup.find_all("a", href=True):
            href = a["href"]
            abs_url = requests.compat.urljoin(url_actual, href)
            if util.is_url_ok_to_follow(abs_url, domain):
                if abs_url not in visitados:
                    cola.append(abs_url)

    print(f"Total páginas visitadas: {paginas_visitadas}")




    #Pruebas
if __name__ == "__main__":
 go(n_paginas=5, dictionary="dummy.json", output="dummy.csv")