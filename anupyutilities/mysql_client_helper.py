# anupyutilities/initfuncs.py
# Copyright (C) 2021 AnuPyUtilities
# <see TUTHORS file>
#
# This module is part of AnuPyUtilities and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import logging
from contextlib import contextmanager
import urllib
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from collections import ChainMap

def custruct_connect_string(host: str, port: int, user: str,
                passwd: str, database: str,
                connect_string_option_dict: dict = {}):
        # append some default params:
        connect_string_option_chain_map = ChainMap(connect_string_option_dict, {'charset': 'utf8'})

        # https://docs.sqlalchemy.org/en/13/dialects/mysql.html#module-sqlalchemy.dialects.mysql.pymysql
        connect_string = "mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?{options}".format(
            user=user, passwd=urllib.parse.quote_plus(passwd), host=host, port=port, db=database,
            options=urllib.parse.urlencode(dict(**connect_string_option_chain_map))
        )

        return connect_string

def create_engine(connect_string, create_engine_kwargs_dict: dict = {}):
    logging.info("connect mysql with: %s", connect_string)
    # append some default params:
    create_engine_default_dict = {
        'convert_unicode': True,
        'pool_recycle': 3600
    }
    create_engine_kwargs_chain_map = ChainMap(create_engine_kwargs_dict, create_engine_default_dict)
    engine = sqlalchemy_create_engine(connect_string, **create_engine_kwargs_chain_map)
    return engine


class MysqlClientHelper():
    '''
    MysqlClient
    '''
    def __init__(self, engine):
        self.engine = engine

        # Warning: if using automap, all schemes of the DB must have a primary key.
        # For more info, following this link:
        # https://docs.sqlalchemy.org/en/13/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key
        self.Base = automap_base()
        self.Base.prepare(self.engine, reflect=True)

        self.classes = self.Base.classes

        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)


    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def select_session_scope(self):
        """
        Provide a transactional scope around a series of operations.
        Something as session_scope() but only for select, which the
        results can be escaped from return statement or after function call.
        """
        session = self.Session()
        try:
            yield session
        finally:
            session.close()