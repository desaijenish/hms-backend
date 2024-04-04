import os
import uuid


def create_directory(base_directory, category_id, sub_category_id):
    folder_path = os.path.join(base_directory, str(
        category_id), str(sub_category_id))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path


def create_document_directory(base_directory, name):
    folder_path = os.path.join(base_directory, str(
        name))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path


def generate_file_name(extension):
    return f'{uuid.uuid4()}.png'
