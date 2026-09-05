import rasterio
from dem_stitcher import stitch_dem

# 1. 設定六輕涵蓋範圍 [經度最小值, 緯度最小值, 經度最大值, 緯度最大值]
bounds = [120.0, 23.6, 120.4, 24.0]

# 2. 自動拼接與下載 Copernicus GLO-30 DEM (並自動轉換為 WGS84 橢球高)
print("正從 AWS / OpenTopography 下載 Copernicus GLO-30 DEM...")
X, profile = stitch_dem(bounds, dem_name="glo_30", dst_ellipsoidal_height=True)

# 3. 寫入為 GeoTIFF 檔案
dem_path = "./dem_mailiao.tif"
with rasterio.open(dem_path, "w", **profile) as ds:
    ds.write(X, 1)

print(f"DEM 成功下載並儲存至：{dem_path}")
