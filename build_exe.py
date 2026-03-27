# build_exe.py
import PyInstaller.__main__
import os
import sys

# Percorso degli asset (logo)
# Su Windows il separatore per --add-data è ';'
assets_sep = ";" if sys.platform.startswith("win") else ":"
add_data = f"assets{assets_sep}assets"

# Percorso della cartella sorgente
src_path = os.path.abspath("src")

PyInstaller.__main__.run([
    'main.py',                      # Entry point (il wrapper root)
    '--onefile',                    # Unico file EXE
    '--windowed',                   # Nessuna console all'avvio
    '--name=MyPay4_Generator_v2.2.0',
    f'--add-data={add_data}',       # Include la cartella assets nell'EXE
    f'--paths={src_path}',          # Aggiunge src al path di ricerca moduli
    '--clean',                      # Pulisce la cache prima della build
])
