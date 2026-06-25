# Overview

Real-time automatic vehicle license plate recognition system, using YOLOv10, ByteTrack, and PaddleOCR in a modular setup, checking Brazilian Mercosur standards, and storing data in Oracle Database via Docker.

# Demonstration

<img width="1600" height="600" alt="Image" src="./img/test-video-2x.gif" />

# Technologies

- YOLO
- Python
- OpenCV
- ByteTrack
- JSON
- Docker
- Oracle DataBase
- PaddleOCR
- Torch

# Installation

## Clone the repository

```bash
git clone git@github.com:Matheus-Sounier/Automatic-Number-Plate-Recognition.git
cd Automatic-Number-Plate-Recognition
```

## Create a virtual environment

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```