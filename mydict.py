# -*- coding: utf8 -*-
# !usr/bin/env python

"""
===============================================================================
    Create dict from available trans and use it for auto-translating.
===============================================================================
"""

import os
import wx
import scripts
import logging


class CreateDict(object):

    """add new source and translation to database"""

    def add_db(self, database, file_name, en_dir, cns_dir):
        collection = os.path.splitext(file_name)[0]
        self.source_path = os.path.join(en_dir, file_name)
        self.trans_path = os.path.join(cns_dir, file_name)
        self.source_dict = scripts.get_dict(self.source_path)[0]
        self.trans_dict = scripts.get_dict(self.trans_path)[0]
        self.collection = database[collection]
        logging.info('start merging %s' % self.source_path)
        self.insert_db()
        logging.info('finish merging %s' % self.source_path)

    def insert_db(self):
        create_time = scripts.get_cur_time()
        total_count = len(self.source_dict)
        done_count = 0
        title = 'merging %s.csv' % self.collection
        message = 'merging %s and %s' % (self.source_path, self.trans_path)
        style = wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT
        dialog = wx.ProgressDialog(title=title, message=message,
                                   maximum=total_count, parent=None,
                                   style=style,
                                   )
        icon = wx.Icon('resources/relax.ico', wx.BITMAP_TYPE_ANY)
        dialog.SetIcon(icon)
        for key in self.source_dict:
            value = self.source_dict[key]
            if key in self.trans_dict and value != self.trans_dict[key]:
                if not self.check_repeat(key):
                    insert_item = {'shortcut': key,
                                   'create_time': create_time,
                                   'source': self.source_dict[key],
                                   'translation': self.trans_dict[key]
                                   }
                    self.collection.insert(insert_item)
            done_count += 1
            dialog.Update(done_count)
        dialog.Destroy()

    def check_repeat(self, shortcut):
        criteria = {'shortcut': shortcut, 'source': self.source_dict[shortcut]}
        projection = {'shortcut': 1, '_id': 0}
        result = self.collection.find_one(criteria, projection)
        if result:
            return True
        else:
            return False


class ApplyDict(object):

    """query translation from databse and auto-translate"""

    def use_db(self, database, file_name, source_dir, save_dir):
        collection = os.path.splitext(file_name)[0]
        self.collection = database[collection]
        self.source_path = os.path.join(source_dir, file_name)
        self.source_dict, self.reject_list = scripts.get_dict(self.source_path)
        self.save_path = os.path.join(save_dir, file_name)
        with open(self.save_path, 'w') as save_file:
            logging.info('start auto-translating %s' % self.source_path)
            # print 'start auto-translating %s' %source_path
            self.query_and_write(save_file)
            logging.info('finish auto-translating %s' % self.source_path)
            # print 'finish auto-translating %s' %source_path

    def query_and_write(self, save_file):
        done_num = done_count = 0
        trans_list = []
        total_num = len(self.source_dict)
        title = 'translating %s.csv' % self.collection
        message = 'translating %s to %s' % (self.source_path, self.save_path)
        dialog = wx.ProgressDialog(title=title, message=message,
                                   maximum=total_num, parent=None,
                                   style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE,
                                   )
        for key in self.source_dict:
            value = self.source_dict[key]
            criteria = {'shortcut': key, 'source': value}
            projection = {'translation': 1, '_id': 0}
            result = self.collection.find_one(criteria, projection)
            if result:
                self.source_dict[key] = result.get('translation')
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

        logging.info('translation rate: %s/%s' % (done_num, total_num))
        # print 'translation rate: %s/%s' %(done_num, total_num)
