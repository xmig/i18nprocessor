import json
import datetime
import decimal
import uuid
import six

from functools import wraps
from logging import getLogger
_logger = getLogger(__name__)

JsonDecodeError = (json.JSONDecodeError, TypeError)


class BytesFixJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode(encoding='utf-8')
        else:
            return super().default(obj)


def json_dumps(data, *args, **kwargs):
    """
    JSON encoding fixer
    """
    cls = kwargs.pop('cls', None) or BytesFixJsonEncoder
    return json.dumps(data, cls=cls, *args, **kwargs)


def json_loads(data_as_string, *args, **kwargs):
    if data_as_string:
        if isinstance(data_as_string, bytes):
            data_as_string = data_as_string.decode(encoding='utf-8')
        return json.loads(data_as_string, *args, **kwargs)


def bytes_fix_encoder(obj):
    if isinstance(obj, bytes):
        return obj.decode(encoding='utf-8')
    return obj


def json_file(filename, *args, **kwargs):
    with open(filename, "rb") as fh:
        data_as_string = fh.read()
        if isinstance(data_as_string, bytes):
            data_as_string = data_as_string.decode('utf-8', 'ignore')
        return json.loads(data_as_string, *args, **kwargs)


def json_write(filename, data):
    """
    Write data to json file
    :param filename: <str> Filename data storing
    :param data: <dict or list> data which stored
    :return: None
    """
    as_json = json_dumps(data, indent=4, sort_keys=True)
    with open(filename, "wt") as fh:
        fh.write(as_json)
    _logger.debug("JSON DUMP. FILE: '{}'".format(filename))


def json_read(filename, *args, **kwargs):
    """
    Load data from JSON file
    :param filename: JSON Filename
    :param args: params will be passed to low level json parser
    :param kwargs: params will be passed to low level json parser
    :return: <dict or list>
    """
    loader = kwargs.pop('cls', None)
    with open(filename, "rb") as fh:
        data_as_string = fh.read()
        if isinstance(data_as_string, bytes):
            data_as_string = data_as_string.decode(encoding='utf-8')
        _logger.debug("JSON LOAD. FILE: '{}'".format(filename))
        return json.loads(data_as_string, *args, cls=loader,  **kwargs)


# def json_file_write(filename, data, dumper=None):
def json_file_write(filename, data, dumper=None):
    # dumper = dumper or json_dumps
    as_json = json_dumps(data, indent=4, sort_keys=True, cls=dumper)
    with open(filename, "wt") as fh:
        fh.write(as_json)


def nice_repack(filename):
    import subprocess
    args = ['json_repack.pl', filename]
    subprocess.Popen(args)
    _logger.debug("Repack JSON to a nice view: {}".format(filename))


def as_json(funct):
    @wraps
    def wrapper(obj, *args, **kwargs):
        return to_json(funct(obj, **kwargs))
    return wrapper


def to_json(obj=None, **kwargs):
    obj = obj if obj is not None else dict()
    return json_dumps(obj, indent=kwargs.pop('indent', 2))

# See webdb/data_adapter/cassandra/json_dumper.py


class ExtendedJsonEncoder(json.JSONEncoder):
    """
    Based on REST Framework JSONEncoder
    .venv/lib/python3.7/site-packages/rest_framework/utils/encoders.py
    """
    def default(self, obj):
        try:
            if isinstance(obj, datetime.datetime):
                representation = obj.isoformat()
                if representation.endswith('+00:00'):
                    representation = representation[:-6] + 'Z'
                return representation
            elif isinstance(obj, datetime.date):
                return obj.isoformat()
            elif isinstance(obj, datetime.time):
                return obj.isoformat()
            elif isinstance(obj, datetime.timedelta):
                return six.text_type(obj.total_seconds())
            elif isinstance(obj, decimal.Decimal):
                return float(obj)
            elif isinstance(obj, uuid.UUID):
                return six.text_type(obj)
            # elif isinstance(obj, OrderedMapSerializedKey):
            #     return dict(obj)
            # elif isinstance(obj, (collections.Set, SortedSet)):
            #     return tuple(obj)
            elif isinstance(obj, bytes):
                return obj.decode('utf-8')
            elif hasattr(obj, 'tolist'):
                return obj.tolist()     # Numpy arrays and array scalars.
            elif hasattr(obj, '__getitem__'):
                return dict(obj)
            elif hasattr(obj, '__iter__'):
                return tuple(item for item in obj)
            return super().default(obj)
        except Exception as ex:
            _logger.error("Cannot provide JSON decoding. EX: type: {} obj: {} Ex: {}".format(type(obj), obj, ex))
            return str(obj)


def json_dumps_extended(data: [list, dict], **kwargs) -> str:
    return json_dumps(data, cls=ExtendedJsonEncoder, **kwargs)


def json_loads_extended(data_as_string: str, **kwargs) -> [list, dict]:
    return json_loads(data_as_string, cls=ExtendedJsonEncoder, **kwargs)