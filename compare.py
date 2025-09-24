import sys
import csv

def load_from_csv(csv_path: str) -> dict:
    
    # Carga el CSV y devuelve un diccionario:  { course_id: set(palabras) }
    cursos = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="|")
        for row in reader:
            if len(row) != 2:
                continue
            cid, palabra = row
            cursos.setdefault(cid, set()).add(palabra)
    return cursos


def jaccard(set1: set, set2: set) -> float: # forma de medir similitud entre dos conjuntos de 0 a 1 
    """
    Calcula la similitud de Jaccard entre dos conjuntos.
    """
    if not set1 and not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)


def compare(csv_path: str, curso1: str, curso2: str) -> None:
    """
    Imprime la similitud Jaccard entre curso1 y curso2
    usando el índice construido desde el CSV.
    """
    cursos = load_from_csv(csv_path)

    if curso1 not in cursos:
        print(f"Curso {curso1} no encontrado en {csv_path}")
        return
    if curso2 not in cursos:
        print(f"Curso {curso2} no encontrado en {csv_path}")
        return

    set1 = cursos[curso1]
    set2 = cursos[curso2]
    sim = jaccard(set1, set2)

    print(f"Similitud Jaccard entre '{curso1}' y '{curso2}': {sim:.3f}")
    print(f"Tokens en común: {sorted(set1 & set2)}")


# --------- Modo consola ----------
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python compare.py <archivo_csv> <curso1_id> <curso2_id>")
        sys.exit(1)

    csv_path, curso1, curso2 = sys.argv[1], sys.argv[2], sys.argv[3]
    compare(csv_path, curso1, curso2)
