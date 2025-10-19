#!/bin/bash
set -e
pip install -r requirements.txt
python scripts/firestore_to_opensearch.py  # <-- este lo agregas aquí
python main.py
