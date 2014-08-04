# -*- coding: utf8 -*-
# !usr/bin/env python

"""
===============================================================================
                 Common functions are defined here
===============================================================================
"""

import re
import logging
import pymongo
import MySQLdb
import datetime

pat_Chinese = re.compile(u'[\u2E80-\u9FFF]')
pat_punc = re.compile(u'[，。、！？…—·]')
pat_brac = re.compile(u'[（）【】《》{}/：；‘’“” ]')


def get_line_list(line):
    """Split source line into a list including shortcut and pure source"""

    temp = line.strip('*\n')
    line_list = temp.split('|')
    return line_list


def remove_None(source_list):
    """This function is used to avoid messed indexing resulted from
    removing list item in a loop."""

    count = source_list.count(None)
    while count > 0:
        source_list.remove(None)
        count -= 1


def get_translation(shortcut, raw_translation):
    """Join shortcut and raw_translation into translation, contrary to
    get_line_list."""

    trans = [shortcut, '|', raw_translation, '\n']
    translation = ''.join(trans)
    return translation


def add_space(usr_input):
    """Add space to character by given rules."""

    space_list = []
    length = len(usr_input)
    for index, item in enumerate(usr_input):
        space_list.append(item)
        # only don't add space when a chinese character followed
        # by punctuations or brackets.
        if re.search(pat_Chinese, item):
            if index < length-1:
                criteria_punc = re.search(pat_punc, usr_input[index+1])
                criteria_brac = re.search(pat_brac, usr_input[index+1])
                if criteria_punc or criteria_brac:
                    pass
                else:
                    space_list.append(' ')
            else:
                space_list.append(' ')
        # only don't add space when a punctuation followed by brackets
        elif re.search(pat_punc, item):
            if index < length-1:
                if re.search(pat_brac, usr_input[index+1]):
                    pass
                else:
                    space_list.append(' ')
            else:
                space_list.append(' ')
    usr_input_space = ''.join(space_list)

    return usr_input_space


def get_cur_time():
    """Get current time in format: 2014-07-01 17:48:46"""

    t = datetime.time(1, 2, 3)
    d = datetime.date.today()
    current_time = datetime.datetime.combine(d, t)
    return current_time


def get_source_list(file_path):
    """source list: source that can be decode('utf8')
    reject list: source that can't be decode('utf8')"""

    with open(file_path, 'U') as source_file:
        source_list = source_file.readlines()
        reject_list = []
    for index, line in enumerate(source_list):
        if index == 0:
            # cut off stupid BOM, proved useful and safe
            source_list[index] = line.lstrip('\xef\xbb\xbf')
        # record error : 'utf8' can't decode byte 0x85 in position...
        # due to line with unwanted character.
        try:
            source_list[index] = line.decode('utf8')
        except Exception, e:
            reject_list.append(line)
            source_list[index] = None
            logging.debug('='*100)
            debug_list = (e, file_path, index, line)
            for item in debug_list:
                logging.error(item)
    remove_None(source_list)

    return (source_list, reject_list)


def get_dict(file_path):
    """get source and trans dict from source and trans list"""

    source_list, reject_list = get_source_list(file_path)
    for index, line in enumerate(source_list):
        line_list = get_line_list(line)
        if len(line_list) == 2:
            source_list[index] = line_list
        else:
            source_list[index] = None
    remove_None(source_list)
    return (dict(source_list), reject_list)


# this is deprecated
def get_mysql_login():
    """Get mysql login information from my.ini"""

    with open('resources/my.ini', 'U') as configure_file:
        configure_list = configure_file.readlines()
    # remove comments and blank lines
    for index, item in enumerate(configure_list):
        item_list = item.split('#')
        if item_list[0] and item_list[0] != '\n':
            configure_list[index] = item_list[0]
        else:
            # can't directly remove item, in which case index would be messed.
            # configure_list.remove(item)
            configure_list[index] = None
    # remove all None
    remove_None(configure_list)

    # remove blank spaces
    for index, item in enumerate(configure_list):
        item_list = item.split('=')
        for i, value in enumerate(item_list):
            item_list[i] = value.strip()
        configure_list[index] = item_list
    configure_dict = dict(configure_list)

    return configure_dict


# this is deprecated.
def conn_mysql():
    """connect to mysql server"""

    login = get_mysql_login()
    print login
    conn = MySQLdb.connect(**login)
    cursor = conn.cursor()
    database = 'translation'
    create = 'CREATE DATABASE `%s`' % database
    try:
        cursor.execute(create)
    except:
        pass
    conn.select_db(database)

    return (conn, cursor)


def connect_mongo():
    """connect to mongodb, return the working database"""

    client = pymongo.MongoClient()
    database = client.translation
    return database


# this is deprecated.
def disc_mysql(conn, cursor):
    cursor.close()
    conn.close()


def config_logging():
    """using logging to record errors and info"""

    log_filename = 'resources/relaxlog.log'
    log_format = """[%(asctime)s][%(filename)s][%(funcName)s]
                    [%(levelname)s][%(message)s]"""
    logging.basicConfig(filename=log_filename, filemode='w',
                        format=log_format, level=logging.DEBUG)
