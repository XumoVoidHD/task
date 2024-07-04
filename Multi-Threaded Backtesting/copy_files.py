import os
import shutil


def copy_files(source_dir, destination_dir, pattern):

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)


    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(pattern):
                print("hit")
                source_file_path = os.path.join(root, file)
                destination_file_path = os.path.join(destination_dir, file)
                shutil.copy2(source_file_path, destination_file_path)
                print(f"Copied: {source_file_path} to {destination_file_path}")


def copy_csv_files_by_names(source_dir, destination_dir, csv_files):

    os.makedirs(destination_dir, exist_ok=True)

    for csv_file in csv_files:
        source_file = os.path.join(source_dir, csv_file)
        destination_file = os.path.join(destination_dir, csv_file)

        if os.path.exists(source_file):
            shutil.move(source_file, destination_file)
            print(f"Copied {source_file} to {destination_file}")
        else:
            print(f"File {csv_file} does not exist in {source_dir}")


# source_directory = 'C:/Users/vedan\PycharmProjects/task/Multi-Threaded Backtesting/data'
# destination_directory = 'C:/Users/vedan\PycharmProjects/task/Multi-Threaded Backtesting/data2'
#
# csv_files_to_copy = ['MARXU_XNAS_1day.csv', 'MAYS_XNAS_1day.csv', 'MCACW_XNAS_1day.csv', 'MCAGR_XNAS_1day.csv', 'MITAU_XNAS_1day.csv', 'MCAAW_XNAS_1day.csv', 'MITAW_XNAS_1day.csv', 'MCAGU_XNAS_1day.csv', 'MCAAU_XNAS_1day.csv', 'MCACR_XNAS_1day.csv', 'MCAC_XNAS_1day.csv', 'MCAG_XNAS_1day.csv', 'MDRRP_XNAS_1day.csv', 'MCACU_XNAS_1day.csv', 'MACAU_XNAS_1day.csv', 'MAQCU_XNAS_1day.csv', 'MARXR_XNAS_1day.csv', 'MAQCW_XNAS_1day.csv', 'MACA_XNAS_1day.csv', 'MACAW_XNAS_1day.csv', 'MAQC_XNAS_1day.csv', 'MMVWW_XNAS_1day.csv', 'MLECW_XNAS_1day.csv']
#
# copy_csv_files_by_names(source_directory, destination_directory, csv_files_to_copy)



# source_directory = "C:/Users/vedan/Downloads/Us"
# destination_directory = "C:/Users/vedan\PycharmProjects/task/Multi-Threaded Backtesting/data"
# file_pattern = '1day.csv'
#
# copy_files(source_directory, destination_directory, file_pattern)