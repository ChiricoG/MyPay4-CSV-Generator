# SPDX-License-Identifier: EUPL-1.2
import sys
import os

# Aggiunge la cartella 'src' al path per permettere l'importazione di mypay4_generator
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from mypay4_generator.__main__ import main as _package_main

def main():
    _package_main()

if __name__ == "__main__":
    main()
