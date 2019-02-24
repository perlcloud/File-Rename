import os
import csv
import time
import win32con
import win32file
import win32event

from datetime import datetime

# Set variables
path_to_watch = 'M:\Lightroom\Betzalel Goupen\Ambitec\Auto Import'
log_path = os.path.join(path_to_watch, 'FileRename_LOG.csv')
delim = '_'

product_id = input('Enter Product ID: ')
loop_count = 1


def log(old_file, new_file):
    """Log a files former and current filename"""
    # Create .csv if one does not exist
    if not os.path.isfile(log_path):
        with open(log_path, 'w', newline='') as log:
            file_writer = csv.writer(log, delimiter=',',
                                     quotechar='"', quoting=csv.QUOTE_ALL)
            file_writer.writerow(['timestamp',
                                  'oldPath',
                                  'newPath'])

    try:
        with open(log_path, 'a', newline='') as log:
            file_writer = csv.writer(log, delimiter=',',
                                     quotechar='"', quoting=csv.QUOTE_ALL)
            file_writer.writerow([str(datetime.now()),
                                  old_file,
                                  new_file])
    except PermissionError:
        print('PermissionError: Log not written, please close the log file.')


def wait_for_file_write(file):
    """Wait for file to finish writing before moving on"""
    file_write_done = False
    while True:
        try:
            # The error: "The process cannot access the file
            # because it is being used by another process"
            # is thrown when the file is still being written.
            # We take advantage of this error to make sure the write is done.
            with open(file) as check_file_write_done:
                file_write_done = True
            break
        except:
            pass


def rename(file, loop_count):
    rename_done = False
    while rename_done != True:
        # If there is already a file with the "new_file" name
        # We increment by 1 until we hit a unique number
        for file_name in file:
            old_file = os.path.join(path_to_watch, file_name)
            new_file = (os.path.join(path_to_watch,
                                     product_id +
                                     delim +
                                     str(loop_count) +
                                     str(os.path.splitext(file_name)[1])))  # Extention

            if old_file != log_path:  # Ignore log file
                if not os.path.isfile(new_file):
                    # If a file with this name does not already exist
                    # take steps to create the file
                    wait_for_file_write(old_file)
                    os.rename(old_file, new_file)
                    log(old_file, new_file)
                    rename_done = True
                else:
                    # If the specified file already exists
                    # advance the loop for this product
                    loop_count += 1


# Sets up dir watch
# Credit to Tim Golden for the directory change watching https://goo.gl/JdrHCn
change_handle = win32file.FindFirstChangeNotification(
    path_to_watch,
    0,
    win32con.FILE_NOTIFY_CHANGE_FILE_NAME
)

try:
    old_path_contents = dict([(f, None) for f in os.listdir(path_to_watch)])
    while 1:
        result = win32event.WaitForSingleObject(change_handle, 500)
        if result == win32con.WAIT_OBJECT_0:
            # If the WaitFor... returned because of a notification (as
            # opposed to timing out or some error) then look for the
            # changes in the directory contents.
            new_path_contents = dict([(f, None) for f in os.listdir(path_to_watch)])
            
            # Get the added files by comparing the old list of files to the new
            added_file = [f for f in new_path_contents if not f in old_path_contents]

            if added_file:
                rename(added_file, loop_count)
                loop_count += 1

            old_path_contents = dict([(f, None) for f in os.listdir(path_to_watch)])
            win32file.FindNextChangeNotification(change_handle)
finally:
    win32file.FindCloseChangeNotification(change_handle)
