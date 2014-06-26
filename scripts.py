# -*- coding:utf-8 -*-
#!usr/bin/env python

import re
import sys
# import datetime

CODING = sys.getfilesystemencoding()
LOGIN = {'host'  :'127.0.0.1',
         'user':'root',
         'passwd':'Aa68553^',
         'db':'translation',
         'charset':'utf8'}   #must be 'utf8', rather than 'utf-8'

"""
===============================================================================
                 Common functions are defined here
===============================================================================
"""

pat_Chinese = re.compile(u'[\u2E80-\u9FFF]')
pat_allSymbols = re.compile(u'[，。、？：；‘’“”…—！·《》【】{}/-|]')
pat_commonSymbols = re.compile(u'[，。、？：；‘’“”…—！·-]')

def get_source_txt(line):
    temp = line.strip('\n')
    source_txt = temp.split('|')
    return source_txt


def get_translation(source_txt, raw_translation):
   if raw_translation:
        translation = '|'.join((source_txt[0], raw_translation))
        translation = ''.join((translation,'\n'))
        return translation


def add_space(usr_input):
    tmp = []
    for char in usr_input:
        if re.search(pat_allSymbols,char):
            c = tmp.pop()
            if c != ' ':
                tmp.append(c)
            tmp.append(char)
            if re.search(pat_commonSymbols,char):
                tmp.append(' ')
        elif re.search(pat_Chinese,char):
            tmp.append(char)
            tmp.append(' ')  #can't combine 2 statments because of pop()
        else:
            tmp.append(char)
    usr_input_space = ''.join(tmp)
    return usr_input_space

# def cur_time():
# 	t = datetime.time(1,2,3)
# 	d = datetime.date.today()
# 	cur_time = datetime.datetime.combine(d,t)
# 	return cur_time 
