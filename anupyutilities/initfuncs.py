# anupyutilities/initfuncs.py
# Copyright (C) 2021 AnuPyUtilities
# <see TUTHORS file>
#
# This module is part of AnuPyUtilities and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import os
import yaml
import logging
import json
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser, ExtendedInterpolation
import sys

def init_yaml_conf(yaml_file):
    '''
    init yaml file
    '''
    if yaml_file:
        # No matter the `yaml_file` is file object or str of the yaml file
        # both can be parsed.
        yaml_dict: dict = yaml.safe_load(yaml_file)
    else:
        yaml_dict = {}

    try: # read the default config folder
        default_conf_dir_path = os.environ['DEFAULT_YAML_CONF_DIR']
        for root, dirs, files in os.walk(default_conf_dir_path, topdown=False):
            for f in files:
                if f.endswith('.yml'):
                    with open(os.path.join(root, f), 'r') as f_object:
                        sub_yaml_dict = yaml.safe_load(f_object)
                        yaml_dict.update(sub_yaml_dict)
    except KeyError: # no default config
        pass

    return yaml_dict


def init_config_parser(config_file):
    '''
    init configure file that ends with .ini
    '''
    config_parser = ConfigParser(
        inline_comment_prefixes=(';','#',),
        interpolation=ExtendedInterpolation())

    # Case sensetive
    config_parser.optionxform = str

    try: # read the default config folder
        default_conf_dir_path = os.environ['DEFAULT_CONF_DIR_PATH']
        for root, dirs, files in os.walk(default_conf_dir_path, topdown=False):
            for f in files:
                if f.endswith('.ini'):
                    with open(os.path.join(root, f), 'r') as f_object:
                        config_parser.read_file(f_object)
    except KeyError: # no default config
        pass
    config_parser.read_file(config_file)
    return config_parser


def init_logging_from_config_parser(config_parser: ConfigParser):
    '''
    init logging
    '''
    section = 'logging'
    prefix = config_parser.get(section, 'prefix', fallback='default')
    cwd = config_parser.get('global', 'cwd', fallback=os.getcwd())
    logdir = config_parser.get(section, 'logdir', fallback='{}/log/'.format(cwd))
    level = config_parser.getint(section, 'level', fallback=logging.INFO)
    stdout = config_parser.getboolean(section, 'stdout', fallback=False)
    datagram_log = config_parser.getboolean(section, 'datagram_log', fallback=False)
    max_bytes = config_parser.getint(section, 'max_byte', fallback=4096 * 1024)  # by default, 4K rotating
    backup_count = config_parser.getint(section, 'backup_count', fallback=20)  # by default, maximum 20 files
    file_log = config_parser.getboolean(section, 'file_log', fallback=True)

    logger_format = logging.Formatter(
        '[{}] - [%(asctime)s][%(levelname)s][%(pathname)s:%(lineno)d]: %(message)s'.format(prefix))

    root_logger = logging.getLogger()
    root_logger.setLevel(level) # 这里表示 logger 能够通过的日志等级
    setattr(root_logger, 'prefix', prefix)

    if file_log:
        handler = RotatingFileHandler("{}/{}.log".format(logdir, prefix), "a",
            max_bytes, backup_count, encoding='utf-8')
        handler.setFormatter(logger_format)
        handler.setLevel(level) # 表示 handle 能够通过的日志等级
        root_logger.addHandler(handler)

    if stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(logger_format)
        stdout_handler.setLevel(level)
        root_logger.addHandler(stdout_handler)

    if datagram_log: # datagram_log, intend to send the message to elasticsearch.
        host = config_parser.get(section, "host", fallback="127.0.0.1")
        port = config_parser.getint(section, "port", fallback=19883)
        datagram_handler = logging.handlers.DatagramHandler(host, port)

        def datagram_format(record):
            """datagram format function
            to replace `makePickle`

            Args:
                record (record): the records
            Returns
                bytes: json dumped and encoded('UTF-8')
            """
            # print(record.__dict__)

            d = {
                'module': record.module,
                '@timestamp': record.asctime,
                'levelname': record.levelname,
                'pathname': record.pathname,
                'lineno': record.lineno,
                'message': record.message,
                'prefix': root_logger.prefix
            }
            return json.dumps(d).encode('utf-8')

        datagram_handler.makePickle = datagram_format
        datagram_handler.setLevel(level)
        root_logger.addHandler(datagram_handler)

    # By default, there is fallback approach, which to ouput the message if no handler capture it.
    # for more info, see:
    #   https://docs.python.org/3/library/logging.html#logging.lastResort
    logging.lastResort = None