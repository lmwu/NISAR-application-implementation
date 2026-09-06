from collections import defaultdict
import asf_search as asf
from shapely.geometry import shape

# 1. 定義六輕 AOI 範圍 (Shapely Polygon)
mailiao_wkt = (
    "POLYGON((120.15 23.75, 120.24 23.75, 120.24 23.83, 120.15 23.83, 120.15 23.75))"
)

# 2. 僅搜尋元數據 (Metadata Search, 不會下載檔案)
print("正在檢索元數據...")
results = asf.geo_search(
    platform=asf.PLATFORM.NISAR,
    processingLevel="GUNW",
    flightDirection="ASCENDING",  # 或 'DESCENDING'
    intersectsWith=mailiao_wkt,
)

# 3. 按 (Relative Orbit, Frame Number) 進行分組統計
grouped_results = defaultdict(list)
for item in results:
    track = item.properties.get("relativeOrbit")
    # 從檔名或 properties 獲取 Frame
    frame = item.properties.get("frameNumber", "Unknown")
    key = f"Track_{track}_Frame_{frame}"
    grouped_results[key].append(item)

# 4. 列出統計結果並找出「最佳黃金組合」
print("\n=== 各軌道與框架的可下數量統計 ===")
best_key = None
max_count = 0

for key, items in grouped_results.items():
    count = len(items)
    print(f"[{key}] : 共 {count} 幅影像")
    if count > max_count:
        max_count = count
        best_key = key

print(f"\n最佳組合選定：{best_key}（共 {max_count} 幅）")

# 5. 只針對「最佳黃金組合」執行精準下載
target_items = asf.GranuleRList(grouped_results[best_key])

print(f"\n開始精準下載 {best_key} 的 {len(target_items)} 個檔案...")
session = asf.ASFSession().login()  # 輸入 ASF 帳號密碼
target_items.download(path="./data_gunw/ASC_Clean", session=session)
print("下載完成！此資料夾可 100% 直攻 MintPy prep_nisar.py。")
