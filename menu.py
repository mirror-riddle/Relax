# -*- coding: utf-8 -*-
#!usr/bin/env python

import wx
import sys
import mydict
import scripts
import MySQLdb

"""
    =======================================================
                        main file
    =======================================================
"""


class MyApp(wx.App):

    def __init__(self, redirect=True, filename=None):
        wx.App.__init__(self, redirect, filename)

    def OnInit(self):
        self.frame = MyFrame(None)
        self.frame.Show()
        self.frame.load(wx.EVT_BUTTON)
        return True


class MyFrame(wx.Frame):

    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent=None, title='Translation', size=(800, 600))

        panel = wx.Panel(self)
        btn_load = wx.Button(panel, label='Load')
        btn_space = wx.Button(panel, label='Add space')
        btn_save = wx.Button(panel, label='Save')
        btn_store = wx.Button(panel, label='Store')

        self.file_name = wx.TextCtrl(panel, value='info_pages.csv')
        self.list_en = wx.ListCtrl(panel, style=wx.LC_REPORT|
                                                wx.LC_HRULES|
                                                wx.LC_VRULES|
                                                wx.LC_SINGLE_SEL)
        self.list_en.InsertColumn(0, 'id')    
        self.list_en.InsertColumn(1, 'source')
        self.contents_en = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.contents_cn = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.contents_cn_space = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.contents_stored = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.contents_log = wx.TextCtrl(panel, style=wx.TE_MULTILINE)

        hbox0 = wx.BoxSizer()
        hbox0.Add(self.file_name, proportion=1, flag=wx.EXPAND)
        hbox0.Add(btn_load, proportion=0, flag=wx.EXPAND | wx.LEFT, border=5)

        hbox1 = wx.BoxSizer()
        hbox1.Add(self.list_en, proportion=1, flag=wx.EXPAND)

        hbox2 = wx.BoxSizer()
        hbox2.Add(self.contents_en, proportion=1, flag=wx.EXPAND)
        hbox2.Add(self.contents_cn, proportion=1, flag=wx.EXPAND)
        hbox2.Add(btn_space, proportion=0, flag=wx.EXPAND | wx.LEFT, border=5)

        hbox3 = wx.BoxSizer()
        hbox3.Add(self.contents_cn_space, proportion=1, flag=wx.EXPAND)
        hbox3.Add(btn_store, proportion=0, flag=wx.EXPAND | wx.LEFT, border=5)

        hbox4 = wx.BoxSizer()
        hbox4.Add(self.contents_log, proportion=1, flag=wx.EXPAND)
        hbox4.Add(self.contents_stored, proportion=1, flag=wx.EXPAND)
        hbox4.Add(btn_save, proportion=0, flag=wx.EXPAND | wx.LEFT, border=5)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox0, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(hbox1, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(hbox2, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(hbox3, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(hbox4, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        panel.SetSizer(vbox)

        btn_load.Bind(wx.EVT_BUTTON, self.load)
        btn_space.Bind(wx.EVT_BUTTON, self.addspace)
        btn_store.Bind(wx.EVT_BUTTON, self.store)
        btn_save.Bind(wx.EVT_BUTTON, self.save)
        self.list_en.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_selected)

    def load(self, event):
        conn = MySQLdb.connect(**scripts.LOGIN)
        self.cursor = conn.cursor()
        self.list_en.DeleteAllItems()
        with open(self.file_name.GetValue(), 'U') as source_file:
            self.source_list = source_file.readlines()
        for col, source in enumerate(self.source_list):
            source = source.decode(scripts.CODING)
            index = self.list_en.InsertStringItem(sys.maxint, str(col))
            self.list_en.SetStringItem(index, 1, source)
        self.list_en.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.list_en.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.clear_cn()

    def on_item_selected(self, event):
        self.index = event.GetIndex()
        # source = self.list_en.GetItemText(index, 1)
        # print source
        source = self.source_list[self.index]
        self.source_txt = scripts.get_source_txt(source)
        self.contents_en.SetValue(self.source_txt[1])
        self.clear_cn()
        self.search_trans()

    def search_trans(self):
        self.table_name = self.file_name.GetValue().split('.')[0]
        select = """SELECT trans FROM `%s` 
                    WHERE shortcut LIKE %%s
                    OR source LIKE %%s
                    LIMIT 2""" % (self.table_name)
        self.cursor.execute(select, (self.source_txt[0], self.source_txt[1]))
        results = self.cursor.fetchall()
        for result in results:
            self.contents_cn_space.AppendText(result[0])

    def addspace(self, event):
        usr_input = self.contents_cn.GetValue()     #usr_input coding: unicode
        usr_input_space = scripts.add_space(usr_input)
        self.contents_cn_space.SetValue(usr_input_space)

    def store(self, event):
        raw_translation = self.contents_cn_space.GetValue()
        translation = scripts.get_translation(self.source_txt, raw_translation)
        if translation:
            self.source_list[self.index] = translation
            self.list_en.SetStringItem(self.index, 1, translation)

    def save(self, event):
        translation_file = open(self.file_name.GetValue(), 'w')
        for source in self.source_list:
            translation_file.write(source.encode(scripts.CODING))
        translation_file.close()

    def clear_cn(self):
        self.contents_cn.SetValue('')
        self.contents_cn_space.SetValue('')

if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()
