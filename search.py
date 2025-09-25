import requests
from bs4 import BeautifulSoup

urls = [
    "https://educacionvirtual.javeriana.edu.co/ruta-hub-aeronautico",
    "https://educacionvirtual.javeriana.edu.co/escuela-de-verano",
    "https://educacionvirtual.javeriana.edu.co/teachers_education",
    "https://educacionvirtual.javeriana.edu.co/health_education",
    "https://educacionvirtual.javeriana.edu.co/generacion-55",
]

for url in urls:
    print("\n🔗 URL:", url)
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        html = r.text
        soup = BeautifulSoup(html, "html.parser")

        titulo = soup.find("h2", class_="font-weight-bold mb-md-0")
        if titulo:
            print("✅ Título encontrado:", titulo.get_text(strip=True))
        else:
            print("⚠️ No se encontró título en HTML")

        content_divs = soup.find_all("div", class_="course-wrapper-content")
        if content_divs:
            print(f"✅ Se encontraron {len(content_divs)} divs de contenido")
            print("Ejemplo:", content_divs[0].get_text(strip=True)[:120], "...")
        else:
            print("⚠️ No se encontraron divs de contenido")
    except Exception as e:
        print("❌ Error:", e)