from pathlib import Path
import json


def generar_diccionario_carpetas(ruta_base="."):
    """
    Recorre todas las carpetas y subcarpetas desde ruta_base
    y genera un diccionario con formato:

    {
        "carpeta/": "",
        "carpeta/sub1/": "",
        ...
    }
    """

    base = Path(ruta_base).resolve()

    resultado = {}

    # incluir carpeta raíz
    resultado[f"{base.name}/"] = ""

    # recorrer todas las subcarpetas
    for carpeta in sorted(base.rglob("*")):
        if carpeta.is_dir():
            ruta_relativa = carpeta.relative_to(base)

            clave = f"{base.name}/{ruta_relativa.as_posix()}/"

            resultado[clave] = ""

    return resultado


if __name__ == "__main__":

    # carpeta actual
    ruta = "."

    diccionario = generar_diccionario_carpetas(ruta)

    # mostrar en pantalla
    print(json.dumps(diccionario, indent=2, ensure_ascii=False))

    # guardar archivo json
    with open("estructura_carpetas.json", "w", encoding="utf-8") as f:
        json.dump(diccionario, f, indent=2, ensure_ascii=False)

    print("\nArchivo generado: estructura_carpetas.json")




import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


# =========================
# CONFIG
# =========================

SERVICE_ACCOUNT_FILE = "service_account.json"

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


# =========================
# AUTH
# =========================

creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

service = build("drive", "v3", credentials=creds)


# =========================
# HELPERS
# =========================

def buscar_carpeta(nombre, parent_id):
    """
    Busca carpeta por nombre dentro de parent_id
    """

    query = (
        f"mimeType='application/vnd.google-apps.folder' "
        f"and trashed=false "
        f"and name='{nombre}' "
        f"and '{parent_id}' in parents"
    )

    results = service.files().list(
        q=query,
        fields="files(id,name)"
    ).execute()

    files = results.get("files", [])

    if files:
        return files[0]["id"]

    return None


def resolver_path(path, root_id):
    """
    Resuelve:
    MPAT4/core/cognition/

    usando búsqueda jerárquica
    """

    partes = [p for p in path.split("/") if p]

    current_id = root_id

    # saltar MPAT4 porque root ya es MPAT4
    for carpeta in partes[1:]:

        folder_id = buscar_carpeta(carpeta, current_id)

        if not folder_id:
            return None

        current_id = folder_id

    return current_id


# =========================
# LOAD JSON
# =========================

with open("estructura.json", "r", encoding="utf-8") as f:
    data = json.load(f)


vfolder = data["v-folder"]


# root conocido
ROOT_ID = vfolder["MPAT4/"]


# =========================
# RESOLVE
# =========================

for path, folder_id in vfolder.items():

    if folder_id == "":

        print(f"Resolviendo: {path}")

        resolved = resolver_path(path, ROOT_ID)

        if resolved:
            vfolder[path] = resolved
            print(f"  OK -> {resolved}")
        else:
            print("  NO ENCONTRADO")


# =========================
# SAVE
# =========================

with open("estructura_resuelta.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\nestructura_resuelta.json generado")
