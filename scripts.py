# -*- coding:utf-8 -*-
#!usr/bin/env python

import re
import pickle
import datetime

"""
    =============================================================================================###########################
                             All functions are defined in this file
    =============================================================================================
"""

pat_Chinese = re.compile(u'[\u2E80-\u9FFF]')
pat_allSymbols = re.compile(u'[，。、？:;‘’“”…—！·《》【】{}/-|]')
pat_commonSymbols = re.compile(u'[，。、？:;‘’“”…—！·-]')

###

def get_source_txt(line):
    temp = line.strip('\n')
    source_txt = temp.split('|')
    return source_txt


def get_translation(source_txt,usr_input):
   if usr_input:
        translation = '|'.join((source_txt[0],usr_input))
        translation = ''.join((translation,'\n'))
        return translation


def add_space(usr_input):
    tmp = []
    for char in usr_input:
        if re.search(pat_allSymbols,char):
            c = tmp.pop()
            if c != ' ':
                tmp.append(c)
            else:
                pass
            tmp.append(char)
            if re.search(pat_commonSymbols,char):
                tmp.append(' ')
        elif re.search(pat_Chinese,char):
            tmp.append(char)
            tmp.append(' ')              # can't combine two statments because of pop() above
        else:
            tmp.append(char)
    usr_input_space = ''.join(tmp)
    return usr_input_space


def get_offset(offset_file):
    offset = 0
    try:
        offset_str = pickle.load(offset_file)
    except EOFError:
        pass
    else:
        if offset_str:
            offset = int(offset_str)
    return offset

def cur_time():
	t = datetime.time(1,2,3)
	d = datetime.date.today()
	cur_time = datetime.datetime.combine(d,t)
	return cur_time 
