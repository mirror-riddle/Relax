# -*- coding: utf-8 -*-
#!usr/bin/env python

import os
import sys
import time
import scripts
import MySQLdb

"""
===============================================================================
    Create dict from available trans and use it for auto-translating.
===============================================================================
"""


class Mydict(object):

    def get_content(self, file_name, is_trans=True):
        with open(file_name, 'U') as source_file:
            cont = source_file.readlines()
        for index, line in enumerate(cont):
            if index == 0:
                line = line.lstrip('\xef\xbb\xbf')     #cut off stupid BOM
            if is_trans:
                line = line.decode('utf-8')     #scipts.CODING doesn't work?
            source = scripts.get_source_txt(line)
            cont[index] = source
        return dict(cont)

    def check_repetition(self, cursor, shortcut, source):
            select = """SELECT 1 FROM `%s`
                        WHERE (shortcut, source)=(%%s, %%s) 
                        LIMIT 1""" % self.table_name
            cursor.execute(select, (shortcut, source))
            results = cursor.fetchall()     #results coding: unicode
            if results:
                repetition = True
            else:
                repetition = False
            return repetition

    def save_db(self, conn, cursor, shortcut, source, trans):
        #uploader = raw_input('uploader name: ')
        uploader = 'hejin'
        create_time = time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
        repetition = self.check_repetition(cursor, shortcut, source)
        if not repetition:
            insert = """INSERT INTO `%s`
                        (shortcut, source, trans, create_time, uploader)
                        VALUES(%%s, %%s, %%s, %%s, %%s)""" % self.table_name
            value = (shortcut,source,trans,create_time, uploader)
            try:
                cursor.execute(insert, value)
            except:
                bug = tans

    def merge(self, conn, cursor, source_cont, trans_cont):
        for key in source_cont:
            if trans_cont.has_key(key):
                self.save_db(conn, cursor, 
                             key, source_cont[key], 
                             trans_cont[key])

    def add_dict(self, conn, cursor, file_name):
        self.table_name = file_name.rstrip('.csv')
        source_path = ''.join(('native_en/', file_name))
        trans_path = ''.join(('native_cns/', file_name))
        source_cont = self.get_content(source_path, is_trans=False)
        trans_cont = self.get_content(trans_path, is_trans=True)
        create = """CREATE TABLE IF NOT EXISTS `%s`
                    (id INT PRIMARY KEY AUTO_INCREMENT,
                     shortcut VARCHAR(500) NOT NULL, 
                     source VARCHAR(5000) NOT NULL, 
                     trans VARCHAR(5000) NOT NULL, 
                     create_time VARCHAR(30) NOT NULL, 
                     uploader VARCHAR(20) NOT NULL)""" % self.table_name
        cursor.execute(create)
        print 'start merging %s' % file_name
        self.merge(conn, cursor, source_cont, trans_cont)
        print 'finish merging %s' % file_name

    def use_dict(self, conn, cursor, file_name):
        self.table_name = file_name.rstrip('.csv')
        source_path = 'ACOK1.3_en/'+file_name
        f = open('ACOK1.3_cns/'+file_name, 'w')
        source_cont = mydict.get_content(source_path, is_trans=False)
        print 'start auto-translating %s' % file_name
        for key in source_cont:
            select = """SELECT trans FROM `%s` 
                        WHERE (shortcut, source) =(%%s, %%s) 
                        LIMIT 1""" % self.table_name
            cursor.execute(select, (key, source_cont[key]))
            result = cursor.fetchone()
            if result:
                source_cont[key] = result[0]
            else:
                select = """SELECT trans FROM `%s` 
                            WHERE source=%%s 
                            LIMIT 1""" % self.table_name 
                cursor.execute(select, (source_cont[key],))
                temp = cursor.fetchone()
                if temp:
                    source_cont[key] = temp[0]
            trans_list = [key, '|', source_cont[key], '\n']
            trans = ''.join(trans_list)
            f.write(trans.encode(scripts.CODING))
        f.close()
        print 'finish auto-translating %s' % file_name

if __name__ == '__main__':
    mydict = Mydict()
    conn = MySQLdb.connect(**scripts.LOGIN)
    cursor = conn.cursor()
    files = os.listdir('ACOK1.3_en/')
    files.sort()
    option = raw_input("add_dict: 1\nuse_dict: 2\nyou choose (1/2?): ")
    for file_name in files:
        if option =='1':
            mydict.add_dict(conn, cursor, file_name)
        elif option =='2':
            mydict.use_dict(conn, cursor, file_name)
    cursor.close()
    conn.commit()
    conn.close()