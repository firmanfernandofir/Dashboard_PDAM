+import pandas as pd
+import numpy as np
+import json
+
+# Path file
+file_path = "/vercel/sandbox/Data Evaluasi Cabang PDAM.xlsx"
+
+# Baca semua sheet
+xls = pd.ExcelFile(file_path)
+all_sheets = xls.sheet_names
+
+# Filter hanya sheet bulan (bukan "Per Hari")
+bulan_sheets = [s for s in all_sheets if "Per Hari" not in s]
+
+print(f"Sheet bulan yang tersedia: {bulan_sheets}")
+
+# Fungsi untuk membersihkan angka
+def clean_number(val):
+    if pd.isna(val) or val == '':
+        return 0
+    if isinstance(val, str):
+        val = val.replace(',', '').replace('.', '').strip()
+        try:
+            return float(val)
+        except:
+            return 0
+    return float(val)
+
+# Baca semua data bulan
+data_bulan = {}
+for sheet in bulan_sheets:
+    df = pd.read_excel(file_path, sheet_name=sheet)
+    df.columns = df.columns.str.strip()
+    
+    # Cari kolom yang relevan
+    cabang_col = 'CABANG'
+    
+    # Identifikasi kolom bulan ini
+    bulan_name = sheet.upper()
+    
+    # Cari kolom pelanggan, konsumsi, distribusi, terjual, pendapatan
+    pelanggan_col = [c for c in df.columns if 'JUMLAH PELANGGAN BULAN' in c and bulan_name in c.upper()]
+    konsumsi_gol2_col = [c for c in df.columns if 'KONSUMSI GOL 2 BULAN' in c and bulan_name in c.upper()]
+    konsumsi_total_col = [c for c in df.columns if 'KONSUMSI TOTAL BULAN' in c and bulan_name in c.upper()]
+    distribusi_col = [c for c in df.columns if 'AIR DISTRIBUSI BULAN' in c and bulan_name in c.upper()]
+    terjual_col = [c for c in df.columns if 'AIR TERJUAL BULAN' in c and bulan_name in c.upper()]
+    pendapatan_col = [c for c in df.columns if 'PENDAPATAN AIR BULAN' in c and bulan_name in c.upper()]
+    
+    # Buat dataframe bersih
+    clean_data = []
+    for idx, row in df.iterrows():
+        cabang = row[cabang_col]
+        if pd.isna(cabang) or cabang == 'TOTAL':
+            continue
+            
+        data_row = {
+            'CABANG': cabang,
+            'PELANGGAN': clean_number(row[pelanggan_col[0]]) if pelanggan_col else 0,
+            'KONSUMSI_GOL2': clean_number(row[konsumsi_gol2_col[0]]) if konsumsi_gol2_col else 0,
+            'KONSUMSI_TOTAL': clean_number(row[konsumsi_total_col[0]]) if konsumsi_total_col else 0,
+            'DISTRIBUSI': clean_number(row[distribusi_col[0]]) if distribusi_col else 0,
+            'TERJUAL': clean_number(row[terjual_col[0]]) if terjual_col else 0,
+            'PENDAPATAN': clean_number(row[pendapatan_col[0]]) if pendapatan_col else 0,
+        }
+        
+        # Hitung ATR (Tingkat Kehilangan Air)
+        if data_row['DISTRIBUSI'] > 0:
+            data_row['ATR'] = ((data_row['DISTRIBUSI'] - data_row['TERJUAL']) / data_row['DISTRIBUSI']) * 100
+        else:
+            data_row['ATR'] = 0
+            
+        clean_data.append(data_row)
+    
+    data_bulan[sheet] = pd.DataFrame(clean_data)
+    print(f"✓ Berhasil membaca {sheet}: {len(clean_data)} cabang")
+
+# Simpan data ke JSON untuk dashboard
+output_data = {}
+for bulan, df in data_bulan.items():
+    output_data[bulan] = df.to_dict('records')
+
+with open('/vercel/sandbox/pdam_data.json', 'w') as f:
+    json.dump(output_data, f, indent=2)
+
+print("\n✓ Data berhasil dianalisis dan disimpan ke pdam_data.json")
+print(f"Total bulan: {len(data_bulan)}")

diff --git a/dashboard_pdam.html b/dashboard_pdam.html
new file mode 100644
index 0000000..8eecd08
--- /dev/null
