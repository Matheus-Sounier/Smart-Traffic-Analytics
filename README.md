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

# Oracle Database Setup

## Create the user

```sql
CREATE USER license_plate_example IDENTIFIED BY your_password;

GRANT CONNECT, RESOURCE TO license_plate_example;
```

## Configure the connection

```env
DB_USER=license_plate_example
DB_PASSWORD=your_password
DB_HOST=your_type_host
DB_PORT=1521
DB_SERVICE=your_service
```

## Run the code

If everything's all right, then run in the root directory:

```bash
python main.py

```

# How to train your own license plate yolo model

Access the roboflow and try to install any [dataset](https://universe.roboflow.com/roboflow-universe-projects/license-plate-recognition-rxg4e/dataset/4) you want 

## The dataset structure that you've installed'll look like this:

```text
dataset/
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── data.yaml
```

## Example data.yaml

```yaml
path: dataset

train: train/images
val: valid/images

names:
  0: license_plate
```