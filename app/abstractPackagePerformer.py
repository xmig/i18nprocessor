from sysutils.csv_utils import write_as_csv
from abc import ABC, abstractmethod


class AbstractPerformer(ABC):
    FILE_NAME = "please-define-filename"
    
    PACKAGE_NAME = 'name'
    PACKAGE_VERSION = 'version'

    DELIMITER = ','
    
    def __init__(self, root_folder='../data', delimiter=DELIMITER):
        self.root_folder = root_folder
        self.delimiter = delimiter
    
    @abstractmethod
    def process(self, *args, **kwargs):
        """repack data into ' list of dict' view"""

    def save(self, datalist, filename):
        header = [self.PACKAGE_NAME, self.PACKAGE_VERSION]
        with open(filename, "w") as fh:
            write_as_csv(fh, sorted(datalist, key=lambda k: k[self.PACKAGE_NAME]), fieldnames=header, delimiter=self.delimiter)
            print("FILE '{}' created".format(filename))
    
    @abstractmethod
    def extract(self):
        """extract data from a file"""
