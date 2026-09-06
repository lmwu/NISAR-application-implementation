import os
import asf_search as asf

def main():

# 1. 自動建立目標下載資料夾
	output_dir = './data_gunw'
	os.makedirs(output_dir, exist_ok=True)


# 2. 定義六輕地理多邊形 (Polygon)
	mailiao_aoi = "POLYGON((120.15 23.75, 120.24 23.75, 120.24 23.83, 120.15 23.83, 120.15 23.75))"

# 3. 搜尋 Track 24 且確實涵蓋六輕的升軌 GUNW 影像
	print("正在搜尋涵蓋六輕的 Track 24 升軌資料...")
	resultsA = asf.geo_search(
	    platform=asf.PLATFORM.NISAR,
	    processingLevel="GUNW",
	    flightDirection="ASCENDING",
	    relativeOrbit=24,
	    intersectsWith=mailiao_aoi,
	)

	print(f"共找到 {len(results)} 幅符合六輕邊界的跨日期 GUNW 檔案。")

# 4. 執行下載至指定資料夾
	
	resultsA.download(path=output_dir, processes=4)


# 3-1. 搜尋 Track 24 且確實涵蓋六輕的降軌 GUNW 影像
	print("正在搜尋涵蓋六輕的 Track 24 升軌資料...")
	resultsD = asf.geo_search(
	    platform=asf.PLATFORM.NISAR,
	    processingLevel="GUNW",
	    flightDirection="DESCENDING",
	    relativeOrbit=24,
	    intersectsWith=mailiao_aoi,
	)

	print(f"共找到 {len(results)} 幅符合六輕邊界的跨日期 GUNW 檔案。")

# 4-1. 執行下載至指定資料夾
	
	resultsD.download(path=output_dir, processes=4)

if __name__ == '__main__':
    main()
