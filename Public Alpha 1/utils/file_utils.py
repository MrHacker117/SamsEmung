import os
import shutil
import logging
import zipfile

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        logging.info(f"Created directory: {path}")

def delete_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        logging.info(f"Deleted directory: {path}")

def copy_file(src, dst):
    shutil.copy2(src, dst)
    logging.info(f"Copied file from {src} to {dst}")

def move_file(src, dst):
    shutil.move(src, dst)
    logging.info(f"Moved file from {src} to {dst}")

def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    logging.info(f"Extracted {zip_path} to {extract_to}")

def get_file_size(file_path):
    return os.path.getsize(file_path)

def list_files(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def list_directories(directory):
    return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

def is_file_empty(file_path):
    return os.path.getsize(file_path) == 0

def get_file_extension(file_path):
    return os.path.splitext(file_path)[1]

def rename_file(old_name, new_name):
    os.rename(old_name, new_name)
    logging.info(f"Renamed file from {old_name} to {new_name}")

