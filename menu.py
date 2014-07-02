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
        self.frame.store.Enable(False)
        self.frame.undo.Enable(False)
        self.frame.redo.Enable(False)
        self.frame.Show()
        return True


class MyFrame(wx.Frame):


    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent=None, title='Relax', size=(1000,600))

        #connect to mysql-server
        self.conn, self.cursor = scripts.conn_mysql()

        #config logging 
        scripts.config_logging()

        #setup font
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetStyle(wx.FONTSTYLE_NORMAL)
        font.SetPointSize(11)

        #load and setup icon and taskbar icon.
        icon = wx.Icon('pictures/relax.ico')
        self.SetIcon(icon)
        self.taskbar_icon = wx.TaskBarIcon(wx.TBI_DOCK)
        self.taskbar_icon.SetIcon(icon, 'Relax')
        # self.taskbar_icon.CreatePopupMenu()
        
        
        #when window close
        self.Bind(wx.EVT_CLOSE, self.on_close)

        #create panel
        panel = wx.Panel(self)

        #menu 0 File
        menu_file = wx.Menu()
        load = menu_file.Append(-1, '&Open\tCtrl+O', 'Open file')
        menu_file.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.on_load, load)
        self.save = menu_file.Append(-1, '&Save\tCtrl+S', 'Save file')
        menu_file.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.on_save, self.save)
        self.save_as = menu_file.Append(-1, '&Save as...\tCtrl+Shift+S', 'Save as...')
        menu_file.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.on_save_as, self.save_as)
        exit = menu_file.Append(-1, '&Exit\tCtrl+E', 'Exit')
        self.Bind(wx.EVT_MENU, self.on_exit, exit)
        
        #menu 1 Edit
        menu_edit = wx.Menu()
        self.undo = menu_edit.Append(-1, '&Undo\tCtrl+Z', 'Undo')
        self.Bind(wx.EVT_MENU, self.on_undo, self.undo)
        self.redo = menu_edit.Append(-1, '&Redo\tCtrl+Y', 'Redo')
        self.Bind(wx.EVT_MENU, self.on_redo, self.redo)
        self.store = menu_edit.Append(-1, '&Confirm\tCtrl+enter', 'Confirm')
        self.Bind(wx.EVT_MENU, self.on_store, self.store)

        #menu 2 Tools
        menu_tool = wx.Menu()
        self.add_dict = menu_tool.Append(-1, '&Add dictionary\tCtrl+D', 'Add dictionary')
        self.Bind(wx.EVT_MENU, self.on_add_dict, self.add_dict)
        menu_tool.AppendSeparator()
        self.apply_dict = menu_tool.Append(-1, '&Use dictionary\tCtrl+Shift+D', 'Use dictionary')
        self.Bind(wx.EVT_MENU, self.on_apply_dict, self.apply_dict)

        #Menu 3 Help
        menu_help = wx.Menu()
        help_doc = menu_help.Append(-1, '&Help documents\tCtrl+H', 'Help documents')
        
        #Menu Bar and Status Bar
        menu_bar = wx.MenuBar()
        menu_bar.Append(menu_file, 'File')
        menu_bar.Append(menu_edit, 'Edit')
        menu_bar.Append(menu_tool, 'Tools')
        menu_bar.Append(menu_help, 'Help')
        self.SetMenuBar(menu_bar)
        self.CreateStatusBar()

        #list_en: display contents of source file
        self.list_en = wx.ListCtrl(panel, -1, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.LC_SINGLE_SEL)
        self.list_en.SetFont(font)
        self.list_en.SetBackgroundColour('#C7EDCC')
        self.list_en.InsertColumn(0, 'line')
        self.list_en.InsertColumn(1, 'source')
        self.list_en.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selected)

        #cont_en: display raw source withour shortcut.
        #cont_cns: used to typing in usr_input
        #cont_cns_space: display translation with space but without shortcut.
        self.cont_en = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.cont_en.SetFont(font)
        self.cont_en.SetBackgroundColour('#C7EDCC')
        self.cont_cns = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.cont_cns.SetFont(font)
        self.cont_cns.SetBackgroundColour('#C7EDCC')
        self.cont_cns.Bind(wx.EVT_TEXT, self.on_cns_change)
        self.cont_cns.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.cont_cns_space = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.cont_cns_space.SetFont(font)
        self.cont_cns_space.SetBackgroundColour('#C7EDCC')
        self.cont_cns_space.Bind(wx.EVT_TEXT, self.on_cns_space)
        self.cont_cns_space.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        # 1 vertical box include 3 horizontal boxes.
        hbox1 = wx.BoxSizer()
        hbox1.Add(self.list_en, proportion=1, flag=wx.EXPAND)
        hbox2 = wx.BoxSizer()
        hbox2.Add(self.cont_en, proportion=1, flag=wx.EXPAND)
        hbox2.Add(self.cont_cns_space, proportion=1, flag=wx.EXPAND)
        hbox3 = wx.BoxSizer()
        hbox3.Add(self.cont_cns, proportion=1, flag=wx.EXPAND)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox1, proportion=4, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(hbox2, proportion=3, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(hbox3, proportion=3, flag=wx.EXPAND | wx.ALL, border=5)

        panel.SetSizer(vbox)
        panel.Fit()        #must have this


    #Get name, path of a source file, display its contents in list_en
    def on_load(self, event):
        self.undo_dict = {'index': '', 'source': '', 'usr_input': '', 'raw_trans': '', 'trans': ''}
        self.redo_dict = {'index': '', 'trans': '', 'cur_index': ''}
        file_path, file_name = self.dialog_get_file()
        #only change path when file_name is really reseted,
        #in which case file_path can be True while file_name is ''.
        if file_name:
            self.SetTitle('%s - Relax' %file_path)    #reset window title.
            self.list_en.DeleteAllItems()
            self.file_path, self.file_name = (file_path, file_name)
            self.source_list, self.reject_list = scripts.get_source_list(self.file_path)
            total_count = len(self.source_list)
            done_count = 0
            title = 'Loading %s' %self.file_name
            message = 'Loading %s' %self.file_path
            dialog = wx.ProgressDialog(title=title, message=message, maximum=total_count, 
                                   parent=None, style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE
                                   )
            for col, source in enumerate(self.source_list):
                index = self.list_en.InsertStringItem(col, str(col))
                self.list_en.SetStringItem(index, 1, source)
                done_count += 1
                dialog.Update(done_count)
                dialog.Destroy()

            self.list_en.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self.list_en.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self.save.Enable(True)
            self.cont_en.SetValue('')
            self.clear_cn()


    #Get the selected source, display it in cont_en
    #and search possible translation in mysql database.
    def on_selected(self, event):
        self.index = self.list_en.GetFocusedItem()
        self.redo_dict['cur_index'] = self.index
        #can't get full text by 'listitem.GetText()' when
        #text is very long, for which reason is unknown.
        self.source = self.source_list[self.index]
        self.shortcut, self.raw_source = scripts.get_line_list(self.source)
        self.cont_en.SetValue(self.raw_source)
        self.clear_cn()
        self.search_trans()


    #Get the translation with shortcut and breakline, replace the source
    #in list_en with it.
    def on_store(self, event):
        index = self.index
        self.undo_dict['index'] = index
        self.redo_dict['index'] = index
        self.undo_dict['source'] = self.source_list[index]
        usr_input = self.cont_cns.GetValue()
        self.undo_dict['usr_input'] = usr_input
        raw_trans = self.cont_cns_space.GetValue()
        self.undo_dict['raw_trans'] = raw_trans
        trans = scripts.get_translation(self.shortcut, raw_trans)
        self.undo_dict['trans'] = trans
        self.redo_dict['trans'] = trans

        self.source_list[self.index] = trans
        self.list_en.SetStringItem(index, 1, trans)

        self.undo.Enable(True)
        self.redo.Enable(True)


    #Save file to overwrite original one. Messed coding line will be moved to the end.
    def on_save(self, event):
        self.save_file(self.file_path, self.source_list, self.reject_list)


    #save file as...
    def on_save_as(self, event):
        file_path = self.dialog_save_file(self.file_name)
        self.save_file(file_path, self.source_list, self.reject_list)


    #When choose menu_add dictionary.
    def on_add_dict(self, event):
        create_dict = mydict.Createdict()
        en_dir = self.dialog_get_dir('source')
        cns_dir = self.dialog_get_dir('translation')

        if en_dir and cns_dir:
            file_list = os.listdir(en_dir)
            file_list.sort()
            logging.info('add_dict_begin' + '*'*100)
            for file_name in file_list:
                create_dict.add_db(self.cursor, file_name, en_dir, cns_dir, progress_dialog1)
        self.conn.commit()

        logging.info('add_dict_begin' + '*'*100)


    #When choose menu_use dictionary.
    def on_apply_dict(self, event):
        apply_dict = mydict.Applydict()
        source_dir = self.dialog_get_dir('source')
        save_dir = self.dialog_get_dir('save')
        if not save_dir:
            message = 'You must choose a directory to save file!'
            title = 'No directory chosen for saving file'
            dialog = wx.MessageDialog(self, message, title, wx.OK | wx.ICON_INFORMATION)
            dialog.ShowModal()
            dialog.Destroy()
        elif source_dir:
            file_list = os.listdir(source_dir)
            file_list.sort()
            logging.info('apply_dict_begin' + '*'*100)
            for file_name in file_list:
                apply_dict.use_db(self.cursor, file_name, source_dir, save_dir)
            logging.info('apply_dict_end' + '*'*100)


    #Instantly add space when typing raw translation.
    def on_cns_change(self, event):
        cns = self.cont_cns.GetValue()
        cns_space = scripts.add_space(cns)
        self.cont_cns_space.SetValue(cns_space)


    #Menu_store is enabled when there is a translation.
    def on_cns_space(self, event): 
        if self.cont_cns_space.GetValue():
            enable = True
        else:
            enable = False
        self.store.Enable(enable)


    #Store translation when 'Enter' is pressed.
    def on_key_down(self, event):
        key = event.GetKeyCode()
        # if press 'Enter', store transaltion
        if key == 13:
            if self.cont_cns_space.GetValue():
                self.on_store(wx.EVT_MENU)
                index = self.index + 1
                self.list_en.Focus(index)
                #this will trigger self.on_selected()
                self.list_en.SetItemState(index, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        elif key in (314, 315, 316, 317):
            if key == 314:
                index = self.index - 5        #if press wxk_left, index - 5
            elif key == 315:
                index = self.index - 1        #if press wxk_up, index - 1
            elif key == 316:
                index = self.index + 5        #if press wxk_right, index + 5
            elif key == 317:
                index = self.index + 1        #if press wxk_down, index + 1
            self.list_en.Focus(index)
            self.list_en.SetItemState(index, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        else:
            event.Skip()


    #Undo last operation.
    def on_undo(self, event):
        index = self.undo_dict['index']
        source = self.undo_dict['source']
        usr_input = self.undo_dict['usr_input']
        raw_trans = self.undo_dict['raw_trans']
        trans = self.undo_dict['trans']

        self.list_en.Focus(index)
        self.source_list[index] = source
        self.list_en.SetStringItem(index, 1, source)
        self.list_en.SetItemState(index, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        self.cont_cns.SetValue(usr_input)
        self.cont_cns_space.SetValue(raw_trans)

    #Redo last operation
    def on_redo(self, event):
        trans = self.redo_dict['trans']
        index =  self.redo_dict['index']
        cur_index = self.redo_dict['cur_index']

        self.source_list[index] = trans
        self.list_en.SetStringItem(index, 1, trans)
        self.list_en.Focus(cur_index)
        self.list_en.SetItemState(cur_index, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)


   #Disconnect from mysql-server and close window when exit.
   #This is how it work when click menu_exit
    def on_exit(self, event):
        scripts.disc_mysql(self.conn, self.cursor)
        self.taskbar_icon.RemoveIcon()
        self.Close()


    #This is how it work when click the X button.
    def on_close(self, event):
        self.Destroy()
        self.taskbar_icon.RemoveIcon()


    #Search translation from mysql database when source is selected.
    def search_trans(self):
        table = os.path.splitext(self.file_name)[0]
        select = """SELECT translation FROM `%s` WHERE shortcut LIKE %%s OR source LIKE %%s LIMIT 1""" % table
        #record error : 'utf8' codec can't decode byte 0x85 in position...
        #due to line with unwanted character, may remove this exception if
        #mysql character and collation are both set properly.
        try:
            self.cursor.execute(select, (self.shortcut, self.raw_source))
        except Exception, e:
            logging.debug('='*50)
            debug_list = [e, self.file_path, self.shortcut, self.raw_source]
            for item in debug_list:
                logging.error(item)
        else:
            result = self.cursor.fetchone()
            if result:
                self.cont_cns_space.SetValue(result[0])


    #Clear cont_cns and cont_cns_space.
    def clear_cn(self):
        self.cont_cns.SetValue('')
        self.cont_cns_space.SetValue('')


    #Dialog to get source file for translating.
    @staticmethod
    def dialog_get_file():
        dialog = wx.FileDialog(
            None, message='Choose a file', defaultDir=os.getcwd(),
            defaultFile='', wildcard='*.csv', style=wx.OPEN
            )
        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            file_name = dialog.GetFilename()
            result = (file_path, file_name)
        else:
            result = ('', '')
        return result
        dialog.Destroy()
        

    #Dialog to save file.
    @staticmethod
    def dialog_save_file(file_name):
        dialog = wx.FileDialog(
            None, message='Save file as ...', defaultDir=os.getcwd(),
            defaultFile=file_name, wildcard='*.csv', style=wx.SAVE
            )
        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
        return file_path
        dialog.Destroy()


    #Dialog to get source or translation directory, depending on language.
    @staticmethod
    def dialog_get_dir(dir_type):
        message = 'Choose %s directory' % dir_type
        dialog = wx.DirDialog(None, message, style=0)
        if dialog.ShowModal() == wx.ID_OK:
            dir_path = dialog.GetPath()
        else:
            dir_path = ''
        return dir_path
        dialog.Destroy()


    #save file
    @staticmethod
    def save_file(file_path, source_list, reject_list):
        with open(file_path, 'w') as trans_file:
            #source_list coding：Unicode
            #reject_list coding: messed
            #source in reject_list fails when trying to source.encode('utf8')
            new_source_list = []
            for source in source_list:
                new_source_list.append(source.encode('utf8'))
            new_source_list.extend(reject_list)
            for source in new_source_list:
                trans_file.write(source)



if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()