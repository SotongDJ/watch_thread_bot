from asyncio import threads
import json, tomlkit

record = json.load(open("record.json"))
thread_doc = tomlkit.document()
for id, thread in record.items():
    parent_id_str = str(thread["parent_id"])
    parent_table = thread_doc.get(parent_id_str,tomlkit.table())
    parent_table[str(id)] = thread["name"]
    thread_doc[parent_id_str] = parent_table
with open("thread.toml","w") as toml_handle:
    tomlkit.dump(thread_doc,toml_handle)

settings = json.load(open("settings.json"))
settings_doc = tomlkit.document()
for key,value in settings.items():
    settings_doc[key] = value
with open("settings.toml","w") as toml_handle:
    tomlkit.dump(settings_doc,toml_handle)

