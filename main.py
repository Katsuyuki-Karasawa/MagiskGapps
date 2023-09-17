import os
import json
import shutil
import zipfile
import fnmatch

with open("module-info.json") as f:
    contents = json.load(f)
id = contents["result"]["id"]
name = contents["result"]["name"]
version = contents["result"]["version"]
versionCode = contents["result"]["versionCode"]
author = contents["result"]["author"]
description = contents["result"]["description"]

# Create module.prop
with open("template/module.prop", "w") as f:
    f.write(
        "id="
        + id
        + "\n"
        + "name="
        + name
        + "\n"
        + "version="
        + version
        + "\n"
        + "versionCode="
        + versionCode
        + "\n"
        + "author="
        + author
        + "\n"
        + "description="
        + description
    )

# Unzip and move AppSet files
with zipfile.ZipFile(os.path.join(".", "gapps.zip"), "r") as zip_ref:
    zip_ref.extractall("gapps")

# Define the appsetPath variable to point to the 'appset' directory
appsetPath = os.path.join(".", "appset")

# Check if the 'appset' directory exists before proceeding
if not os.path.exists(appsetPath):
    os.makedirs(appsetPath)

rootPath = os.path.join("gapps", "AppSet")
pattern = "*.zip"
for root, dirs, files in os.walk(rootPath):
    for filename in fnmatch.filter(files, pattern):
        print("Moving " + os.path.join(root, filename))
        zipfile.ZipFile(os.path.join(root, filename)).extractall(os.path.join("appset"))
        os.remove("appset/installer.sh")
        os.remove("appset/uninstaller.sh")
print("Moving files")

# Renames Files from ___ to /
path = "appset"
os.chmod(path, 0o777)
for filename in os.listdir(appsetPath):
    src_file = os.path.join(appsetPath, filename)
    dst_file = os.path.join(appsetPath, filename.replace("___", os.sep).lstrip(os.sep))

    # Check if the destination directory exists, if not create it
    dst_dir = os.path.dirname(dst_file)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    if os.path.exists(dst_file):
        if os.path.isdir(dst_file):
            shutil.rmtree(dst_file)
        else:
            os.remove(dst_file)

    shutil.move(src_file, dst_file)


# Combines everything
source_folder = r"template"
destination_folder = r"builds"
shutil.copytree(source_folder, destination_folder)

source_folder = r"appset"
destination_folder = r"builds/system"
shutil.copytree(source_folder, destination_folder)
print("Building Module")

shutil.make_archive("releases/MagiskGApps-" + version, "zip", "builds")
print("Building Zip and archiving")
os.chmod("gapps", 0o777)
os.chmod("builds", 0o777)
os.chmod("AppSet", 0o777)

shutil.rmtree("gapps", ignore_errors=True)
shutil.rmtree("builds", ignore_errors=True)
os.remove(os.path.join("template", "module.prop"))
shutil.rmtree("AppSet", ignore_errors=True)
