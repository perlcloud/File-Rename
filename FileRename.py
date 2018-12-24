import os
import time
import win32con
import win32event
import win32file
from datetime import datetime

# Set Variables
path_to_watch = 'M:\Lightroom\Betzalel Goupen\Ambitec\Auto Import'
log_path = path_to_watch + '\\FileRename_LOG.csv'
delim = '_'

product_id = input('Enter Product ID:')
global loop_count
loop_count = 1


def log(old_file, new_file):  # Create log file
    # Create a log file if it does not exist
    if not os.path.isfile(log_path):
        with open(log_path, 'w+') as log_file:
            log_file.write('Timestamp,Old Path,New Path\n')
            log_file.close

    # Write name change to log
    with open(log_path, 'a') as log_file:
        log_file.write(str(datetime.now()) + ',' +
                       old_file + ',' +
                       new_file + '\n')
        log_file.close()


def wait_for_file_write(file):  # Wait for file to finish writing
    file_write_done = False
    while file_write_done != True:
        try:
            # The error: "The process cannot access the file
            # because it is being used by another process"
            # is thrown when the file is still being written.
            # We take advantage of this error to make sure the write is done.
            file_done = open(file)
            file_done.close()
            file_write_done = True
        except:
            pass


def rename(file, loop_count):
    rename_done = False
    while rename_done != True:
        # If there is already a file witgh the "new_file" name
        # We increment by 1 until we hit a unique number
        for file_name in file:
            old_file = path_to_watch + '\\' + file_name
            new_file = (path_to_watch + '\\'
                        + product_id
                        + delim  # Defined to account for product_id w/ an _
                        + str(loop_count)
                        + str(os.path.splitext(file_name)[1]))  # Extention

            if old_file != log_path:  # Ignore log file
                if not os.path.isfile(new_file):
                    wait_for_file_write(old_file)
                    os.rename(old_file, new_file)
                    log(old_file, new_file)
                    rename_done = True
                else:
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
            new_path_contents = dict([(f, None) for f in os.listdir(path_to_watch)])
            added_file = [f for f in new_path_contents if not f in old_path_contents]

            if added_file:
                rename(added_file, loop_count)
                loop_count += 1

            new_path_contents = dict([(f, None) for f in os.listdir(path_to_watch)])
            old_path_contents = new_path_contents
            win32file.FindNextChangeNotification(change_handle)
finally:
    win32file.FindCloseChangeNotification(change_handle)
