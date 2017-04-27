
"""
parse the configuration file
"""

try:
    import configparser as iniParser
except:
    import ConfigParser as iniParser

TEST_FILE = "bcdamenu.ini"
MAIN_SECTION_LABEL = 'BcdaMenu'


class ConfigFileError(Exception): pass


class MenuBase(object):
    
    kind = None
    
    def __init__(self, parent=None, order=None):
        self.parent = parent
        self.order = order


class Menu(MenuBase):
    
    kind = 'menu'

    def __init__(self, parent=None, sectionName = None):
        MenuBase.__init__(self, parent=parent)
        self.sectionName = sectionName
        self.setTitle(sectionName)
        self.menuObject = None
        self.itemDict = {}
    
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
        self.title = title

    def setMenuObject(self, obj):
        self.menuObject = obj
    
    def readConfiguration(self, config):
        """
        read the menu's section from the config file
        
        :param obj config: instance of ConfigParser()
        """
        if self.title is None:
            msg = "no title given for menu"
            raise ConfigFileError(msg)
        if self.title not in config:
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
                    msg = 'Error in settings file, section [%s]: ' % menu_name + ini_file
                    msg += '\n  line reading: ' + k + ' = ' + v
                    raise KeyError(msg)
                key = 'key_%04d' % int(parts[0])
                label = k[k.find(' '):].strip()
                if label == 'submenu':
                    menu = Menu(self, v)
                    labels[key] = label
                    commands[key] = menu
                    menu.readConfiguration(config)
                    # print(str(menu))
                elif label == 'separator':
                    labels[key] = label
                    commands[key] = MenuSeparator(self)
                else:
                    labels[key] = label
                    if len(v) == 0:
                        v = None
                    item = MenuItem(self)
                    item.setCommand(v)
                    commands[key] = item
    
        # add the menu items in numerical order
        for k, label in sorted(labels.items()):
            self.itemDict[label] = commands[k]


class MenuItem(MenuBase):
    
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
        self.label = label

    def setCommand(self, command):
        self.command = command


class MenuSeparator(MenuBase):
    
    kind = 'separator'

    def __init__(self, parent=None):
        MenuBase.__init__(self, parent=parent)
    
    def __str__(self):
        msg = "MenuSeparator()"
        return msg


if __name__ == "__main__":
    config = iniParser.ConfigParser(allow_no_value=True)
    config.optionxform = str    # do not make labels lower case
    config.read(TEST_FILE)
    menu_list = []
    for k, v in config.items(MAIN_SECTION_LABEL):
        if k == "menus":
            for menu_name in v.split():
                menu = Menu(None, menu_name)
                menu_list.append(menu)
                menu.readConfiguration(config)
                # print(str(menu))
    pass
