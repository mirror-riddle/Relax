# -*- coding: utf8 -*-
#!usr/bin/env python

import os
import sys
import scripts
import logging
"""
===============================================================================
    Create dict from available trans and use it for auto-translating.
===============================================================================
"""


class Mydict(object):
    """
    Two methods that finish jobs below:
    add_db: add new source and translation to database
    use_db: query translation from databse and auto-translate
    """
    def __init__(self):
        scripts.config_logging()

    def add_db(self, conn, cursor, file_name, en_dir, cns_dir):
        table = os.path.splitext(file_name)[0]
        source_path = os.path.join(en_dir, file_name)
        trans_path = os.path.join(cns_dir, file_name)
        source_dict = self.get_dict(source_path)[0]
        trans_dict = self.get_dict(trans_path)[0]
        create = """CREATE TABLE IF NOT EXISTS `%s`(
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    shortcut VARCHAR(500) NOT NULL, 
                    source VARCHAR(5000) NOT NULL, 
                    translation VARCHAR(5000) NOT NULL, 
                    create_time VARCHAR(30) NOT NULL)""" %table
        cursor.execute(create)
        logging.info('start merging %s' % source_path)
        print 'start merging %s' % source_path
        self.insert_db(conn, cursor, source_dict, trans_dict, table, source_path, trans_path)
        logging.info('finish merging %s' % source_path)
        print 'finish merging %s' % source_path

    def insert_db(self, conn, cursor, source_dict, trans_dict, table, source_path, trans_path):
        create_time = scripts.cur_time()
        for key in source_dict:
            if trans_dict.has_key(key) and source_dict[key] != trans_dict[key]:
                repeat = self.check_repeat(cursor, key, source_dict[key], table, source_path)
                if not repeat:
                    insert = """INSERT INTO `%s`(shortcut, source, translation, create_time)
                                VALUES(%%s, %%s, %%s, %%s)""" % table
                    value = (key, source_dict[key], trans_dict[key], create_time)
                    try:
                        cursor.execute(insert, value)
                    except Exception, e:
                        logging.debug('='*50)
                        debug_list = [e, source_path, key, trans_dict[key]]
                        for item in debug_list:
                            logging.error(item)

    def use_db(self, conn, cursor, file_name, source_dir):
        table = os.path.splitext(file_name)[0]
        source_path = os.path.join(source_dir, file_name)
        source_dict, reject_list = self.get_dict(source_path)
        save_dir = os.path.join(os.getcwd(), 'new_language')
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        save_path = os.path.join(save_dir, file_name)
        with open(save_path, 'w') as save_file:
            logging.info('start auto-translating %s' %source_path)
            print 'start auto-translating %s' %source_path
            self.query_and_write(cursor, save_file, table, source_dict, reject_list, source_path)
            logging.info('finish auto-translating %s' %source_path)
            print 'finish auto-translating %s' %source_path

    @staticmethod
    def query_and_write(cursor, save_file, table, source_dict, reject_list, source_path):
        total_num = len(source_dict)
        done_num = 0
        trans_list = []
        for key in source_dict:
            value = source_dict[key]
            select = "SELECT translation FROM `%s` WHERE (shortcut, source) =(%%s, %%s) LIMIT 1" %table
            try:
                cursor.execute(select, (key, value))
            except Exception, e:
                logging.debug('='*50)
                debug_list = [e, source_path, key, value]
                for item in debug_list:
                    logging.error(item)
            else:
                result = cursor.fetchone()
                if result:
                    source_dict[key] = result[0]  #value != source_dict[key] now
                    done_num += 1
            trans = ''.join([key, '|', source_dict[key], '\n'])
            trans_list.append(trans.encode('utf8'))
        trans_list.sort()
        trans_list.extend(reject_list)
        for trans_line in trans_list:
            save_file.write(trans_line)
        logging.info('translation rate: %s/%s' %(done_num, total_num))
        print 'translation rate: %s/%s' %(done_num, total_num)

    @staticmethod
    def get_dict(file_path):
        source_list, reject_list = scripts.get_source_list(file_path)
        for index, line in enumerate(source_list):
            line_list = scripts.get_line_list(line)
            if len(line_list) == 2:
                source_list[index] = line_list
            else:
                source_list[index] = None
        scripts.remove_None(source_list)
        return (dict(source_list), reject_list)

    @staticmethod
    def check_repeat(cursor, shortcut, source, table, source_path):
        select = "SELECT id FROM `%s`WHERE (shortcut, source)=(%%s, %%s) LIMIT 1" %table
        try:
            cursor.execute(select, (shortcut, source))
        except Exception, e:
            logging.debug('='*50)
            debug_list = [e, source_path, shortcut, source]
            for item in debug_list:
                logging.error(item)
            repeat = True
        else:
            result = cursor.fetchone()     #result coding: unicode
            if result:
                repeat = True
            else:
                repeat = False
        return repeat