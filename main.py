import os
import json
import shutil
import zipfile
import fnmatch
import pysftp

def load_json(filename):
    with open(filename) as f:
        return json.load(f)['result']

def create_module_prop(template_file, module_info):
    with open(template_file, 'w') as f:
        for key, value in module_info.items():
            f.write(f'{key}={value}\n')

def unzip_and_move_files(zip_filename, extract_folder, appset_folder):
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)
    
    os.mkdir(appset_folder)
    rootPath = os.path.join(extract_folder, "AppSet")
    pattern = '*.zip'

    for root, dirs, files in os.walk(rootPath):
        for filename in fnmatch.filter(files, pattern):
            print(f"Moving {os.path.join(root, filename)}")
            zipfile.ZipFile(os.path.join(root, filename)).extractall("appset/")
            os.remove("appset/installer.sh")
    
    os.remove("appset/uninstaller.sh")

def rename_files(path):
    os.chmod(path, 0o777)
    for filename in os.listdir(path):
        src_file = os.path.join(path, filename)
        dst_file = os.path.join('appset', filename.replace('___', '/'))
        print(f"Renaming {src_file} to {dst_file}")
        shutil.move(src_file, dst_file)

def copy_and_combine_folders(src_folders, dst_folders):
    for src, dst in zip(src_folders, dst_folders):
        shutil.copytree(src, dst)

def clean_up(files, folders):
    for file in files:
        os.remove(file)
    
    for folder in folders:
        shutil.rmtree(folder, ignore_errors=True)

def upload_to_sourceforge(sftp_details, local_path, remote_path):
    with pysftp.Connection(host="frs.sourceforge.net", username=sftp_details['SF_user'], password=sftp_details['SF_pass']) as srv:
        print("Uploading to SourceForge")
        with srv.cd(remote_path): 
            srv.put(local_path) 

def main():
    contents = load_json('module-info.json')
    create_module_prop('template/module.prop', contents)
    
    unzip_and_move_files("gapps.zip", "gapps", "AppSet")
    rename_files("appset")

    src_folders = ["template", "appset"]
    dst_folders = ["builds", "builds/system"]
    copy_and_combine_folders(src_folders, dst_folders)

    version = contents['version']
    shutil.make_archive(f"releases/MagiskGApps-{version}", 'zip', "builds")
    print("Building Zip and archiving")

    chmod_folders = ["gapps", "builds", "AppSet"]
    for folder in chmod_folders:
        os.chmod(folder, 0o777)

    to_remove_files = ["template/module.prop", "gapps.zip"]
    to_remove_folders = ["gapps", "builds", "AppSet"]
    clean_up(to_remove_files, to_remove_folders)

    remote_path = f'/home/frs/project/magiskgapps/{contents["SF_folder"]}/{contents["SF_version"]}'
    local_path = f'releases/MagiskGApps-{version}.zip'
    upload_to_sourceforge(contents, local_path, remote_path)

if __name__ == "__main__":
    main()
