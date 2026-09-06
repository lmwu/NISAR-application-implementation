import os
from collections import defaultdict
import asf_search as asf

def main():

    outputA_dir = './data_gunw/ASC'
    os.makedirs(outputA_dir, exist_ok=True)
    outputD_dir = './data_gunw/DESC'
    os.makedirs(outputD_dir, exist_ok=True)

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

# 3. 從檔名解析 Track (parts[4]) 與 Frame (parts[5])
    grouped_results = defaultdict(list)
    for item in results:
        scene_name = item.properties.get("sceneName", "")
        parts = scene_name.split("_")

    # 範例: NISAR_L2_PR_GUNW_024_039_A_...
        if len(parts) >= 6:
            track = parts[4]
            frame = parts[5]
        else:
            track = "Unknown"
            frame = "Unknown"

        key = f"Track_{track}_Frame_{frame}"
        grouped_results[key].append(item)

# 4. 印出真正的 Track/Frame 統計與下載
    print("\n=== 各軌道與框架的可下數量統計 ===")
    for key, items in grouped_results.items():
        print(f"[{key}] : 共 {len(items)} 幅影像")

    best_key = max(grouped_results, key=lambda k: len(grouped_results[k]))
    target_items = asf.ASFSearchResults(grouped_results[best_key])
    print(f"\n最佳組合選定：{best_key}（共 {len(target_items)} 幅影像）")

    print(f"\n開始精準下載 {best_key} 的 {len(target_items)} 個檔案...")

    target_items.download(path=outputA_dir)  # 或 outputD_dir
    print("下載完成！")

if __name__ == '__main__':
    main()
