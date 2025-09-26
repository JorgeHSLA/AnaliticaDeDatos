# Laboratorio 2
## Jorge Sierra y Sara Garcia

### Objetivo
Con el desarrollo de este laboratorio usted:

1. Construirá un motor de búsqueda de cursos de la Javeriana
2. Construirá un rastreador web que rastrea una copia de sombra del catálogo universitario para construir un índice simple.

### Herramientas que se van a usar:

- Python:

    - requests (para conexiones http y recuperardocumentos)
    - html5lib y beautifulsoup4 (mejorar entendimiento de html)
    - urllib.parse (para analisis de URLS)
    - selenium (para la extraccion de paginas dinamicas)

### pasos:

1. Lo primero a realizar fue el crawler:
    1. Implementamos parte del codigo requerido por las especificaciones en el docuemnto pdf en la clase util, en este hay 3 funciones: get_request(url), el cual realiza una petición HTTP GET y devuelve un objeto response, read_request(request) Que el cuerpo de la petición y lo devuelve, y is_url_ok_to_follow(url: str, domain: str) que determina si la url es concuerda con lo que buscamos
    2. Despues lo que se hizo fue una forma de traer los paths de 


