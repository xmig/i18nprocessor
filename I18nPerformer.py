import os, sys
import re
import copy
from logging import getLogger
from logging.config import dictConfig
from sysutils.utils.file_utils import file_exists, check_or_create_folder, list_folder, get_basename, file_rename
from sysutils.utils.dict_utils import walk_through, dict_merge, get_or_create
from sysutils.utils.debug import nice_print
from sysutils.utils.json_tools import json_file, json_write
from sysutils.csv_utils import write_as_csv, load_csv_as_dict_iterator
from sysutils.timeutils import time_as_string
from mmh3 import hash128

check_or_create_folder("./logs")

from logging_config import LOGGING_CONFIG
dictConfig(LOGGING_CONFIG)

_logger = getLogger(__name__)


class I18nPerformer:
    SEPARATOR = '.'
    
    def __init__(self,
                 baselang="en",
                 ia8n_folder='./data/i18n',
                 store_folder='./data/storage',
                 output_folder='./data/out',
                 input_folder='./data/in'):
        self.baselang = baselang
        self.i18n_folder = ia8n_folder
        self.store_folder = store_folder
        self.output_folder = output_folder
        self.input_folder = input_folder
        
        self.masterdata = {}
        self.master_wrk = {}
    
    @staticmethod
    def timestring():
        return time_as_string(None, '%Y-%m-%d_%H-%M')
    
    def master_filename(self):
        return os.path.join(self.store_folder, 'MASTER.json')

    def backup_file(self, name):
        new_name = "{}.{}.bak".format(name, self.timestring())
        file_rename(name, new_name)
        _logger.info("file '{}' backuping...".format(new_name))
        return new_name
    
    def backup_master_file(self):
        name = self.master_filename()
        if file_exists(name):
            return self.backup_file(name)
            
    def json_filename(self, filename_prefix):
        return '{}.json'.format(filename_prefix)
    
    def csv_input_filename(self, lang):
        return os.path.join(self.input_folder, '{}.in.csv'.format(lang))
    
    def csv_output_filename(self, lang):
        return os.path.join(self.output_folder, '{}.out.csv'.format(lang))
    
    def packer(self, value, path, lang):
        if not value:
            return
        lang_is_base = lang == self.baselang
        hash = hash128(value)
        item = self.masterdata.get(hash)
        
        pathes = path.split(self.SEPARATOR)
        key = pathes[-1]
        
        whole_key = self.SEPARATOR.join(pathes[1:]) # 'en.' remove from beginning
        
        if lang_is_base:
            if not item:
                item = {'hash': hash, 'phrase': value, 'key': key, 'placed': []}
                self.masterdata[hash] = item
            self.master_wrk[whole_key] = item
            item['placed'].append(path)
        else:
            base_item = self.master_wrk.get(whole_key)
            if not base_item:
                _logger.debug("Extra '{}' phrase will be removed {}".format(lang, value))
                return
            base_item['placed'].append(path)
            
    def unpack(self, data, lang):
        result = {}
        hashlangtab = {str(hash128(item['phrase'])): item for item in data}
        
        for hash, master in self.masterdata.items():
            data = hashlangtab.get(hash)
            if not data:
                if master.get('key') and master.get('key') != 'null':
                    _logger.debug("Cannot found master data for '{}'; SKIPPED".format(master['key']))
                continue
            master[lang] = data[lang]
            for place in master.get('placed') or []:
                parts = place.split(self.SEPARATOR)
                target_lang = parts.pop(0)  # not used
                filename = parts.pop(0)
                file_ref = get_or_create(result, filename)
                dict_merge(file_ref, self.compose_dict(parts, master.get(lang), lang))
        return(result)
    
    @staticmethod
    def compose_dict(parts: list, key: str, lang: str):
        if not parts:
            return
        result = {}
        pointer = result
        while len(parts) > 0:
            part = parts.pop(0)
            p = pointer.get(part)
            if not p:
                pointer[part] = {}
            if len(parts) == 0:
                pointer[part] = key
            else:
                pointer = pointer[part]
        return result

    def init_from_file(self, filename, filename_prefix, lang):
        _logger.info("lang: '{}' file '{}' processing...".format(lang, filename))
        data = json_file(filename)
        base_path = "{}.{}".format(lang, filename_prefix)
        walk_through(data, lambda value, path: self.packer(value, path, lang), base_path)
    
    def process_save(self, filename, lang):
        header = ["phrase", lang]
        check_or_create_folder(filename, skip_last_part=True)
        with open(filename, "w") as fh:
            datalist = []
            for key, item in self.masterdata.items():
                if not item.get('phrase'):
                    continue
                used_langs = {x.split(self.SEPARATOR)[0] for x in item['placed']}
                if lang in used_langs:
                    _logger.debug("Phrase already presented, lang: '{}' phrase: '{}'. SKIPPED".format(lang, item.get('phrase')))
                    continue
                item = copy.deepcopy(item)
                item[lang] = ''
                del item['key']
                del item['placed']
                datalist.append(item)
            if not datalist:
                _logger.info("Output file is empty for lang: {}. SKIPPED".format(lang))
                return
            write_as_csv(fh, datalist, fieldnames=header)
            _logger.info("lang {}; {} records was stored in file {}".format(lang, len(datalist), filename))
            
            
    def save(self, langs: (list, tuple)):
        _logger.info("Masterdata file '{}' updating...".format(self.master_filename()))
        filename = self.master_filename()
        check_or_create_folder(filename, True)
        json_write(filename, self.masterdata)
        for lang in langs:
            filename = self.csv_output_filename(lang)
            if (file_exists(filename)):
                self.backup_file(filename)
            _logger.info("lang: '{}' file '{}' composing...".format(lang, filename))
            self.process_save(filename, lang)
        
    def join(self, langs: (list, tuple)):
        try:
            self.masterdata = json_file(self.master_filename())
        except FileNotFoundError as ex:
            _logger.error("MASTER file '{}' not found. STOPPED.".format(self.master_filename()))
            return
    
        for lang in langs:
            fieldnames = ['phrase', lang]
            try:
                filename = self.csv_input_filename(lang)
                with open(filename, "r") as fh:
                    data = self.unpack([x for x in load_csv_as_dict_iterator(fh, fieldnames=fieldnames)], lang)
                    _logger.info("lang: '{}' file '{}' processing...".format(lang, filename))
                    for prefix in data.keys():
                        content = data[prefix]
                        folder = check_or_create_folder(os.path.join(self.output_folder, lang))
                        
                        outputfilename = os.path.join(folder, self.json_filename(prefix))
                        if file_exists(outputfilename):
                            base_file_name = self.backup_file(outputfilename)
                            base_data = json_file(base_file_name)
                            dict_merge(content, base_data)
                            _logger.info("lang {}. Content was added to file '{}'. Original was backup".format(lang, outputfilename))
                        else:
                            _logger.info("lang {}. Content file composed '{}'.".format(lang, outputfilename))
                        json_write(outputfilename, content)
            except IOError as ex:
                _logger.warning("Cannot process '{}'; Exception: {}".format(lang, ex))

    def load_folder(self, folder, lang):
        for filename in list_folder(folder):
            whole_file_name = os.path.join(folder, filename)
            self.init_from_file(whole_file_name, get_basename(filename), lang)
            
    def load(self, langs: (list, tuple)):
        
        folder = os.path.join(self.i18n_folder, self.baselang)
        _logger.info("loading base language '{}' content...".format(self.baselang))
        self.load_folder(folder, self.baselang)
        for lang in langs:
            _logger.info("loading actual '{}' content...".format(lang))
            folder = os.path.join(self.i18n_folder, lang)
            self.load_folder(folder, lang)
            
        self.backup_master_file()
        self.save(langs)


