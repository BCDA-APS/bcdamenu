#!/usr/bin/env python
#Boa:Frame:Frame1

#*************************************************************************
# Copyright (c) 2009 The University of Chicago, as Operator of Argonne
#     National Laboratory.
# Copyright (c) 2009 The Regents of the University of California, as
#     Operator of Los Alamos National Laboratory.
# This file is distributed subject to a Software License Agreement found
# in the file LICENSE that is included with this distribution.
#*************************************************************************

'''menuLauncher: Launch command-line statements from a wxPython menu

from: https://subversion.xray.aps.anl.gov/trac/small_angle/browser/USAXS/tools/menuUSAXS.py
'''


import wx
import subprocess
import os
import pprint


MENU_ITEMS = (
      ("9-ID-C USAXS controls (MEDM)", "start_epics"),
      ("separator", None),
      ("USAXS Q calculator", "qToolUsaxs.csh"),
      ("sample and detector XY position tool", "wxmtxy.csh"),
      ("USAXS sample stage tool", "/home/beams/USAXS/Apps/wxmtusaxs/wxmtusaxs"),
      ("PyMca", "/APSshare/bin/pymca"),
      ("SAXS Imaging tool", "/APSshare/epd/rh6-x86/bin/python /home/beams/USAXS/Apps/USAXS_dataworker/Main.py"),
      ("Save Instr. status to Elog", "saveToElog.csh")
    )


def create(parent):
    return Frame1(parent)


[wxID_FRAME1, wxID_FRAME1BUTTON1, wxID_FRAME1PANEL,
] = [wx.NewId() for _init_ctrls in range(3)]


[wxID_FRAME1THEMENUITEMS0, wxID_FRAME1THEMENUITEMS1,
] = [wx.NewId() for _init_coll_theMenu_Items in range(2)]


class Frame1(wx.Frame):

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FRAME1, name='', parent=prnt,
              pos=wx.Point(294, 331), size=wx.Size(223, 65),
              style=wx.DEFAULT_FRAME_STYLE, title='Frame1')
        self.SetClientSize(wx.Size(215, 31))

        self.panel = wx.Panel(id=wxID_FRAME1PANEL, name='panel', parent=self,
              pos=wx.Point(0, 0), size=wx.Size(215, 31),
              style=wx.TAB_TRAVERSAL)

        self.button1 = wx.Button(id=wxID_FRAME1BUTTON1, label='button1 label',
              name='button1', parent=self.panel, pos=wx.Point(0, 0),
              size=wx.Size(216, 32), style=0)
        self.button1.SetToolTipString('button1 tooltip')

    def __init__(self, parent,
            label="Command-line tools ...",
            contents=None):
        if contents == None:
            contents = (
                ("Here's looking at you, kid!", "xeyes"),
                ("separator", None),
                ("X11 clock", "xclock"),
                ("describe command to be done", "xclock")
            )
        self._init_ctrls(parent)
        self.registry = {}
	self.SetTitle(label)
        b = self.button1
        b.SetLabel(label)
        b.SetBackgroundColour("bisque")
        b.SetToolTipString("command: menuUSAXS.csh")
        b.Bind(wx.EVT_LEFT_DOWN, self.OnClick, b)
        b.Bind(wx.EVT_RIGHT_DOWN, self.OnClick, b)
        self.popupmenu = wx.Menu()
        for entry in contents:
            #pprint.pprint(entry)
	    text, command = entry
            if text == "separator":
                self.appendSeparator(self.popupmenu)
            else:
                self.appendMenuItem(
                    menu = self.popupmenu,
                    id = wx.NewId(),
                    text = text,
                    cmd = command,
                    handler = self.OnTheMenuGenericMenu)

    def appendSeparator(self, menu = None):
        '''add a separator line to the menu'''
        if menu != None:
            menu.AppendSeparator()

    def appendMenuItem(self, id, menu = None, text = 'text string',
            help='help string', handler = None, cmd = ''):
        '''add an item to the menu
            @param id: (int) to associate with handler
            @param menu: (menu object) usually self.theMenu
            @param text: (string) label for the menu item
            @param help: (string) describe actio to be performed
            @param cmd: (string) full command to be called
            @param handler: (method object) function that will receive event
        '''
        if menu != None:
            entry = {}
            entry['cmd'] = cmd
            entry['text'] = text
            entry['help'] = help
            entry['id'] = id
            self.registry[id] = entry
            menu.Append(help=help, id=id, kind=wx.ITEM_NORMAL, text=text)
            if handler != None:
                self.Bind(wx.EVT_MENU, handler, id=id)

    def OnTheMenuGenericMenu(self, event):
        id = event.GetId()
        entry = self.registry[id]
        cmd = os.path.normpath(entry['cmd'])
        #pprint.pprint(os.path.normpath(cmd))
        subprocess.Popen(cmd, shell = True)
        #print os.path.abspath(cmd)

    def OnClick(self, event):
        self.panel.PopupMenu(self.popupmenu, (0, 0))


if __name__ == '__main__':
    app = wx.PySimpleApp()
    menu_items = MENU_ITEMS
    frame = Frame1(None, label="9-ID-C USAXS menu", contents=menu_items)
    frame.Show()

    app.MainLoop()
