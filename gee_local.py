import ee
import time
import pandas as pd
from google.oauth2.service_account import Credentials  
from googleapiclient.discovery import build
import google.auth.transport.requests
import os

def create_folder_and_data_file(folder_name):
    # Tạo thư mục trên Google Drive
    # ... (bạn có thể đã có hàm tạo thư mục trên Google Drive)

    # Tạo thư mục trên máy cục bộ
    local_folder_path = os.path.join('list_name_file_local', folder_name)
    if not os.path.exists(local_folder_path):
        os.makedirs(local_folder_path)

    # Tạo hoặc mở file data.txt để ghi
    data_file_path = os.path.join(local_folder_path, 'data.txt')
    if not os.path.exists(data_file_path):
        with open(data_file_path, 'w') as file:
            pass

def save_image_name_to_data_file(folder_name, image_name):
    data_file_path = os.path.join('list_name_file_local', folder_name, 'data.txt')
    with open(data_file_path, 'a') as file:
        file.write(image_name + '\n')

def check_image_in_local_data(folder_name, image_name):
    data_file_path = os.path.join('list_name_file_local', folder_name, 'data.txt')
    if not os.path.exists(data_file_path):
        return False

    with open(data_file_path, 'r') as file:
        content = file.read()
        return image_name in content
    
def convert_to_int16(image):
    # Chọn các bands bạn muốn chuyển đổi. Ví dụ: 'B1', 'B2', ...
    bands_to_convert = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10', 'B11']
    converted_image = image.select(bands_to_convert).toInt16()
    
    # Thêm lại các bands khác mà bạn không muốn chuyển đổi
    other_bands = image.select(['pixel_qa'])  # Ví dụ, bạn có thể chỉ định các bands khác ở đây
    return converted_image.addBands(other_bands)

def download_image_to_local(roi, img, description, folder_path):
    # """Tải ảnh xuống máy cục bộ."""
    task = ee.batch.Export.image.toLocal(
        image=img,
        description=description,
        path=folder_path,
        scale=30,
        region=roi.getInfo()['coordinates'],
        fileFormat='GeoTIFF',
        maxPixels=1e13
    )
    task.start()

    while task.active():
        print('Polling for task (id: {}).'.format(task.id))
        time.sleep(5)

    task_status = task.status()
    print('Task completed with status: ' + task_status['state'])

    # In ra thông điệp lỗi nếu nhiệm vụ thất bại
    if task_status['state'] == 'FAILED':
        print('Error message: ' + task_status['error_message'])

def download_image_to_local(image, roi, filename):
    url = image.getDownloadURL({
        'scale': 30,
        'crs': 'EPSG:4326',
        'fileFormat': 'GeoTIFF',
        'region': roi.getInfo()['coordinates']
    })

    # Sử dụng URL này để tải xuống ảnh bằng một công cụ tải về như requests hoặc wget
    print("Download URL:", url)

    # Ví dụ sử dụng requests để tải ảnh:
    import requests
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)


def getImageGEE(lon_right, lat_up, lon_left, lat_bottom, date_start, date_end, folder):
    # Khởi tạo Earth Engine
    ee.Initialize()
    print(lon_left, lat_bottom, lon_right, lat_up )
    # Xác định khu vực quan tâm (Region of Interest, ROI)
    roi = ee.Geometry.Rectangle([lon_left, lat_bottom, lon_right, lat_up])
    create_folder_and_data_file(folder)
    # Lấy hình ảnh Landsat 8 dựa trên bộ lọc ngày và khu vực
    image_collection = (ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
                        .filterDate(date_start, date_end)
                        .filterBounds(roi)
                        .sort('CLOUD_COVER'))
    # Duyệt qua từng hình ảnh trong bộ sưu tập
    images_info = image_collection.getInfo()['features']

    for img_info in images_info:
        image = ee.Image(img_info['id'])
        extracted_name = img_info['id'].split('/')[-1]
        description = f"Landsat_{extracted_name}"
        local_folder_path = os.path.join('data_download', folder)
        if not os.path.exists(local_folder_path):
            os.makedirs(local_folder_path)
            
        if not check_image_in_local_data(folder, description):
            download_image_to_local(roi, image.toInt16(), description, local_folder_path)
            save_image_name_to_data_file(folder, description)
    
def getData():
    df = pd.read_excel('data.xlsx', engine='openpyxl')

# Duyệt qua từng dòng trong DataFrame
    for index, row in df.iterrows():
        longitude = row['Kinh độ phải']  # Thay đổi 'kinh độ' thành tên cột thích hợp trong tệp Excel của bạn
        latitude = row['Vĩ độ dưới']    # Thay đổi 'vĩ độ' thành tên cột thích hợp
        time = row['Vùng']    # Thay đổi 'thời gian' thành tên cột thích hợp

        # Làm gì đó với dữ liệu, ví dụ:
        print(longitude, latitude, time)

if __name__ == '__main__':

    df = pd.read_excel('data.xlsx', engine='openpyxl')
    # Duyệt qua từng dòng trong DataFrame
    for index, row in df.iterrows():
        longitude_right = row['Kinh độ phải'] 
        longitude_left = row['Kinh độ trái']  # Thay đổi 'kinh độ' thành tên cột thích hợp trong tệp Excel của bạn
        latitude_bottom = row['Vĩ độ dưới']  
        latitude_up = row['Vĩ độ trên']  # Thay đổi 'vĩ độ' thành tên cột thích hợp
        distinct = row['Vùng'] 
        getImageGEE(longitude_right, latitude_up, longitude_left, latitude_bottom, '2023-08-01', '2023-09-20', f"{distinct}")
