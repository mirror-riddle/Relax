# -*- coding: utf-8 -*-
#!usr/bin/env python

import os
import sys
import time
import scripts
import MySQLdb
#from exceptions import OperationalError
"""
===============================================================================
    Create dict from available trans and use it for auto-translating.
===============================================================================
"""


class Mydict(object):

    def get_content(self, file_path):
        with open(file_path, 'U') as source_file:
            cont = source_file.readlines()
        for index, line in enumerate(cont):
            if index == 0:
                line = line.lstrip('\xef\xbb\xbf')     #cut off stupid BOM
            try:
                line = line.decode('utf-8')  #scipts.CODING doesn't work?
            except:
                if scripts.DEBUG:
                    print file_path, 'at line: ', index
                    print "get_content:mixed coding line:\n%s" %line 
                line = ''
            source = scripts.get_source_txt(line)
            if len(source) == 2:
                cont[index] = source
            else:
                cont[index] = None
                # print line
                # cont.remove(line) # removing element results in wrong index.
        count = cont.count(None)
        for i in range(count):
            cont.remove(None)
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
        try:
            repetition = self.check_repetition(cursor, shortcut, source)
        except:
            if scripts.DEBUG:
                print self.source_path
                print 'check_repetition: bad coded source:\n%s|%s' %(shortcut, source)
            repetition = True
        if not repetition:
            insert = """INSERT INTO `%s`
                        (shortcut, source, trans, create_time, uploader)
                        VALUES(%%s, %%s, %%s, %%s, %%s)""" % self.table_name
            value = (shortcut,source,trans,create_time, uploader)
            try:
                cursor.execute(insert, value)
            except :
                if scripts.DEBUG:
                    print self.trans_path
                    print 'found bad coded translation: %s|%s' %(shortcut, trans)

    def merge(self, conn, cursor, source_cont, trans_cont):
        for key in source_cont:
            if trans_cont.has_key(key):
                self.save_db(conn, cursor, 
                             key, source_cont[key], 
                             trans_cont[key])

    def add_dict(self, conn, cursor, file_name):
        self.table_name = file_name.split('.')[0]
        for mod in os.listdir('available source/'):
            self.source_path = 'available source/' + mod + '/en/' + file_name
            self.trans_path = 'available source/' + mod + '/cns/' + file_name
            source_cont = self.get_content(self.source_path)
            trans_cont = self.get_content(self.trans_path)
            create = """CREATE TABLE IF NOT EXISTS `%s`
                        (id INT PRIMARY KEY AUTO_INCREMENT,
                         shortcut VARCHAR(500) NOT NULL, 
                         source VARCHAR(5000) NOT NULL, 
                         trans VARCHAR(5000) NOT NULL, 
                         create_time VARCHAR(30) NOT NULL, 
                         uploader VARCHAR(20) NOT NULL)""" % self.table_name
            cursor.execute(create)
            print 'start merging %s/%s' % (mod, file_name)
            self.merge(conn, cursor, source_cont, trans_cont)
            print 'finish merging %s/%s' % (mod, file_name)

    def use_dict(self, conn, cursor, file_name):
        self.table_name = file_name.split('.')[0]
        source_path = 'ACOK1.3_en/' + file_name
        f = open('ACOK1.3_cns/' + file_name, 'w')
        source_cont = mydict.get_content(source_path)
        print 'start auto-translating %s' % source_path
        total_num = len(source_cont)
        done_num = 0
        for key in source_cont:
            select = """SELECT trans FROM `%s` 
                        WHERE (shortcut, source) =(%%s, %%s) 
                        LIMIT 1""" % self.table_name
            cursor.execute(select, (key, source_cont[key]))
            result = cursor.fetchone()
            if result:
                source_cont[key] = result[0]
                done_num += 1
            else:
                select = """SELECT trans FROM `%s` 
                            WHERE source=%%s 
                            LIMIT 1""" % self.table_name 
                cursor.execute(select, (source_cont[key],))
                temp = cursor.fetchone()
                if temp:
                    source_cont[key] = temp[0]
                    done_num += 1
            trans_list = [key, '|', source_cont[key], '\n']
            trans = ''.join(trans_list)
            f.write(trans.encode('utf8'))
        f.close()
        print 'finish auto-translating %s. degree: %s/%s' % (source_path, done_num, total_num)

if __name__ == '__main__':
    mydict = Mydict()
    conn = MySQLdb.connect(**scripts.LOGIN)
    cursor = conn.cursor()
    files = os.listdir('native_en/')
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