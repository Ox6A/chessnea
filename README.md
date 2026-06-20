# Chess NEA Project

[![Build](https://git.tsbprodesk.co.uk/localuser/chessnea/badges/workflows/build.yml/badge.svg?branch=main&event=push&style=flat-square)](https://git.tsbprodesk.co.uk/localuser/chessnea/actions)
[![Release](https://git.tsbprodesk.co.uk/localuser/chessnea/badges/release.svg?style=flat-square)](https://git.tsbprodesk.co.uk/localuser/chessnea/releases)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)
![License](https://img.shields.io/badge/license-GPL--3.0-blue?style=flat-square)

A chess game, written in Python with the `pygame-ce` library, for my A-Level OCR Computer Science NEA.

## Requirements
- Python 3.10 or newer
- Git, or download a `.zip` of the source code
- `pygame-ce` package

## Installation

Windows Powershell:
```powershell
git clone https://git.tsbprodesk.co.uk/localuser/chessnea.git
cd chessnea
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src\main.py
```

Linux/macOS:

```bash
git clone https://git.tsbprodesk.co.uk/localuser/chessnea.git
cd chessnea
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 src/main.py
```

## Development

Follow the same steps as Installation, but ensure you use `requirements-dev.txt` instead of `requirements.txt`. Run unit tests with: 

Linux/macOS:

```bash
cd chessnea
source venv/bin/activate
python3 -m pytest -n auto -q
```

Windows Powershell:
```powershell
cd chessnea
.\venv\Scripts\Activate.ps1
python -m pytest -n auto -q
```