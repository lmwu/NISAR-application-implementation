import glob
import os
import h5py
from pyproj import Transformer

# 台灣 UTM Zone 51N (EPSG:32651) 轉 WGS84 經緯度 (EPSG:4326)
transformer = Transformer.from_crs("EPSG:32651", "EPSG:4326", always_xy=True)
mailiao_bounds = [
    120.15,
    120.24,
    23.75,
    23.83,
]  # [lon_min, lon_max, lat_min, lat_max]


def find_coords(h5_file):
    x_ds, y_ds = None, None

    def visitor(name, obj):
        nonlocal x_ds, y_ds
        if isinstance(obj, h5py.Dataset):
            basename = os.path.basename(name).lower()
            if basename in ["xcoordinates", "xcoordinate", "x"]:
                x_ds = obj
            elif basename in ["ycoordinates", "ycoordinate", "y"]:
                y_ds = obj

    h5_file.visititems(visitor)
    return x_ds, y_ds


files = sorted(glob.glob("data_gunw/ASC/*.h5"))
print(f"=== 萬用版：檢查 {len(files)} 個檔案的實際涵蓋範圍 ===\n")

for fpath in files:
    fname = os.path.basename(fpath)
    try:
        with h5py.File(fpath, "r") as f:
            x_ds, y_ds = find_coords(f)

            if x_ds is None or y_ds is None:
                print(f"檔名: {fname}\n  ❌ 無法定位 X/Y 座標 Dataset\n")
                continue

            x, y = x_ds[()], y_ds[()]

            # 轉換 UTM 邊界值至經緯度
            lon1, lat1 = transformer.transform(x.min(), y.min())
            lon2, lat2 = transformer.transform(x.max(), y.max())

            min_lon, max_lon = min(lon1, lon2), max(lon1, lon2)
            min_lat, max_lat = min(lat1, lat2), max(lat1, lat2)

            covers_mailiao = (
                (min_lon <= mailiao_bounds[0])
                and (max_lon >= mailiao_bounds[1])
                and (min_lat <= mailiao_bounds[2])
                and (max_lat >= mailiao_bounds[3])
            )

            status = "✅ 涵蓋六輕" if covers_mailiao else "❌ 未涵蓋六輕"
            print(f"檔名: {fname}")
            print(
                f"  經緯度範圍: Lon[{min_lon:.2f}, {max_lon:.2f}], Lat[{min_lat:.2f},"
                f" {max_lat:.2f}] --> {status}\n"
            )

    except Exception as e:
        print(f"檔名: {fname}\n  ❌ 讀取失敗: {e}\n")
