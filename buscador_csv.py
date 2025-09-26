import csv
import unicodedata

# ------------------------------------------------------------
# Normaliza: minúsculas y sin tildes
# ------------------------------------------------------------
def normalize(text: str) -> str:
    text = text.lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

# ------------------------------------------------------------
# Busca cursos más relevantes según las palabras clave
# ------------------------------------------------------------
def search(keywords: list[str], top_k: int = 10) -> list[tuple[str, float]]:
    query = [normalize(k) for k in keywords]

    # Cargar CSV en {curso_id: set(palabras)}
    cursos = {}
    with open("output.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="|")
        for row in reader:
            if len(row) != 2:
                continue
            cid, palabra = row
            cursos.setdefault(cid, set()).add(normalize(palabra))

    # Calcular relevancia
    ranking = []
    for cid, words in cursos.items():
        match = len(words & set(query))
        if match == 0:
            continue
        score = match / len(query)
        ranking.append((cid, score))

    # Ordenar por relevancia descendente
    ranking.sort(key=lambda x: x[1], reverse=True)

    # Reconstruir URLs
    results = []
    for cid, score in ranking[:top_k]:
        url = f"https://educacionvirtual.javeriana.edu.co/{cid}"
        results.append((url, score))

    return results

# ------------------------------------------------------------
# Interacción con el usuario
# ------------------------------------------------------------
if __name__ == "__main__":
    print("=== Buscador de cursos ===")
    print("Escribe tus intereses separados por espacios o comas.")
    print("Ejemplo: fotografia luminosidad composicion\n")

    # Leer una sola línea y dividir en palabras
    entrada = input("Intereses: ")
    # Permite que el usuario escriba: "vida, experiencia, genero"
    intereses = [pal.strip() for pal in entrada.replace(",", " ").split() if pal.strip()]

    if not intereses:
        print("No ingresaste intereses.")
    else:
        resultados = search(intereses, top_k=10)
        if resultados:
            print("\nCursos más relevantes:")
            for url, score in resultados:
                print(f"{url}  (relevancia {score:.2f})")
        else:
            print("\nNo se encontraron cursos que coincidan con esos intereses.")
