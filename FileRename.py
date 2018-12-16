import os
from datetime import datetime

src = "M:\\Dropbox\\Sandbox\\FileRename\\SampleImages\\Original"
productID = input('Enter Product ID:')

log_path = src + '\\FileRename_LOG.csv'
delim = '_'

def log(old_file, new_file):  # Create log file
    # Create a log file if it does not exist
    if not os.path.isfile(log_path):
        with open(log_path, 'w+') as log_file:
            log_file.write('Timestamp,old,new\n')
            log_file.close

    # Write name change to log
    with open(log_path, 'a') as log_file:
        log_file.write(str(datetime.now()) + ',' +
                        old_file + ',' +
                        new_file + '\n')
        log_file.close()


def rename():
    files = os.listdir(src)
    i = 1

    for file_name in files:
        old_file = src + '\\' + file_name
        new_file = (src + '\\'
                    + productID
                    + delim
                    + str(i)
                    + str(os.path.splitext(file_name)[1]))  # File extention

        if old_file != log_path:  # Ignore log file
            log(old_file, new_file)
            os.rename(old_file, new_file)
            i += 1


if __name__ == '__main__':
    rename()