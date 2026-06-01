import json
from pathlib import Path

class MPAT4Config:
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.v_folder = {}
        self.load_config()

    def load_config(self):
        """Carga el JSON dinámico de configuración sin alterar el código"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Soporta tanto el formato plano "v-folder" como la estructura cruda
                self.v_folder = data.get("v-folder", data)
            print(f"✅ Configuración de MPAT4 cargada con éxito desde {self.json_path}")
        except FileNotFoundError:
            print(f"❌ Error: No se encontró el archivo de configuración en {self.json_path}")
        except json.JSONDecodeError:
            print(f"❌ Error: El archivo {self.json_path} no tiene un formato JSON válido")

    def get_id(self, virtual_path: str) -> str:
        """Devuelve el ID de Google Drive para una ruta virtual específica"""
        # Asegura que la ruta termine en '/' si es un directorio
        if not virtual_path.endswith('/'):
            virtual_path += '/'

        folder_id = self.v_folder.get(virtual_path, "")
        if not folder_id:
            print(f"⚠️ Advertencia: La ruta '{virtual_path}' no tiene un ID de Google Drive asignado.")
        return folder_id

# =====================================================================
# EJEMPLO DE USO EN TU ENTORNO REAL
# =====================================================================
if __name__ == "__main__":
    # 1. Instancias la configuración apuntando a tu archivo JSON
    # Al día siguiente solo cambias el contenido del JSON, NO este código.
    config = MPAT4Config("estructura_carpetas.json")

    # 2. Tu proceso solicita los componentes dinámicamente en tiempo de ejecución
    runtime_id = config.get_id("MPAT4/core/cognition/cognition_runtime/")
    seccomp_id = config.get_id("MPAT4/core/sandboxing/seccomp/")

    print(f"\nID recuperado para Runtime: {runtime_id}")
    print(f"ID recuperado para Seccomp: {seccomp_id}")
