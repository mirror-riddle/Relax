# -*- coding: utf8 -*-
#!usr/bin/env python

import wx
import os
import sys
import mydict
import scripts
import logging
"""
===============================================================================
                            main menu
===============================================================================
"""


class MyApp(wx.App):

    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)

    def OnInit(self):
        self.frame = MyFrame(None)
        self.frame.save.Enable(False)
        # self.frame.addspace.Enable(False)
        self.frame.store.Enable(False)
        # self.frame.btn_addspace.Enable(False)
        self.frame.btn_store.Enable(False)
        self.frame.Show()
        return True


class MyFrame(wx.Frame):

    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent=None, title='Translation', size=(1200,600))

        self.conn, self.cursor = scripts.conn_mysql()
        panel = wx.Panel(self)

        menu_file = wx.Menu()
        load = menu_file.Append(-1, 'load', 'load file')
        menu_file.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.on_load, load)
        self.save = menu_file.Append(-1, 'save', 'save file')
        menu_file.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.on_save, self.save)
        exit = menu_file.Append(-1, 'exit', 'exit programe')
        self.Bind(wx.EVT_MENU, self.on_exit, exit)

        menu_edit = wx.Menu()
        # self.addspace = menu_edit.Append(-1, 'add space', 'add space')
        # menu_edit.AppendSeparator()
        # self.Bind(wx.EVT_MENU, self.on_addspace, self.addspace)
        self.store = menu_edit.Append(-1, 'store', 'store')
        self.Bind(wx.EVT_MENU, self.on_store, self.store)

        menu_tool = wx.Menu()
        self.add_dict = menu_tool.Append(-1, 'add dictionary', 'add dictionary')
        self.Bind(wx.EVT_MENU, self.on_add_dict, self.add_dict)
        menu_tool.AppendSeparator()
        self.apply_dict = menu_tool.Append(-1, 'use Translation', 'use Translation')
        self.Bind(wx.EVT_MENU, self.on_apply_dict, self.apply_dict)

        menu_help = wx.Menu()
        help_doc = menu_help.Append(-1, 'help documents', 'help documents')
        
        menu_bar = wx.MenuBar()
        menu_bar.Append(menu_file, 'file')
        menu_bar.Append(menu_edit, 'edit')
        menu_bar.Append(menu_tool, 'tool')
        menu_bar.Append(menu_help, 'help')
        self.SetMenuBar(menu_bar)
        self.CreateStatusBar()

        self.list_en = wx.ListCtrl(panel, style=wx.LC_REPORT|wx.LC_HRULES|
                                                wx.LC_VRULES|wx.LC_SINGLE_SEL)
        self.list_en.InsertColumn(0, 'id')    
        self.list_en.InsertColumn(1, 'source')
        self.list_en.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selected)

        # btn_load = wx.Button(panel, label='Load')
        # btn_load.Bind(wx.EVT_BUTTON, self.load)
        # self.btn_addspace = wx.Button(panel, label='Add space')
        # self.btn_addspace.Bind(wx.EVT_BUTTON, self.on_addspace)
        # btn_save = wx.Button(panel, label='Save')
        # btn_save.Bind(wx.EVT_BUTTON, self.save)
        self.btn_store = wx.Button(panel, label='Store')
        self.btn_store.Bind(wx.EVT_BUTTON, self.on_store)

        self.cont_en = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.cont_cns = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.cont_cns.Bind(wx.EVT_TEXT, self.on_cns)
        self.cont_cns_space = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.cont_cns_space.Bind(wx.EVT_TEXT, self.on_cns_space)
        # self.contents_stored = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        # self.contents_log = wx.TextCtrl(panel, style=wx.TE_MULTILINE)

        # hbox0 = wx.BoxSizer()
        # hbox0.Add(self.file_name, proportion=1, flag=wx.EXPAND)
        # hbox0.Add(btn_load, proportion=0, flag=wx.EXPAND | wx.LEFT, border=5)

        hbox1 = wx.BoxSizer()
        hbox1.Add(self.list_en, proportion=1, flag=wx.EXPAND)

        hbox2 = wx.BoxSizer()
        hbox2.Add(self.cont_en, proportion=1, flag=wx.EXPAND)
        hbox2.Add(self.cont_cns, proportion=1, flag=wx.EXPAND)
        # hbox2.Add(self.btn_addspace, proportion=0, flag=wx.EXPAND | wx.LEFT, border=5)

        hbox3 = wx.BoxSizer()
        hbox3.Add(self.cont_cns_space, proportion=1, flag=wx.EXPAND)
        hbox3.Add(self.btn_store, proportion=0, flag=wx.EXPAND | wx.LEFT, border=5)

        # hbox4 = wx.BoxSizer()
        # hbox4.Add(self.contents_log, proportion=1, flag=wx.EXPAND)
        # hbox4.Add(self.contents_stored, proportion=1, flag=wx.EXPAND)
        # hbox4.Add(btn_save, proportion=0, flag=wx.EXPAND | wx.LEFT, border=5)

        vbox = wx.BoxSizer(wx.VERTICAL)
        # vbox.Add(hbox0, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(hbox1, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(hbox2, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(hbox3, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        # vbox.Add(hbox4, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        panel.SetSizer(vbox)

    def on_load(self, event):
        self.file_path, self.file_name = self.dialog_get_file()
        if self.file_path:
            temp = scripts.get_source_list(self.file_path)
            self.source_list, self.reject_list = temp
            for col, source in enumerate(self.source_list):
                index = self.list_en.InsertStringItem(col, str(col+1))
                self.list_en.SetStringItem(index, 1, source)
            self.list_en.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            self.list_en.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self.save.Enable(True)
            self.cont_en.SetValue('')
            self.clear_cn()

    def on_selected(self, event):
        self.index = event.GetIndex()
        line = self.source_list[self.index]
        self.line_list = scripts.get_line_list(line)
        self.cont_en.SetValue(self.line_list[1])
        self.clear_cn()
        self.search_trans()

    def search_trans(self):
        table = os.path.splitext(self.file_name)[0]
        shortcut = self.line_list[0]
        source = self.line_list[1]
        select = """SELECT translation FROM `%s` WHERE shortcut LIKE %%s
                    OR source LIKE %%s LIMIT 1""" % table
        try:
            self.cursor.execute(select, (shortcut, source))
        except Exception, e:
            logging.debug('='*50)
            debug_list = [e, self.file_path, shortcut, source]
            for item in debug_list:
                logging.error(item)
        else:
            result = self.cursor.fetchone()
            if result:
                self.cont_cns_space.SetValue(result[0])

    # def on_addspace(self, event):
    #     usr_input = self.cont_cns.GetValue()     #usr_input coding: unicode
    #     usr_input_space = scripts.add_space(usr_input)
    #     self.cont_cns_space.SetValue(usr_input_space)

    def on_store(self, event):
        raw_trans = self.cont_cns_space.GetValue()
        trans = scripts.get_trans(self.line_list, raw_trans)
        if trans:
            self.source_list[self.index] = trans
            self.list_en.SetStringItem(self.index, 1, trans)

    def on_save(self, event):
        trans_file = open(self.file_path, 'w')
        for source in self.source_list:
            trans_file.write(source.encode('utf8'))
        for source in self.reject_list:
            trans_file.write(source)
        trans_file.close()

    def on_add_dict(self, event):
        create_dict = mydict.Mydict()
        en_dir = self.dialog_get_dir('en')
        cns_dir = self.dialog_get_dir('cns')
        if en_dir and cns_dir:
            file_list = os.listdir(en_dir)
            file_list.sort()
            for file_name in file_list:
                create_dict.add_db(self.conn, self.cursor, file_name, en_dir, cns_dir)
        self.conn.commit()
        logging.info('#'*100)
        print 'done!'

    def on_apply_dict(self, event):
        conn, cursor = scripts.conn_mysql()
        apply_dict = mydict.Mydict()
        source_dir = self.dialog_get_dir('source')
        if source_dir:
            file_list = os.listdir(source_dir)
            file_list.sort()
            for file_name in file_list:
                apply_dict.use_db(self.conn, self.cursor, file_name, source_dir)
            logging.info('*'*100)
            print 'done!'

    def on_cns(self, event):
        cns = self.cont_cns.GetValue()
        self.cont_cns_space.SetValue(scripts.add_space(cns))
        # if cns:
        #     enable = True
        # else:
        #     enable = False
        # self.addspace.Enable(enable)
        # self.btn_addspace.Enable(enable)

    def on_cns_space(self, event):
        if self.cont_cns_space.GetValue():
            enable = True
        else:
            enable = False
        self.store.Enable(enable)
        self.btn_store.Enable(enable)

    def clear_cn(self):
        self.cont_cns.SetValue('')
        self.cont_cns_space.SetValue('')

    def dialog_get_file(self):
        dialog = wx.FileDialog(None, 'Choose a file', '', '', '*.csv', wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            file_name = dialog.GetFilename()
            result = (file_path, file_name)
        else:
            result = ('', '')
        return result
        dialog.Destroy()
        
    def dialog_get_dir(self, language):
        message = 'Choose %s directory' % language
        dialog = wx.DirDialog(None, message, style=0)
        if dialog.ShowModal() == wx.ID_OK:
            dir_path = dialog.GetPath()
        else:
            dir_path = ''
        return dir_path
        dialog.Destroy()
    
    def on_exit(self, event):
        scripts.disc_mysql(self.conn, self.cursor)
        self.Close()

if __name__ == '__main__':
    scripts.config_logging()
    app = MyApp()
    app.MainLoop()
