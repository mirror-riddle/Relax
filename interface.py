# -*- coding: utf-8 -*-
#!usr/bin/env python

import wx
import sys
import pickle
import scripts
import mysql

CODING = sys.getfilesystemencoding()

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
        return True


class MyFrame(wx.Frame):

    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent=None, title='Translation', size=(800, 600))

        panel = wx.Panel(self)
        btn_load = wx.Button(panel, label='Load')
        btn_skip = wx.Button(panel, label='Skip')
        btn_space = wx.Button(panel, label='Add space')
        btn_save = wx.Button(panel, label='Save')
        btn_store = wx.Button(panel, label='Store')

        self.file_name = wx.TextCtrl(panel, value='uimain.csv')
        self.contents_en = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.contents_cn = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.contents_cn_space = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.contents_stored = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.contents_log = wx.TextCtrl(panel, style=wx.TE_MULTILINE)

        hbox0 = wx.BoxSizer()
        hbox0.Add(self.file_name, proportion=1, flag=wx.EXPAND)
        hbox0.Add(btn_load, proportion=0, flag=wx.EXPAND | wx.LEFT, border=5)

        hbox1 = wx.BoxSizer()
        hbox1.Add(self.contents_en, proportion=1, flag=wx.EXPAND)
        hbox1.Add(btn_skip, proportion=0, flag=wx.EXPAND | wx.LEFT, border=5)

        hbox2 = wx.BoxSizer()
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
        btn_skip.Bind(wx.EVT_BUTTON, self.skip)
        btn_space.Bind(wx.EVT_BUTTON, self.addspace)
        btn_store.Bind(wx.EVT_BUTTON, self.store)
        btn_save.Bind(wx.EVT_BUTTON, self.save)

    def load(self, event):
        self.current_translation = []
        self.f_en = open(self.file_name.GetValue(), 'U')
        with open('offset.txt', 'a+') as f_offset:
            self.offset = scripts.get_offset(f_offset)
            self.f_en.seek(self.offset)
        self.nextline(wx.EVT_BUTTON)
        self.print_stored('Welcome!'.center(69, '='))
        self.print_log(
            '{0}>>>LOAD:{1}'.format(scripts.cur_time(),
                                     self.file_name.GetValue()))

    def nextline(self, event):
        self.source = self.f_en.readline().decode(CODING)
        self.source_txt = scripts.get_source_txt(self.source)
        self.contents_en.SetValue(self.source_txt[1])
        self.contents_cn.SetValue('')
        self.contents_cn_space.SetValue('')

    def addspace(self, event):
        usr_input = self.contents_cn.GetValue()
        usr_input_space = scripts.add_space(usr_input)
        self.contents_cn_space.SetValue(usr_input_space)
        if  self.contents_cn.GetValue():
            self.print_log(
                '{0}>>>ADD SPACE:{2}'.format(scripts.cur_time(),
                                             usr_input.encode(CODING),
                                             usr_input_space.encode(CODING)))

    def store(self, event):
        raw_translation = self.contents_cn_space.GetValue()
        translation = scripts.get_translation(self.source_txt,
            raw_translation)
        if translation not in self.current_translation:
            self.current_translation.append(translation)
            if translation:
                self.print_stored(translation.strip('\n'))
                self.offset = self.f_en.tell()
                self.nextline(wx.EVT_BUTTON)
                self.print_log(
                    '{0}>>>STORE LINE:{1}'.format(scripts.cur_time(),
                    translation.strip('\n').encode(CODING)))

    def skip(self, event):
        with open('undone.csv', 'a') as f_undone:
            f_undone.write(self.source)
        self.offset = self.f_en.tell()
        self.save_offset(self.offset)
        self.nextline(wx.EVT_BUTTON)
        self.print_log('{0}>>> SKIP LINE {1}'.format(scripts.cur_time(),
            self.source.strip('\n')))

    def save(self, event):
        if self.current_translation:
            with open('uimain_cn.csv', 'a') as f_cns:
                for line in self.current_translation:
                    f_cns.write(line.encode(CODING))
                    self.print_log('{0}>>> SAVE CONTENTS: {1}'.format(
                        scripts.cur_time(), line.strip('\n').encode(CODING)))
                self.save_offset(self.offset)
                self.current_translation = []

    def save_offset(self, offset):
        with open('offset.txt', 'w') as f_offset:
            pickle.dump(offset, f_offset)
            self.print_log('{0}>>> SAVE OFFSET: {1}'.format(scripts.cur_time(),
                self.offset))

    def print_stored(self, sth):
        sys.stdout = self.contents_stored
        print sth

    def print_log(self, sth):
        sys.stdout = self.contents_log
        print sth

    def OnExit(self):
        self.f_en.close()




if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()
