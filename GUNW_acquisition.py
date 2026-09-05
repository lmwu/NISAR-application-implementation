import os
import asf_search as asf

# 1. 自動建立目標下載資料夾
output_dir = './data_gunw'
os.makedirs(output_dir, exist_ok=True)

# 2. 定義六輕 AOI 並檢索數據
mailiao_aoi = 'POLYGON((120.15 23.75, 120.24 23.75, 120.24 23.83, 120.15 23.83, 120.15 23.75))'

results = asf.search(
    platform=asf.PLATFORM.NISAR,
    processingLevel='GUNW',
    intersectsWith=mailiao_aoi
)

print(f"搜尋到 {len(results)} 幅 GUNW 影像，準備開始下載...")

# 3. 執行批次下載
results.download(
    path=output_dir,
    processes=4
)
