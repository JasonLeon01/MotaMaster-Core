import json
import os
from PySFBoost import *
import shutil
import zipfile

def create_nested_dict(path_parts, value):
    if len(path_parts) == 1:
        return {path_parts[0]: value}
    return {path_parts[0]: create_nested_dict(path_parts[1:], value)}

def merge_dicts(dict1, dict2):
    for key in dict2:
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            merge_dicts(dict1[key], dict2[key])
        else:
            dict1[key] = dict2[key]

def load_assets_to_dict(assets_folder):
    assets_dict = {}
    for root, dirs, files in os.walk(assets_folder):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, assets_folder)
                path_parts = relative_path.replace('\\', '/').split('/')

                image = sfGraphics.Image()
                success = image.load_from_file(file_path)
                if not success:
                    print(f'Access failed: {file_path}')
                    continue

                _, ext = os.path.splitext(file)
                format = ext[1:].lower()
                try:
                    memory_data = bytes(image.save_to_memory(format))
                    nested_dict = create_nested_dict(path_parts, memory_data)
                    merge_dicts(assets_dict, nested_dict)
                except TypeError as e:
                    print(f'Failed to save at {file_path}, {e}')
                    continue

    return assets_dict

def save_asset_dict_to_mtpak(data_dict, output_file):
    try:
        with open(output_file, 'wb') as f:
            import pickle
            pickle.dump(data_dict, f)
        print(f'Successfully save to {output_file}')
    except pickle.PickleError as e:
        print(f'Save failed: {e}')

def load_data_to_dict(data_folder):
    data_dict = {}
    for root, dirs, files in os.walk(data_folder):
        for file in files:
            if file.lower().endswith('.json'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, data_folder)
                path_without_ext = os.path.splitext(relative_path)[0]
                path_parts = path_without_ext.replace('\\', '/').split('/')

                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    nested_dict = create_nested_dict(path_parts, data)
                    merge_dicts(data_dict, nested_dict)

    return data_dict

def save_data_dict_to_mtpak(data_dict, output_file):
    try:
        with open(output_file, 'wb') as f:
            import pickle
            pickle.dump(data_dict, f)
        print(f'Successfully save to {output_file}')
    except pickle.PickleError as e:
        print(f'Save failed: {e}')

def create_game_package(output_zip):
    try:
        temp_dir = 'temp_package'
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        folders_to_copy = ['assets/fonts', 'assets/musics', 'assets/sounds',
                          'assets/voices', 'PySFBoost', 'scripts']

        def ignore_patterns(path, names):
            patterns = ['.git', '__pycache__', '.pytest_cache']
            return [name for name in names if name in patterns or name.endswith('.pyi')]

        for folder in folders_to_copy:
            if os.path.exists(folder):
                dst = os.path.join(temp_dir, folder)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copytree(folder, dst, ignore=ignore_patterns)

        files_to_copy = ['assets.mtpak', 'data.mtpak', 'main.py', 'mota.ini', 'mota.exe']
        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy2(file, os.path.join(temp_dir, file))

        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)

        shutil.rmtree(temp_dir)
        print(f'Successfully created package: {output_zip}')

        for mtpak in ['assets.mtpak', 'data.mtpak']:
            if os.path.exists(mtpak):
                os.remove(mtpak)
                print(f'Removed {mtpak}')

    except Exception as e:
        print(f'Package creation failed: {e}')

def get_game_name():
    try:
        with open('data/configs/system.json', 'r', encoding='utf-8') as f:
            system_config = json.load(f)
            return system_config.get('title_name', 'game_package')
    except Exception as e:
        print(f'Failed to read system config: {e}')
        return 'game_package'

if __name__ == '__main__':
    assets_folder = 'assets'
    data_folder = 'data'
    output_assets_file = 'assets.mtpak'
    output_data_file = 'data.mtpak'

    game_name = get_game_name()
    output_zip = f'{game_name}.zip'

    assets_dict = load_assets_to_dict(assets_folder)
    save_asset_dict_to_mtpak(assets_dict, output_assets_file)
    data_dict = load_data_to_dict(data_folder)
    save_data_dict_to_mtpak(data_dict, output_data_file)

    create_game_package(output_zip)
