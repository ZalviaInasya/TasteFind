import json
import csv
import os
import glob

class DataMerger:
    def __init__(self):
        self.dataset_folder = "dataset"
        self.output_json = "semua.json"
        self.output_csv = "semua.csv"

    def merge_data(self):
        print("="*60)
        print("🔄 MEMULAI PENGGABUNGAN DATASET")
        print("="*60)

        # Cari semua file .json di dalam folder dataset
        # Kita menggunakan JSON sebagai sumber utama karena format list (bahan/langkah) lebih aman
        json_pattern = os.path.join(self.dataset_folder, "*.json")
        files = glob.glob(json_pattern)
        
        all_data = []
        new_id = 1
        
        # Urutan header prioritas untuk CSV agar rapi
        field_order = [
            "id", "type", "judul", "tanggal", "kategori", 
            "deskripsi", "url_gambar", "url_link", "bahan", "langkah"
        ]
        
        # Set untuk menampung semua key yang mungkin ada (jika ada key tambahan di berita)
        all_keys = set(field_order)

        for file_path in files:
            # Skip jika file output sendiri ada di folder tersebut (menghindari duplikasi)
            if "semua.json" in file_path:
                continue
                
            print(f"   📂 Membaca: {os.path.basename(file_path)}...")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Cek apakah data berupa list atau object tunggal
                    if isinstance(data, list):
                        for item in data:
                            # Update ID menjadi urut
                            item['id'] = new_id
                            
                            # Normalisasi data (jika berita tidak punya bahan/langkah, isi dengan list kosong/string kosong)
                            if 'bahan' not in item: item['bahan'] = []
                            if 'langkah' not in item: item['langkah'] = []
                            
                            # Kumpulkan semua key untuk header CSV
                            all_keys.update(item.keys())
                            
                            all_data.append(item)
                            new_id += 1
                    else:
                        print(f"      ⚠️  Format file {file_path} bukan list JSON.")
                        
            except Exception as e:
                print(f"      ❌ Gagal membaca {file_path}: {e}")

        print(f"\n   ✅ Total data terkumpul: {len(all_data)} items")

        # --- SIMPAN KE JSON ---
        output_json_path = os.path.join(self.dataset_folder, self.output_json)
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"   💾 JSON Disimpan: {output_json_path}")

        # --- SIMPAN KE CSV ---
        # Mengatur urutan kolom: Prioritas field_order, sisanya taruh di belakang
        sorted_fieldnames = [k for k in field_order if k in all_keys]
        remaining_keys = [k for k in all_keys if k not in field_order]
        final_headers = sorted_fieldnames + remaining_keys

        output_csv_path = os.path.join(self.dataset_folder, self.output_csv)
        
        with open(output_csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=final_headers)
            writer.writeheader()
            
            for item in all_data:
                row = item.copy()
                
                # Konversi LIST menjadi STRING agar bisa masuk satu sel CSV
                # Contoh: ['Garam', 'Gula'] menjadi "Garam | Gula"
                if isinstance(row.get('bahan'), list):
                    row['bahan'] = ' | '.join(row['bahan'])
                
                if isinstance(row.get('langkah'), list):
                    row['langkah'] = ' | '.join(row['langkah'])
                
                writer.writerow(row)
                
        print(f"   💾 CSV Disimpan : {output_csv_path}")
        print("="*60)
        print("🎉 SELESAI! Semua data telah digabung.")

if __name__ == "__main__":
    merger = DataMerger()
    merger.merge_data()