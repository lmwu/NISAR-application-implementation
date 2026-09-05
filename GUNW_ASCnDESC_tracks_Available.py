import asf_search as asf

# 搜尋六輕涵蓋範圍的 GUNW 資料
results = asf.geo_search(
    platform=asf.PLATFORM.NISAR,
    processingLevel="GUNW",
    intersectsWith="POLYGON((120.15 23.75, 120.24 23.75, 120.24 23.83, 120.15 23.83, 120.15 23.75))",
)

# 分別統計 ASC 與 DESC 的 Relative Orbit 編號與影像數量
asc_tracks = {}
desc_tracks = {}

for item in results:
    properties = item.properties
    flight_dir = properties.get("flightDirection")
    orbit = properties.get("relativeOrbit")

    if flight_dir == "ASCENDING":
        asc_tracks[orbit] = asc_tracks.get(orbit, 0) + 1
    elif flight_dir == "DESCENDING":
        desc_tracks[orbit] = desc_tracks.get(orbit, 0) + 1

print("【升軌 ASC 可用軌道】:", asc_tracks)
print("【降軌 DESC 可用軌道】:", desc_tracks)
