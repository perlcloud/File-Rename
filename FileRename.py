import os
import win32con
import win32event
import win32file
import time
import threading
from datetime import datetime

path_to_watch = 'M:\\Dropbox\\Sandbox\\FileRename\\SampleImages'
product_id = input('Enter Product ID:')
global loop_count
loop_count = 1

log_path = path_to_watch + '\\FileRename_LOG.csv'
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


def rename(file, loop_count):
    # time.sleep(1)
    for file_name in file:
        old_file = path_to_watch + '\\' + file_name
        new_file = (path_to_watch + '\\'
                    + product_id
                    + delim
                    + str(loop_count)
                    + str(os.path.splitext(file_name)[1]))  # File extention

        if old_file != log_path:  # Ignore log file
            if not os.path.isfile(new_file):
                log(old_file, new_file)
                os.rename(old_file, new_file)
            else:
                loop_count += 1


change_handle = win32file.FindFirstChangeNotification(
    path_to_watch,
    0,
    win32con.FILE_NOTIFY_CHANGE_FILE_NAME
)

try:  
    old_path_contents = dict ([(f, None) for f in os.listdir (path_to_watch)])
    while 1:
        result = win32event.WaitForSingleObject (change_handle, 500)  
        if result == win32con.WAIT_OBJECT_0:
            new_path_contents = dict ([(f, None) for f in os.listdir (path_to_watch)])
            added = [f for f in new_path_contents if not f in old_path_contents]
            deleted = [f for f in old_path_contents if not f in new_path_contents]
            if added:
                rename(added, loop_count)
                loop_count += 1
            
            new_path_contents = dict ([(f, None) for f in os.listdir (path_to_watch)])
            old_path_contents = new_path_contents
            win32file.FindNextChangeNotification(change_handle)
            # print('1')

finally:
    win32file.FindCloseChangeNotification (change_handle)