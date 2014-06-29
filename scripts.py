# -*- coding:utf8 -*-
#!usr/bin/env python

import re
import sys
import datetime
import MySQLdb
import logging

# DEBUG = True
# CODING = sys.getfilesystemencoding()
LOGIN = {'host'  :'127.0.0.1',
         'user':'root',
         'passwd':'Aa68553^',
         'charset':'utf8'}   #must be 'utf8', rather than 'utf8'

"""
===============================================================================
                 Common functions are defined here
===============================================================================
"""

pat_Chinese = re.compile(u'[\u2E80-\u9FFF]')
# pat_allSymbols = re.compile(u'[，。、！？：；‘’“”…—·《》{}/]')
pat_punctuations = re.compile(u'[，。、！？…—·]')
pat_brackets = re.compile(u'[（）【】《》{}/：；‘’“” ]')


def get_line_list(line):
    temp = line.strip('\n')
    line_list = temp.split('|')
    return line_list

def remove_None(source_list):
    count = source_list.count(None)
    for i in range(count):
        source_list.remove(None)

def get_trans(source_txt, raw_translation):
   if raw_translation:
        translation = '|'.join((source_txt[0], raw_translation))
        translation = ''.join((translation,'\n'))
        return translation

def add_space(usr_input):
    space_list = []
    length = len(usr_input)
    for index, item in enumerate(usr_input):
        space_list.append(item)
        if re.search(pat_Chinese, item):
            if index < length-1:
                condition_punc = re.search(pat_punctuations, usr_input[index+1])
                condition_brac = re.search(pat_brackets, usr_input[index+1])
                if condition_punc or condition_brac:
                    pass
                else:
                    space_list.append(' ')
            else:
                space_list.append(' ')
        elif re.search(pat_punctuations, item):
            if index < length-1:
                if re.search(pat_brackets, usr_input[index+1]):
                    pass
                else:
                    space_list.append(' ')
            else:
                space_list.append(' ')
    usr_input_space = ''.join(space_list)
    return usr_input_space

def cur_time():
	t = datetime.time(1,2,3)
	d = datetime.date.today()
	cur_time = datetime.datetime.combine(d,t)
	return cur_time 

def get_source_list(file_path):
    with open(file_path, 'U') as source_file:
        source_list = source_file.readlines()
        reject_list = []
    for index, line in enumerate(source_list):
        if index == 0:
            source_list[index] = line.lstrip('\xef\xbb\xbf') #cut off stupid BOM         
        try:
            source_list[index] = line.decode('utf8')
        except Exception, e:
            reject_list.append(line)
            source_list[index] = None
            logging.debug('='*50)
            debug_list = (e, file_path, index, line)
            for item in debug_list:
                logging.error(item)
    remove_None(source_list)
    return (source_list, reject_list)

def conn_mysql():
    conn = MySQLdb.connect(**LOGIN)
    cursor = conn.cursor()
    database = 'translation'
    create = 'CREATE DATABASE IF NOT EXISTS `%s`' %database
    cursor.execute(create)
    conn.select_db(database)
    return (conn, cursor)


def disc_mysql(conn, cursor):
    cursor.close()
    conn.close()

def config_logging():
    log_format = '[%(asctime)s][%(filename)s][%(funcName)s][%(levelname)s][%(message)s]'
    log_filename = 'log.log'
    logging.basicConfig(filename= log_filename, filemode='w', format=log_format, level=logging.DEBUG)


config_logging() # logging config