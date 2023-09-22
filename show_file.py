import rasterio
import matplotlib.pyplot as plt
import numpy as np

def show_tif_image(file_path):
    with rasterio.open(file_path) as src:
        # Đọc dữ liệu ảnh từ file .tif
        img = src.read(1)  # Đọc band đầu tiên, thay đổi số 1 nếu bạn muốn đọc band khác

        # Hiển thị ảnh
        plt.imshow(img, cmap='gray')  # Sử dụng cmap khác nếu bạn muốn
        plt.colorbar()
        plt.show()      

# Sử dụng hàm
file_path = "F:/NCKH/Nam5/GEE/img/Landsat_LC09_127047_20230901.tif"
show_tif_image(file_path)


