## Application Demonstration
![Demo](README_MD/brave_AdPuw7W7F2.gif)

## Frameworks and technologies used

| Python | Django |
|----------|----------|
|  ![Python](README_MD/python.png)    | ![Django](README_MD/django.png)   |


| OpenCV | Tesseract OCR |
|----------|----------|
|  ![Open CV](README_MD/opencv.webp)    | ![Tesseract OCR](README_MD/tesseract_ocr.png)   |


| YOLO V8 Machine Learning Architecture from Ultralytics |
|--------------------------------------------------------|
|  ![YOLOv8 from Ultralytics](README_MD/yolov8.png)  |



We use YOLOv8 from Ultralytics Ltd. to train the provided datasets, validate, test and deploy the the Trained Model and saved the model as "best.pt". 

```python
from ultralytics import YOLO

# Load a model
model = YOLO("yolov8n.yaml")  # build a new model from scratch

# Use the model
results = model.train(data="/content/Bangladeshi-license-plate-1/data.yaml", epochs=100)  # train the model
```



## Deployed Demo Web Application
To check the site go to https://lprts.onrender.com/

Username and Password


| Username | Password |
|----------|----------|
|  arif  |  1830398  |
|  asif  |  1831066  |
|  farhan  |  1810615  |
|  shibriat  |  1831099  |


## Top Contributors
| Student ID | Student Name |
|----------|----------|
|  1830398  |  S.M. Arif Mahmud  |
|  1831066  |  Ahmad Asif Arifeen  |
|  1810615  |  S.M. Farhan Ishrak  |
|  1831099  |  Shibriat Hossain  |



