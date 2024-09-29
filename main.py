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
    #tải model để phát hiện khuôn mặt. đường dẫn tới mô hình được lấy từ thư viện OpenCV.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #chuyển sang ảnh xám để tăng tốc độ xử lý
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)) 
    return faces

#hàm kiểm tra và so sánh 2 ảnh
def compare_faces(image1, image2):
    faces1 = detect_faces(image1)
    faces2 = detect_faces(image2)

    if len(faces1) == 0:
        return "ảnh 1 không tìm thấy khuôn mặt"
    if len(faces2) == 0:
        return "ảnh 2 không tìm thấy khuôn mặt"
    
    #cắt khuôn mặt
    (x1, y1, w1, h1) = faces1[0]  #lấy khuôn mặt trong ảnh
    face1 = image1[y1:y1+h1, x1:x1+w1]

    (x2, y2, w2, h2) = faces2[0]  #lấy khuôn mặt trong ảnh
    face2 = image2[y2:y2+h2, x2:x2+w2]
    
    #resize 2 ảnh khuôn mặt về cùng kích thước
    face1_resized = cv2.resize(face1, (200, 200))
    face2_resized = cv2.resize(face2, (200, 200))

    # So sánh histogram của 2 ảnh khuôn mặt
    hist1 = cv2.calcHist([face1_resized], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([face2_resized], [0], None, [256], [0, 256])

    # Chuẩn hóa histogram
    hist1 = cv2.normalize(hist1, hist1)
    hist2 = cv2.normalize(hist2, hist2)

    # Tính độ tương đồng giữa 2 histogram bằng hàm correlation
    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

    #ngưỡng xác định cùng 1 người hay không
    if similarity > 0.7:
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