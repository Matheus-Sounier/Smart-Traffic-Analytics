import numpy as np
import re

from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, use_gpu=False, lang='en')

def paddle_ocr(frame, x1, y1, x2, y2):
    crop = frame[y1:y2, x1:x2]
    result = ocr.ocr(crop, det=False, rec=True, cls=False)
    text = ""
    best_score = 0
    for r in result:
        scores = r[0][1]
        if np.isnan(scores):
            scores = 0
        else:
            scores = int(scores * 100)
        if scores / 100.0 > 0.6:
            text = r[0][0]
            best_score = scores
    pattern = re.compile('[\W]')
    text = pattern.sub('', text)
    text = text.replace("???", "")
    text = text.replace("粤", "")
    return str(text), best_score