import os


def check_files_exist(directory1, directory2):
    total = []
    new = 0
    csv_files = os.listdir(directory1)
    html_files = os.listdir(directory2)

    csv_names = {filename.split('_')[0] for filename in csv_files if filename.endswith('.csv')}
    html_names = {filename.split('.')[0] for filename in html_files if filename.endswith('.html')}

    for name in csv_names:
        if name not in html_names:
            print(f"{name}.csv exists in {directory1} but {name}.html does not exist in {directory2}")
            total.append(f"{name}_XNAS_1day.csv")
            new += 1

    for name in html_names:
        if name not in csv_names:
            print(f"{name}.html exists in {directory2} but {name}.csv does not exist in {directory1}")

    print(total)
    print(new)


directory1 = 'C:/Users/vedan\PycharmProjects/task/Multi-Threaded Backtesting/data'
directory2 = 'C:/Users/vedan/PycharmProjects/task/Multi-Threaded Backtesting'
