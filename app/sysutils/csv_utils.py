"""
Set of routines pointed to CSV manipulation
"""

import csv
import logging

_logger = logging.getLogger(__name__)


class CsvException(Exception):
    pass


def load_csv_as_dict_iterator(file_obj, fieldnames=None, delimiter=";", quotechar='"', record_num_field="#"):
    """
    Iterator.
    Read & unpack CSV File Header. Return the NEXT record.
    Field's names loaded from @param 'fieldnames' or from a header (if it presented)
    Skip header line if both 'fieldnames' & CSV header are presented

    :param file_obj: <file obj> Input CSV File
    :param fieldnames: <list | tuple | None> collection of Field's Names
    :param record_num_field: <str | None> it this field defined - inserts into the result '#' or a record
    :return: <dict> next record
    """
    assert isinstance(fieldnames, (type(None), list, tuple))

    if not file_obj:
        raise CsvException("file for CSV reader Not Defined")

    MAX_HEADER_LENGHT = 2 * 1024
    has_header = csv.Sniffer().has_header(file_obj.read(MAX_HEADER_LENGHT))
    file_obj.seek(0)
    first_line_need_to_be_skipped = False

    if fieldnames:
        csv_reader = csv.DictReader(file_obj, fieldnames=fieldnames, delimiter=delimiter, quotechar=quotechar)
        first_line_need_to_be_skipped = True if has_header else False
    else:
        if not has_header:
            raise CsvException("cannot define names of columns for CSV reader")
        csv_reader = csv.DictReader(file_obj)

    for i, row in enumerate(csv_reader):
        if first_line_need_to_be_skipped:
            first_line_need_to_be_skipped = False
            _logger.debug("csv header {} skipped".format(row))
            continue
        if record_num_field:
            row[record_num_field] = i
        yield row


def write_as_csv(file_obj, data_list, fieldnames=None, delimiter=",", quotechar='"'):
    """
    Only for TEST Purposes only in the moment
    Write Data as CSV File
    :param file_obj: <io.file> CSV File for records storing
    :param data_list: <list of dicts> Data which will be stored
    :param fieldnames: <list of str | None> Field Names - The First Line of Resulted File
    :param delimiter: <char | None> CSV Delemiter
    :param quotechar: <char | None> CSV Quotechar
    :return:
    """
    assert isinstance(data_list, list)

    def write_header(csv_writer, fieldnames):
        csv_writer.writerow(fieldnames)

    def write_row(csv_writer, fieldnames, data):
        csv_writer.writerow([data.get(x) or '' for x in fieldnames])

    first_record = data_list[0]
    fieldnames = fieldnames or list(first_record.keys())
    csv_writer = csv.writer(file_obj, delimiter=delimiter, quotechar=quotechar, quoting=csv.QUOTE_MINIMAL)

    write_header(csv_writer, fieldnames)
    i = -1
    try:
        for i, data in enumerate(data_list):
            data.pop("#", None)
            write_row(csv_writer, fieldnames, data)
    except Exception as ex:
        _logger.warn("cannot write CSV file. Only the first %d  lines stored. Exception: %s", i, ex)
