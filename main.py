from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import cv2
import numpy as np
from starlette.requests import Request

app = FastAPI()
#lấy css và js từ thư mục static
app.mount("/static", StaticFiles(directory="static"), name="static")

#lấy template từ thư mục templates
templates = Jinja2Templates(directory="templates")

#hàm đọc ảnh
def read_image(file: UploadFile):
    image = np.fromstring(file.file.read(), np.uint8)
    return cv2.imdecode(image, cv2.IMREAD_COLOR)

#hàm nhận diện khuôn mặt trong ảnh
def detect_faces(image):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces

#hàm kiểm tra và so sánh 2 ảnh
def compare_faces(image1, image2):
    faces1 = detect_faces(image1)
    faces2 = detect_faces(image2)

    if len(faces1) == 0 and len(faces2) == 0:
        return "không tìm thấy khuôn mặt ở cả 2 ảnh"
    elif len(faces1) == 0:
        return "ảnh 1 không tìm thấy khuôn mặt"
    elif len(faces2) == 0:
        return "ảnh 2 không tìm thấy khuôn mặt"

    if len(faces1) == len(faces2):
        return "Cùng 1 người"
    else:
        return "2 người khác nhau"

#route nhận ảnh và so sánh
@app.post("/upload-images")
async def upload_images(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    image1 = read_image(file1)
    image2 = read_image(file2)
    
    result = compare_faces(image1, image2)
    return {"result": result}

#route chính render giao diện
@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})