def i18n_load(perfomer, target_languages):
    perfomer.load(target_languages)
    _logger.info("i18n {} completed".format('load'))


def i18n_apply(perfomer, target_languages):
    perfomer.join(target_languages)
    _logger.info("i18n {} completed".format('apply'))


def main(command=None):
    command = command or os.environ.get('COMMAND') or "load"
    _logger.info("i18n started. command: {}".format(command))
    
    base_language = os.environ.get('BASE_LANGUAGE') or "en"
    target_languages = os.environ.get('TARGET_LANGUAGES') or "ru"
    target_languages = [x.strip() for x in re.split('[\s|,]', target_languages) if x.strip()]

    # perfomer = I18nPerformer(
    #     baselang=base_language,
    #     ia8n_folder='./data/i18n',
    #     store_folder='./data/storage',
    #     output_folder='./data/out',
    #     input_folder='./data/in')
    
    perfomer = I18nPerformer(
        baselang=base_language,
        ia8n_folder='./data/i18n',
        store_folder='./data/storage',
        output_folder='./data/i18n',
        input_folder='./data/i18n')
    
    if command == "load":   return i18n_load(perfomer, target_languages)
    if command == "apply":  return i18n_apply(perfomer, target_languages)
    
    _logger.error("Please set up COMMAND ENVIRONMENT Variable 'load' or 'apply' ")


if __name__ == "__main__":
    #main(sys.argv[1:])
    main('load')
    # main('apply')