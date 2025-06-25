import json

with open("data/allocDefinitionGA.json") as f:
    alloc = json.load(f)
with open("data/usersDefinition.json") as f:
    users = json.load(f)
with open("data/appDefinition.json") as f:
    apps = json.load(f)

needed = set()
for user in users["sources"]:
    app = str(user["app"])
    node = user["id_resource"]
    msg = user["message"]
    app_obj = next((a for a in apps if a["name"] == app), None)
    if app_obj:
        msg_obj = next((m for m in app_obj["message"] if m["name"] == msg), None)
        if msg_obj:
            mod_dst = msg_obj["d"]
            needed.add((app, mod_dst, node))

filtered = []
for entry in alloc["initialAllocation"]:
    key = (str(entry.get("app")), entry.get("module_name"), entry.get("id_resource"))
    # Untuk module tujuan user, hanya keep jika node user
    if key in needed:
        filtered.append(entry)
    # Untuk module lain, keep semua
    elif all(key[:2] != (n[0], n[1]) for n in needed):
        filtered.append(entry)

with open("data/allocDefinitionGA.filtered.json", "w") as f:
    json.dump({"initialAllocation": filtered}, f, indent=4)

print("allocDefinitionGA.filtered.json sudah dibuat. Pakai file ini untuk simulasi YAFS.")