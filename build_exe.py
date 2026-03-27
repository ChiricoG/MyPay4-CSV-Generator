# build_exe.py
import PyInstaller.__main__
import os
import sys
import re

# Leggi la versione da pyproject.toml
with open("pyproject.toml", "r", encoding="utf-8") as f:
    text = f.read()
    version_match = re.search(r'version\s*=\s*"(.*?)"', text)
    version = version_match.group(1) if version_match else "unknown"

# Nome finale dell'eseguibile (es: MyPay4_Generator_v2.3.2)
exe_name = f"MyPay4_Generator_v{version}"

# Percorso degli asset (logo)
assets_sep = ";" if sys.platform.startswith("win") else ":"
add_data = f"assets{assets_sep}assets"

# Percorso della cartella sorgente
src_path = os.path.abspath("src")

PyInstaller.__main__.run([
    'main.py',                      # Entry point
    '--onefile',                    # Unico file EXE
    '--windowed',                   # Nessuna console 
    f'--name={exe_name}',           # Nome dinamico basato sulla versione
    f'--add-data={add_data}',       # Include assets
    f'--paths={src_path}',          # Aggiunge src al path
    '--clean',                      # Pulisce cache 
])
