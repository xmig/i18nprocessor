"""
copyright tretyak@gmail.com
MIT License

Set of Input / Output utilities

# todo merge this module with "file_utils"

"""
import os
import io
import shutil
import glob
import traceback
from random import randint

from sysutils.timeutils import time_as_string
from logging import getLogger
_logger = getLogger("sysutils")

from pprint import PrettyPrinter


def printf(str, *args):
    print(str % args, end='')


def full_file_name(file_name, folder=None, extension=None):
    file_name = file_name if folder is None else os.path.join(str(folder), file_name)
    file_name = file_name if extension is None else "{}.{}".format(file_name, extension)
    return file_name

#
# def write_file(data, file_name, folder=None, extension=None, mode='wb'):
#     file_name = full_file_name(file_name, folder, extension)
#     with io.open(file_name, mode) as file_stream:
#         file_stream.write(data)


def nice_dict_print(data, file_name, folder=None, extension=None, indent=4):
    file_name = full_file_name(file_name, folder, extension)
    with io.open(file_name, 'wb') as file_stream:
        printer = PrettyPrinter(stream=file_stream, indent=indent)
        printer.pprint(data)


def get_random_file_name(prefix, ext):
    return "{}_{}_{}.{}".format(prefix, time_as_string(None, time_fmt='%Y%m%d_%H%M%S'), randint(0,9), ext)


def file_extension(file_name):
    name, extension = os.path.splitext(file_name)
    return extension[1:] if extension and len(extension) > 1 else None


def file_size(file_name, skip_exception=True):
    try:
        return os.path.getsize(file_name)
    except:
        if skip_exception:
            return -1
        raise


def file_exists(file_name):
    return os.path.exists(file_name)


def split_path2(path):
    path_parts = []
    while path != os.path.dirname(path):
        path_parts.append(os.path.basename(path))
        path = os.path.dirname(path)
        path_parts.reverse()
    return path_parts


def split_path(path):
    allparts = []
    while True:
        parts = os.path.split(path)
        if parts[0] == path:
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def part_of_path(path, start_from, stop_to):
    parts = split_path(path)
    return '/'.join(parts[start_from:stop_to])


def check_or_create_folder(path):
    path = os.path.normpath(os.path.abspath(path))
    parts = split_path(path)
    for i, item in enumerate(parts):
        temp_parts = parts[0: i + 1]
        temp_name = '/'.join(temp_parts)[1:]
        if temp_name and not os.path.exists(temp_name):
            try:
                os.mkdir(temp_name)
            except OSError as er:
                _logger.warning("Cannot create folder: '{}'; Exception: {}".format(temp_name, er))
                raise
            #print ("Created: '{}' .. [{}]".format(temp_name, item))
    return path


def move_folder_from_to(source, destination):
    return shutil.move(source, destination)


def file_rename(old_name, new_name):
    return shutil.move(old_name, new_name)


def delete_file(file_name, raise_if_no_file=False):
    try:
        os.remove(file_name)
    except FileNotFoundError:
        if raise_if_no_file:
            raise


def list_folder(folder_name):
    try:
        return os.listdir(folder_name) if os.path.exists(folder_name) else []
    except Exception as e:
        _logger.warning("Cannot check folder '{}' .. {}".format(folder_name, e))
        return []


def get_file_names(file_mask, folder="./"):
    mask = os.path.join(folder, file_mask)
    return sorted([x for x in glob.glob(mask)])


def read_file(file_name, folder=None, extension=None, mode='rb'):
    try:
        file_name = full_file_name(file_name, folder, extension)
        with io.open(file_name, mode) as file_stream:
            return file_stream.read()
    except Exception as ex:
        _logger.warning("Cannot read file: '{}'; Reason: '{}' [{}]".format(file_name, ex, traceback.format_exc()))


def read_text_file_as_lines(filename):
    with open(filename, "rt", encoding="utf-8") as f:
        lines = [line.rstrip('\n') for line in f.readlines()]
    return lines


def read_text_file(file_name, folder=None, extension=None):
    return str(read_file(file_name, folder, extension, mode='rt'))


def write_file(data, file_name, folder=None, extension=None, mode='wb'):
    try:
        file_name = full_file_name(file_name, folder, extension)
        with io.open(file_name, mode) as file_stream:
            if isinstance(data, str):
                data = bytes(data.encode('utf-8'))
            file_stream.write(data)
    except Exception as ex:
        _logger.warning("Cannot write file: '{}'; Reason: '{}' [{}]".format(file_name, ex, traceback.format_exc()))
        return None
    else:
        return file_name


def write_text_file(data, file_name, folder=None, extension=None, mode='wb'):
    try:
        file_name = full_file_name(file_name, folder, extension)
        with io.open(file_name, mode) as file_stream:
            if isinstance(data, str):
                data = bytes(data.encode('utf-8'))
            file_stream.write(data)
    except Exception as ex:
        raise
    else:
        return file_name


# def write(data, filename, mode='wb'):
#     with open(filename, mode) as fh:
#         fh.write(data)


def get_filename(full_filename):
    """Returns the final component of a pathname"""
    return os.path.basename(full_filename)


# todo remove this method
def get_basename(filename):
    name = os.path.basename(filename)
    return os.path.splitext(name)[0]


def get_folder(full_name):
    return os.path.split(full_name)[0]


def get_ext(filename):
    """
    return string after the LAST dot (include ".")
    For example for "hello.word.json" it will be  ".json"
    :param filename: <str> full path or base name file name
    :return: <str>
    """
    name = os.path.basename(filename)
    return os.path.splitext(name)[1]


def get_long_ext(filename):
    """
    return string after the FIRTS dot (include ".")
    For example for "hello.word.json" it will be  ".word.json"
    :param filename: <str> full path or base name file name
    :return: <str>
    """
    name = os.path.basename(filename)
    idx = name.index(".")
    return name[idx:]


def make_filename_link(source, target):
    #return os.symlink(source, target)
    return os.link(source, target)


def is_file_exists(path):
    return os.path.exists(path)


# if __name__ == "__main__":
#     name = "/mydev/worddict/.data/worddata/store/videochannels/ted/en/680.mp4"
#     folder = get_folder(name)