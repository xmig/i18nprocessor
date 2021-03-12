#!/usr/bin/env python

import os
from sysutils.utils.json_tools import json_file

from abstractPackagePerformer import AbstractPerformer


class PckgJsonPerformer(AbstractPerformer):
    FILE_NAME = "package.json"
    
    def __init__(self, root_folder='../data', delimiter=AbstractPerformer.DELIMITER):
        super().__init__(root_folder, delimiter)

    def process(self, data, key='dependencies'):
        dependencies = data[key]
        return [{
            self.PACKAGE_NAME: dependency,
            self.PACKAGE_VERSION: dependencies[dependency]
        } for dependency in dependencies.keys()]

    def extract(self):
        try:
            data = json_file(os.path.join(self.root_folder, self.FILE_NAME))
            for key in ('dependencies', 'devDependencies'):
                self.save(self.process(data, key), os.path.join(self.root_folder, "{}-js.csv".format(key)))
        except Exception as ex:
            return "ERROR. Cannot process file '{}'; Reason: {}".format(self.FILE_NAME, ex)
        return "OK"
  
        
def extract(performer):
    status = performer.extract()
    return "Command {} completed. Status: {}".format('extract', status)


def main(command):
    print("PackageJson performer started. command: {}".format(command))

    performer = PckgJsonPerformer(root_folder='../data')
    
    commands = {
        "extract": extract
    }
    return commands.get(command)(performer) if commands.get(command) else "invalid command {}".format(command)


if __name__ == "__main__":
    command = os.environ.get('COMMAND') or "extract"
    print(main(command))