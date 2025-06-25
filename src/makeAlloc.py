import json

# 1. Mapping index global -> (app_name, module_name)
mapping = {
    0: ('0', '0_0'),
    1: ('0', '0_1'),
    2: ('0', '0_2'),
    # ... (copy mapping sampai 237 seperti milikmu)
    237: ('19', '19_237')
}

# 2. Hasil GA-mu (contoh random, GANTI dengan hasilmu)
# Panjangnya HARUS sama dengan jumlah modul (238 di contoh ini)
ga_solution = [10, 20, 3, 1, 1, 5, 6, 2, 1, 5, 3, 2, 1, 12, 4, 1, 1, 5, 2, 6, 9, 4, 10, 2, 7, 1, 12, 3, 2, 5, 9, 1, 8, 5, 4, 6, 9, 8, 1, 2, 3, 5, 6, 7, 12, 1, 3, 4, 2, 7, 9, 1, 8, 5, 2, 3, 1, 4, 5, 7, 8, 1, 4, 2, 3, 10, 12, 1, 8, 5, 2, 7, 1, 3, 4, 2, 8, 5, 10, 1, 2, 3, 5, 12, 7, 1, 8, 9, 4, 6, 3, 2, 1, 5, 12, 4, 7, 1, 3, 4, 2, 5, 6, 1, 8, 3, 4, 2, 10, 7, 1, 3, 4, 6, 2, 1, 5, 3, 7, 8, 1, 4, 2, 3, 10, 7, 1, 5, 4, 2, 6, 1, 3, 4, 2, 7, 8, 9, 1, 4, 2, 3, 5, 10, 1, 4, 2, 7, 12, 1, 3, 4, 2, 5, 1, 8, 3, 4, 2, 7, 1, 3, 4, 2, 5, 6, 12, 1, 8, 3, 4, 2, 10, 1, 3, 4, 2, 7, 8, 1, 4, 2, 3, 5, 12, 1, 8, 5, 2, 7, 1, 3, 4, 2, 8, 5, 10, 1, 2, 3, 5, 12, 7, 1, 8, 9, 4, 6, 3, 2, 1, 5, 12, 4, 7, 1, 3, 4, 2, 5, 6, 1, 8, 3, 4, 2, 10, 7, 1, 3, 4, 6, 2, 1, 5, 3, 7, 8, 1, 4, 2, 3, 10, 7, 1, 5, 4, 2, 6, 1, 3, 4, 2, 7, 8, 9, 1, 4, 2, 3, 5, 10, 1, 4, 2, 7, 12, 1, 3, 4, 2, 5, 1, 8, 3, 4, 2, 7, 1, 3, 4, 2, 5, 6, 12, 1, 8, 3, 4, 2, 10]  # <-- GANTI dengan hasil GA-mu

# 3. Build alloc json YAFS
alloc_list = []
for idx, node_id in enumerate(ga_solution):
    app_name, module_name = mapping[idx]
    alloc_list.append({
        "app_name": app_name,
        "module_name": module_name,
        "id_resource": node_id  # node penempatan hasil GA
    })

alloc_json = {
    "initialAllocation": alloc_list
}

# 4. Tulis ke file
with open("allocDefinition.json", "w") as f:
    json.dump(alloc_json, f, indent=2)

print("allocDefinition.json siap dipakai di YAFS!")