#!/usr/bin/env python

import os
import xmltodict
from sysutils.utils.file_utils import read_file

from abstractPackagePerformer import AbstractPerformer


class PomxmlPerformer(AbstractPerformer):
    FILE_NAME = "pom.xml"
    
    def __init__(self, root_folder='../data', delimiter=AbstractPerformer.DELIMITER):
        super().__init__(root_folder, delimiter)
        self._data = {}
        self._properties = {}
    
    @property
    def data(self):
        return self._data
    
    @property
    def properties(self):
        return self._properties
    
    def get(self, keys='project'):
        content = self.data
        for key in keys.split('.'):
            content = dict(content).get(key)
        return content
     
    def as_version(self, value):
        if not value or value is None:
            return ''
        if value.startswith('${'):
            key = value[2:-1]
            return self.properties.get(key) or ''
        return ''
 
    def process(self, keys='project.dependency'):
        content = self.get(keys)
        return [{self.PACKAGE_NAME: "{}.{}".format(d.get('groupId', ''), d.get('artifactId', '')),
                 self.PACKAGE_VERSION: "{}".format(self.as_version(d.get('version')))} for d in content]

    def load(self):
        try:
            self._data = dict(xmltodict.parse(read_file(self.FILE_NAME, self.root_folder)))
            self._properties = self.get('project.properties')
            return "OK"
        except Exception as ex:
            return "ERROR. Cannot process file '{}'; Reason: {}".format(self.FILE_NAME, ex)
            
    def extract(self):
        status = self.load()
        if status != 'OK':
            return status
        
        for key in (
                {'key': 'project.dependencies.dependency', 'name': 'dependencies'},
                {'key': 'project.build.plugins.plugin', 'name': 'plugins'},
                {'key': 'project.build.plugins.plugin', 'name': 'plugins'},
                {'key': 'project.build.pluginManagement.plugins.plugin', 'name': 'management'},
            ):
            self.save(self.process(key['key']), os.path.join(self.root_folder, "{}-java.csv".format(key['name'])))
        return "OK"


def extract(performer):
    status = performer.extract()
    return "Command {} completed. Status: {}".format('extract', status)


def main(command):
    print("PackageJson performer started. command: {}".format(command))
    
    performer = PomxmlPerformer(root_folder='../data')
    
    commands = {
        "extract": extract
    }
    return commands.get(command)(performer) if commands.get(command) else "invalid command {}".format(command)


if __name__ == "__main__":
    command = os.environ.get('COMMAND') or "extract"
    print(main(command))