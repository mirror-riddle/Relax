# -*- coding: utf-8 -*-
#!usr/bin/env python

import  MySQLdb
import  scripts
import  time
import  sys
import os

CODING = sys.getfilesystemencoding()

'''
    =========================================================================================================
            class Translationmydict save source and translation to dababase, and retrive them when needed
    =========================================================================================================

'''

login = {'host'  :'127.0.0.1', 'user':'root',
         'passwd':'Aa68553^', 'db':'translation', 'charset':'utf8'}           #must be utf8, can't be utf-8



class Translationmydict(object):


    def get_contents(self, file_name, is_translation = True):
        with open(file_name, 'U') as f:
            contents = f.readlines()
        for line in contents:
            index = contents.index(line)
            if index == 0:
                line = line.lstrip('\xef\xbb\xbf')           # cut off coding definition at the begining of file
            if is_translation:
                line = line.decode('utf8')
            source = scripts.get_source_txt(line)
            contents[index] = source
        return contents

    def check_repetition(self, cursor, shortcut, source):
            cursor.execute('SELECT * FROM mydict WHERE (shortcut, source)=(%s, %s)', (shortcut, source,))
            results = cursor.fetchall()     # results coding: unicode
            #print results                  # format is: ((translation1,),(translation2,))
            if results:
                repetition = True
            else:
                repetition = False
            return repetition

    def save_to_database(self,conn, cursor, shortcut, source, translation, uploader):
        create_time = time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        repetition = self.check_repetition(cursor,shortcut, source)
        if not repetition:                       #check if translation already exists.
            cursor.execute('INSERT INTO mydict(shortcut,source, translation, create_time, uploader) VALUES(%s,%s,%s,%s,%s)',(shortcut,source,translation,create_time,uploader))
        conn.commit()

    def merge_contents(self, conn, cursor, source_contents, translation_contents, uploader):
        for source_content in source_contents:
            for translation_content in translation_contents:
                if source_content[0].decode('utf8') == translation_content[0]:
                    self.save_to_database(conn, cursor, source_content[0], source_content[1], translation_content[1], uploader)
                    break



def create_dict(conn, cursor, dict_object, file_name):
    source_path = ''.join(('native_en/', file_name))
    translation_path = ''.join(('native_cns/', file_name))
    source_contents = dict_object.get_contents(source_path, is_translation=False)
    translation_contents = dict_object.get_contents(translation_path, is_translation=True)
    #uploader = raw_input('uploader name: ')
    uploader = 'hejin'.decode(CODING)
    cursor.execute('CREATE TABLE IF NOT EXISTS mydict(id INT PRIMARY KEY AUTO_INCREMENT, shortcut VARCHAR(500) NOT NULL, source VARCHAR(5000) NOT NULL, translation VARCHAR(5000) NOT NULL, create_time VARCHAR(30) NOT NULL, uploader VARCHAR(20) NOT NULL)')
    print 'start merging %s' % file_name
    dict_object.merge_contents(conn, cursor, source_contents, translation_contents, uploader)
    print 'finish merging %s' % file_name

def use_dict(conn, cursor, dict_object, file_name):
    source_path = 'ACOK1.3_en/'+file_name
    f = open('ACOK1.3_cns/'+file_name, 'w')
    source_contents = dict_object.get_contents(source_path, is_translation=False)
    print 'start translating %s' % file_name
    for content in source_contents:
        cursor.execute('SELECT translation FROM mydict WHERE source=%s', (content[1],))
        results = cursor.fetchall()
        if results:
            result = results[0]
            if len(results) > 1:              
                cursor.execute('SELECT translation FROM mydict WHERE shortcut=%s', (content[0],))
                temp = cursor.fetchone()
                if temp:
                    result = temp
            content[1] = result[0]
        translation = ''.join((content[0], '|', content[1], '\n'))
        f.write(translation.encode('utf8'))
    f.close()
    print 'finish translating %s' % file_name

if __name__ == '__main__':
    dict_object = Translationmydict()
    conn = MySQLdb.connect(**login)
    cursor = conn.cursor()
    files = os.listdir('ACOK1.3_en/')
    files.sort()
    option = raw_input('create_dict: 1\nuse_dict: 2\nyour option:')
    for file_name in files:
        if option =='1':
            create_dict(conn, cursor, dict_object, file_name)
        elif option =='2':
            use_dict(conn, cursor, dict_object, file_name)
    cursor.close()
    conn.close()