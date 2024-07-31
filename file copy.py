import os
import shutil

def copy_files_by_name(src_folder, file_name, dst_folder):
    """
    Copy files with a specified name from subfolders within a source folder to a destination folder.

    Parameters:
    src_folder (str): The source directory containing subfolders.
    file_name (str): The name of the file to be copied.
    dst_folder (str): The destination directory where the files will be copied.
    """
    shutil.copy(file_name, dst_folder)
    print(f"Copied: {file_name} to {dst_folder}")

if __name__ == "__main__":
    src_folder = "C:/Users/vedan/Downloads/Us"
    dst_folder = "C:/Users/vedan/PycharmProjects/task/data/data_15min"

    for i in os.listdir("C:/Users/vedan/Downloads/Us"):
        file_name = f"C:/Users/vedan/Downloads/Us/{i}/{i}_XNAS_15minute.csv"
        print(file_name)
        shutil.copy(file_name, dst_folder)
    print("File copy operation completed.")
