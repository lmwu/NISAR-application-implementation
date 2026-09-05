import glob
import os
import h5py
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Transformer

# 1. 取得第一個 HDF5 檔案
files = sorted(glob.glob("./data_gunw/DESC/*.h5") + glob.glob("./data_gunw/*.nc"))
if not files:
    raise FileNotFoundError("./data_gunw/DESC 目錄內找不到 .h5 或 .nc 檔案！")

file_path = files[0]
print(f"正讀取檔案：{os.path.basename(file_path)}")

# 2. 開啟 HDF5 並提取資料集
with h5py.File(file_path, "r") as f:
    datasets = {}
    f.visititems(
        lambda name, obj: datasets.update({name: obj})
        if isinstance(obj, h5py.Dataset) and obj.ndim > 0
        else None
    )

    unw_path = next((k for k in datasets if "unwrappedPhase" in k), None)
    coh_path = next(
        (k for k in datasets if "coherence" in k or "coherenceMagnitude" in k),
        None,
    )

    unw = np.squeeze(f[unw_path][:])
    coh = np.squeeze(f[coh_path][:]) if coh_path else np.ones_like(unw)

    h, w = unw.shape[-2], unw.shape[-1]
    x_path = next(
        (
            k
            for k in datasets
            if datasets[k].ndim == 1 and datasets[k].shape[0] == w
        ),
        None,
    )
    y_path = next(
        (
            k
            for k in datasets
            if datasets[k].ndim == 1 and datasets[k].shape[0] == h
        ),
        None,
    )

    xs = f[x_path][:]
    ys = f[y_path][:]

# 3. 修正 Y 軸南北顛倒問題 (若 Y 值由大到小，執行矩陣與座標垂直翻轉)
if ys[0] > ys[-1]:
    ys = ys[::-1]
    unw = np.flipud(unw)
    coh = np.flipud(coh)

# 4. UTM 坐標轉 WGS84 經緯度 (台灣主要落在 UTM Zone 51N / EPSG:32651)
epsg_code = 32651
transformer_to_utm = Transformer.from_crs(
    "EPSG:4326", f"EPSG:{epsg_code}", always_xy=True
)
transformer_to_geo = Transformer.from_crs(
    f"EPSG:{epsg_code}", "EPSG:4326", always_xy=True
)

# 將六輕 WGS84 經緯度轉為 UTM 公尺坐標進行精準裁切
lon_min, lon_max = 120.15, 120.24
lat_min, lat_max = 23.75, 23.83

utm_x1, utm_y1 = transformer_to_utm.transform(lon_min, lat_min)
utm_x2, utm_y2 = transformer_to_utm.transform(lon_max, lat_max)

x_idx = np.where(
    (xs >= min(utm_x1, utm_x2)) & (xs <= max(utm_x1, utm_x2))
)[0]
y_idx = np.where(
    (ys >= min(utm_y1, utm_y2)) & (ys <= max(utm_y1, utm_y2))
)[0]

if len(x_idx) > 0 and len(y_idx) > 0:
    c1, c2 = x_idx.min(), x_idx.max() + 1
    r1, r2 = y_idx.min(), y_idx.max() + 1
    sub_unw = unw[r1:r2, c1:c2]
    sub_coh = coh[r1:r2, c1:c2]

    # 計算裁切區域的實際經緯度範圍
    crop_lon_min, crop_lat_min = transformer_to_geo.transform(
        xs[c1], ys[r1]
    )
    crop_lon_max, crop_lat_max = transformer_to_geo.transform(
        xs[c2 - 1], ys[r2 - 1]
    )
    extent = [crop_lon_min, crop_lon_max, crop_lat_min, crop_lat_max]
else:
    sub_unw, sub_coh = unw, coh
    geo_x1, geo_y1 = transformer_to_geo.transform(xs.min(), ys.min())
    geo_x2, geo_y2 = transformer_to_geo.transform(xs.max(), ys.max())
    extent = [geo_x1, geo_x2, geo_y1, geo_y2]

# 5. 繪製圖表 (X/Y 軸顯示真實經緯度)
fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)

im1 = axes[0].imshow(
    sub_coh, extent=extent, cmap="gray", vmin=0, vmax=1, origin="lower"
)
axes[0].set_title("Coherence Magnitude")
axes[0].set_xlabel("Longitude (°E)")
axes[0].set_ylabel("Latitude (°N)")
fig.colorbar(im1, ax=axes[0], label="Coherence")

im2 = axes[1].imshow(sub_unw, extent=extent, cmap="rainbow", origin="lower")
axes[1].set_title("Unwrapped Phase (rad)")
axes[1].set_xlabel("Longitude (°E)")
fig.colorbar(im2, ax=axes[1], label="Phase (rad)")

plt.suptitle(f"NISAR GUNW QC - Mailiao Area\n{os.path.basename(file_path)}")
plt.tight_layout()
plt.savefig("./mailiao_gunw_qc_DESC.png", dpi=300)
plt.show()
print("QC 圖表已修復 orientation 與坐標系，並儲存至 ./mailiao_gunw_qc_DESC.png")
