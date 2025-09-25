import csv
import unicodedata 

# Función de normalización
def normalize(text: str) -> str:

    # Pasa a minúsculas y quita tildes.
    text = text.lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

# Busca los cursos más relevantes a una lista de palabras clave
def search(keywords: list[str], top_k: int = 10) -> list[tuple[str, float]]:
    # Noraliza intereses del usuario
    query = [normalize(k) for k in keywords]   

    # Carga el CSV en un diccionario
    cursos = {}
    with open("output.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="|")
        for row in reader:
            if len(row) != 2:
                continue
            cid, palabra = row
            cursos.setdefault(cid, set()).add(normalize(palabra))

    # Calcula relevancia de cada curso 
    ranking = []
    for cid, words in cursos.items():
        # Palabras en común
        match = len(words & set(query))
        if match == 0:
            continue
        score = match / len(query)
        ranking.append((cid, score))


    # Ordenar de mayor a menor relevancia
    ranking.sort(key=lambda x: x[1], reverse=True)

    # Se reconstruye la URL
    results = []
    for cid, score in ranking[:top_k]:
        url = f"https://educacionvirtual.javeriana.edu.co/{cid}"
        results.append((url, score))

    return results

# CONSOLA
if __name__ == "__main__":
    intereses = ["experiencias","individualidad"]  
    resultados = search(intereses, top_k=5)
    print("Cursos más relevantes:")
    for url, score in resultados:
        print(f"{url}  (relevancia {score:.2f})")
