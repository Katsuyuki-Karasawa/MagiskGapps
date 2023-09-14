import os
import json
from pyfastcopy import copytree, copy2
import zipfile
import fnmatch
import shutil


def load_module_info():
    with open("module-info.json") as f:
        contents = json.load(f)
    module_info = contents["result"]
    return module_info


def create_module_prop_file(module_info):
    with open("template/module.prop", "w") as f:
        f.write(
            f'id={module_info["id"]}\nname={module_info["name"]}\nversion={module_info["version"]}\nversionCode={module_info["versionCode"]}\nauthor={module_info["author"]}\ndescription={module_info["description"]}'
        )


def extract_and_move_files():
    with zipfile.ZipFile("gapps.zip", "r") as zip_ref:
        zip_ref.extractall("gapps")

    os.mkdir("AppSet")

    rootPath = r"gapps/AppSet"
    pattern = "*.zip"

    for root, dirs, files in os.walk(rootPath):
        for filename in fnmatch.filter(files, pattern):
            print("Moving " + os.path.join(root, filename))
            with zipfile.ZipFile(os.path.join(root, filename)) as zip_ref:
                zip_ref.extractall(os.path.join("appset/"))
            os.remove("appset/installer.sh")

    os.remove("appset/uninstaller.sh")
    print("Moving files")


def rename_files():
    path = "appset"
    os.chmod(path, 0o777)
    filenames = os.listdir(path)

    for filename in filenames:
        src_file = os.path.join(path, filename)
        dst_file = "appset/" + filename.replace("___", "/")
        print(f"Renaming {src_file} to {dst_file}")
        os.rename(src_file, dst_file)


def build_module(module_info):
    source_folder = r"template"
    destination_folder = r"builds"
    copytree(source_folder, destination_folder)

    source_folder = r"appset"
    destination_folder = r"builds/system"
    copytree(source_folder, destination_folder)
    print("Building Module")

    shutil.make_archive(
        f"releases/MagiskGApps-{module_info['version']}", "zip", "builds"
    )
    print("Building Zip and archiving")


def clean_up():
    shutil.rmtree("gapps", ignore_errors=True)
    shutil.rmtree("builds", ignore_errors=True)
    os.remove("template/module.prop")
    shutil.rmtree("AppSet", ignore_errors=True)


# Main script execution
module_info = load_module_info()
create_module_prop_file(module_info)
extract_and_move_files()
rename_files()
build_module(module_info)
clean_up()
