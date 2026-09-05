import glob
import os

files = sorted(glob.glob("data_gunw/DESC/*.h5"))
print(f"=== 檢查 {len(files)} 個升軌 GUNW 檔案的 Track/Frame 組合 ===\n")

groups = {}
for fpath in files:
    fname = os.path.basename(fpath)
    parts = fname.split("_")
    # NISAR 檔名結構範例: NISAR_L2_PR_GUNW_006_039_A_...
    # parts[4] 為 Track, parts[5] 為 Frame
    if len(parts) >= 6:
        key = f"Track_{parts[4]}_Frame_{parts[5]}"
    else:
        key = "Unknown"
    groups.setdefault(key, []).append(fname)

for tf, f_list in groups.items():
    print(f"【{tf}】共 {len(f_list)} 個檔案：")
    for f in f_list:
        print(f"  - {f}")
    print()
