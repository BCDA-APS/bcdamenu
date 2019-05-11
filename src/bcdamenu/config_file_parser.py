
# Copyright (c) 2009-2019, UChicago Argonne, LLC.
# See LICENSE.txt file for details.

"""
parse the configuration file

.. autosummary::

    ~readConfigFile
    ~ConfigFileError
    ~ConfigFileKeyError
    ~clearKnownMenuNames
    ~MenuBase
    ~Menu
    ~MenuItem
    ~MenuSeparator

"""

from collections import OrderedDict
try:
    import configparser as iniParser
except:
    import ConfigParser as iniParser

TEST_FILE = "bcdamenu.ini"
MAIN_SECTION_LABEL = 'BcdaMenu'
KNOWN_VERSIONS = ("2017.3.0", )

class ConfigFileError(Exception):
    """general exception from `config_file_parser`"""

class ConfigFileKeyError(ConfigFileError, KeyError):
    """exception with a key in the configuration file"""

known_menu_names = []


def clearKnownMenuNames():
    """keep a list of all known menus so a recursive configuration will be found"""
    global known_menu_names
    known_menu_names = []


class MenuBase(object):
    """base class for menu definitions"""
    
    kind = None
    
    def __init__(self, parent=None, order=None):
        self.parent = parent
        self.order = order


class Menu(MenuBase):
    """
    specifications of a menu or submenu
    
    .. autosummary::

        ~setTitle
        ~readConfiguration

    """
    
    kind = 'menu'

    def __init__(self, parent=None, sectionName = None):
        MenuBase.__init__(self, parent=parent)
        self.sectionName = sectionName
        self.setTitle(sectionName)
        self.itemDict = OrderedDict()
    
    def __str__(self):
        msg = "Menu("
        if self.parent is not None:
            msg += "parent=" + self.parent.title + ", "
        msg += "sectionName=" + str(self.sectionName)
        msg += ", title=" + str(self.title)
        msg += ", #items=" + str(len(self.itemDict))
        msg += ")"
        return msg

    def setTitle(self, title):
        """set the text of this menu's title"""
        self.title = title

    def readConfiguration(self, config):
        """
        read the menu's section from the config file
        
        :param obj config: instance of ConfigParser()
        """
        global known_menu_names
        
        if self.title is None:
            msg = "no title given for menu"
            raise ConfigFileError(msg)
        if not config.has_section(self.title):
            msg = self.title + " menu not found in config file"
            raise ConfigFileError(msg)
        
        labels = {}
        commands = {}

        for k, v in config.items(self.title):
            if k == 'title':
                self.setTitle(v)
            else:
                parts = k.split()
                if len(parts) < 2:
                    msg = 'Error in settings file, section [%s]: ' % menu_name
                    msg += '\n  line reading: ' + k + ' = ' + v
                    raise ConfigFileKeyError(msg)
                order_code = int(parts[0])
                key = 'key_%04d' % order_code
                label = k[k.find(' '):].strip()
                if label == 'submenu':
                    if v in known_menu_names:
                        raise ConfigFileKeyError(v + " used more than once")
                    menu = Menu(self, v)
                    menu.order = order_code
                    known_menu_names.append(v)
                    labels[key] = v.title
                    commands[key] = menu
                    menu.readConfiguration(config)
                    # print(str(menu))
                elif label == 'separator':
                    labels[key] = label
                    item = MenuSeparator(self)
                    commands[key] = item
                else:
                    labels[key] = label
                    if len(v) == 0:
                        v = None
                    item = MenuItem(self)
                    item.setCommand(v)
                    item.setLabel(label)
                    item.order = order_code
                    commands[key] = item
    
        # add the menu items in numerical order
        for k, label in sorted(labels.items()):
            self.itemDict[k] = commands[k]


class MenuItem(MenuBase):
    """
    specification of one item in a a menu (or submenu)
    
    .. autosummary::

        ~setCommand
        ~setLabel

    """
    
    kind = 'command'

    def __init__(self, parent=None, label=None):
        MenuBase.__init__(self, parent=parent)
        self.setLabel(label)
        self.command = None
    
    def __str__(self):
        msg = "MenuItem("
        msg += "label=" + str(self.label)
        msg += ", value=" + str(self.value)
        msg += ")"
        return msg

    def setLabel(self, label):
        """set the text to appear in the menu (called in constructor)"""
        self.label = label

    def setCommand(self, command):
        """set the text of the command to be executed when this menu item is selected"""
        self.command = command


class MenuSeparator(MenuBase):
    """
    specification of a separator line in a menu
    """
    
    kind = 'separator'

    def __init__(self, parent=None):
        MenuBase.__init__(self, parent=parent)
    
    def __str__(self):
        msg = "MenuSeparator()"
        return msg


def readConfigFile(file_name, ):
    title = MAIN_SECTION_LABEL
    version = 'unknown'

    clearKnownMenuNames()
    config = iniParser.ConfigParser(allow_no_value=True)
    config.optionxform = str    # do not make labels lower case
    config.read(file_name)
    menu_list = []
    for k, v in config.items(MAIN_SECTION_LABEL):
        if k == "title":
            title = v
        elif k == "version":
            if v not in KNOWN_VERSIONS:
                msg = "Unknown version: " + str(v)
                msg += "  expected one of: " + str(KNOWN_VERSIONS)
                raise ConfigFileError(msg)
            version = v
        elif k == "menus":
            for menu_name in v.split():
                if menu_name in known_menu_names:
                    msg = "submenu %s used more than once" % menu_name
                    raise ConfigFileKeyError(msg)
                menu = Menu(None, menu_name)
                known_menu_names.append(menu_name)
                menu_list.append(menu)
                menu.readConfiguration(config)
                # print(str(menu))
    
    return dict(menus=menu_list, title=title, version=version)


if __name__ == "__main__":
    cfg = readConfigFile(TEST_FILE)
    print(cfg['title'])
    print(cfg['version'])
    for m in cfg['menus']:
        print(m)
