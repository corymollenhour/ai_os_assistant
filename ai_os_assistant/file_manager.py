
import os
import shutil
from datetime import datetime

def rename_files(directory, pattern="append_date"):
    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)
        if os.path.isfile(full_path):
            name, ext = os.path.splitext(filename)
            date_str = datetime.now().strftime("%Y-%m-%d")
            new_name = f"{name}_{date_str}{ext}"
            os.rename(full_path, os.path.join(directory, new_name))
            print(f"Renamed: {filename} -> {new_name}")

def sort_files(directory, file_type, group_by):
    for filename in os.listdir(directory):
        if not filename.lower().endswith(file_type):
            continue

        full_path = os.path.join(directory, filename)
        mtime = os.path.getmtime(full_path)
        dt = datetime.fromtimestamp(mtime)

        if group_by == "year":
            folder_name = str(dt.year)
        elif group_by == "month":
            folder_name = f"{dt.year}-{dt.month:02}"
        else:
            folder_name = "unknown"

        target_folder = os.path.join(directory, folder_name)
        os.makedirs(target_folder, exist_ok=True)
        shutil.move(full_path, os.path.join(target_folder, filename))
        print(f"Moved: {filename} -> {target_folder}")

def create_file(filename, content=""):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created file: {filename}")
