# -*- coding: utf8 -*-
#!usr/bin/env python

import os
import wx
import sys
import scripts
import logging
"""
===============================================================================
    Create dict from available trans and use it for auto-translating.
===============================================================================
"""


# class Mydict(object):
#     """
#     Two methods finish two jobs.
#     add_db: add new source and translation to database
#     use_db: query translation from databse and auto-translate
#     """

class Createdict(object):


    def add_db(self, cursor, file_name, en_dir, cns_dir, progress_dialog1):
        self.cursor = cursor
        self.table = os.path.splitext(file_name)[0]
        self.source_path = os.path.join(en_dir, file_name)
        self.trans_path = os.path.join(cns_dir, file_name)
        self.source_dict = scripts.get_dict(source_path)[0]
        self.trans_dict = scripts.get_dict(trans_path)[0]

        create = """CREATE TABLE IF NOT EXISTS `%s`(id INT PRIMARY KEY AUTO_INCREMENT,
                    shortcut VARCHAR(500) NOT NULL, source VARCHAR(8000) NOT NULL, 
                    translation VARCHAR(5000) NOT NULL, create_time VARCHAR(30) NOT NULL)""" %self.table
        self.cursor.execute(create)

        logging.info('start merging %s' % self.source_path)
        # print 'start merging %s' % self.source_path

        self.insert_db(progress_dialog1)

        logging.info('finish merging %s' % self.source_path)
        # print 'finish merging %s' % self.source_path


    def insert_db(self, progress_dialog1):
        create_time = scripts.cur_time()
        total_count = len(source_dict)
        done_count = 0
        title = 'merging %s.csv' %self.table
        message = 'merging %s and %s' %(self.source_path, self.trans_path)
        dialog = wx.ProgressDialog(title=title, message=message, maximum=total_count, 
                                   parent=progress_dialog1, style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE
                                   )
        for key in self.source_dict:
            if self.trans_dict.has_key(key) and self.source_dict[key] != self.trans_dict[key]:
                repeat = self.check_repeat(key)
                if not repeat:
                    insert = """INSERT INTO `%s`(shortcut, source, translation, create_time)
                                VALUES(%%s, %%s, %%s, %%s)""" % self.table
                    value = (key, self.source_dict[key], self.trans_dict[key], create_time)
                    #raise error when column length is not long enough.
                    try:
                        self.cursor.execute(insert, value)
                    except Exception, e:
                        logging.debug('='*100)
                        debug_list = [e, self.source_path, key, self.trans_dict[key]]
                        for item in debug_list:
                            logging.error(item)
            done_count += 1
            dialog.Update(done_count)
        dialog.Destroy()


    def check_repeat(self, shortcut):
        select = "SELECT id FROM `%s`WHERE (shortcut, source)=(%%s, %%s) LIMIT 1" %self.table
        #record error : Illegal mix of collations for operation = 
        try:
            self.cursor.execute(select, (shortcut, self.source_dict[key]))
        except Exception, e:
            logging.debug('='*100)
            debug_list = [e, self.source_path, shortcut, self.source_dict[key]]
            for item in debug_list:
                logging.error(item)
            repeat = True
        else:
            result = self.cursor.fetchone()     #result coding: unicode
            if result:
                repeat = True
            else:
                repeat = False
        return repeat



class Applydict(object):

        
    def use_db(self, cursor, file_name, source_dir, save_dir):
        self.cursor = cursor
        self.table = os.path.splitext(file_name)[0]
        self.source_path = os.path.join(source_dir, file_name)
        self.source_dict, self.reject_list = scripts.get_dict(self.source_path)
        self.save_path = os.path.join(save_dir, file_name)
        with open(self.save_path, 'w') as save_file:
            logging.info('start auto-translating %s' %self.source_path)
            # print 'start auto-translating %s' %source_path
            self.query_and_write(save_file)
            logging.info('finish auto-translating %s' %self.source_path)
            # print 'finish auto-translating %s' %source_path


    def query_and_write(self, save_file):
        done_num = done_count = 0
        trans_list = []
        total_num = len(self.source_dict)
        title = 'translating %s.csv' %self.table
        message = 'translating %s to %s' %(self.source_path, self.save_path)
        dialog = wx.ProgressDialog(title=title, message=message, maximum=total_num, 
                                   parent=None, style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE
                                   )
        for key in self.source_dict:
            value = self.source_dict[key]
            select = "SELECT translation FROM `%s` WHERE (shortcut, source) =(%%s, %%s) LIMIT 1" % self.table
            #record error when shortcut or source has mixed coding.
            try:
                self.cursor.execute(select, (key, value))
            except Exception, e:
                logging.debug('='*100)
                debug_list = [e, self.source_path, key, value]
                for item in debug_list:
                    logging.error(item)
            else:
                result = self.cursor.fetchone()
                if result:
                    self.source_dict[key] = result[0]  #value != source_dict[key] now
                    done_num += 1
            done_count += 1
            dialog.Update(done_count)

            trans = scripts.get_translation(key, self.source_dict[key])
            trans_list.append(trans.encode('utf8'))

        dialog.Destroy()
        trans_list.sort()
        trans_list.extend(self.reject_list)

        for trans_line in trans_list:
            save_file.write(trans_line)

        logging.info('translation rate: %s/%s' %(done_num, total_num))
        # print 'translation rate: %s/%s' %(done_num, total_num)
