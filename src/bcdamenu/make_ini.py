#!/usr/bin/env python

'''
Create a settings.ini file from a dictionary
'''

try:
    import configparser as iniParser
except:
    import ConfigParser as iniParser
import launcher


INI_FILE = 'settings.ini'
USAXS_CONFIG = {
    'title': '9-ID-C USAXS menu',
    'menu_items': {
        "9-ID-C USAXS controls (MEDM)": "start_epics",
        "separator": None,
        "USAXS Q calculator": "qToolUsaxs.csh",
        "sample and detector XY position tool": "wxmtxy.csh",
        "USAXS sample stage tool": "/home/beams/USAXS/Apps/wxmtusaxs/wxmtusaxs",
        "PyMca": "/APSshare/bin/pymca",
        "SAXS Imaging tool": "/APSshare/epd/rh6-x86/bin/python /home/beams/USAXS/Apps/USAXS_dataworker/Main.py",
        "Save Instr. status to Elog": "saveToElog.csh",
    }
}

config = iniParser.ConfigParser()
#config.read(INI_FILE)
config.set(launcher.DEFAULT_SECTION_LABEL, 'title', USAXS_CONFIG['title'])
config.set(launcher.DEFAULT_SECTION_LABEL, 'version', '2017.3.0')
config.set(launcher.DEFAULT_SECTION_LABEL, 'menus', ' '.join([launcher.MENU_ITEMS_SECTION_LABEL,]))
config.add_section(launcher.MENU_ITEMS_SECTION_LABEL)
for index, k in enumerate(USAXS_CONFIG[launcher.MENU_ITEMS_SECTION_LABEL].keys()):
    v = USAXS_CONFIG[launcher.MENU_ITEMS_SECTION_LABEL][k]
    config.set(launcher.MENU_ITEMS_SECTION_LABEL, 'label %d' % (index+1), k)
    config.set(launcher.MENU_ITEMS_SECTION_LABEL, 'command %d' % (index+1), v)
with open(INI_FILE, 'w') as configfile:    # save
    config.write(configfile)
