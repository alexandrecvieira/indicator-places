#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Very simple app-indicator, shows gtk-bookmarks (aka places)
# Author: Alex Simenduev <shamil.si@gmail.com>
# Modificado para elementaryOS por: http://entornosgnulinux.com/
# Modificado para stalonetray no Openbox por: http://alexandrecvieira.droppages.com
#

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, Gio
from gi.repository import AppIndicator3 as AppIndicator

import os
import signal
import subprocess
from urllib.parse import unquote

APP_NAME = 'indicator-places'
APP_VERSION = '1.0'

class IndicatorPlaces:

    LEGACY_BOOKMARKS_PATH = os.getenv('HOME') + '/.gtk-bookmarks'
    BOOKMARKS_PATH = os.getenv('HOME') + '/.config/gtk-3.0/bookmarks'

    FM = Gio.app_info_get_default_for_type("inode/directory", True).get_executable()

    # print FM # for debug

    def __init__(self):
        self.ind = AppIndicator.Indicator.new("places", Gtk.STOCK_HOME, AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)        

        self.update_menu()

    def create_menu_item(self, label, icon_name):
        image = Gtk.Image()
        image.set_from_icon_name(icon_name, 24)

        item = Gtk.ImageMenuItem()
        item.set_label(label)
        item.set_image(image)
        item.set_always_show_image(True)
        return item
    
    # This method gets a themed icon name
    def get_bookmark_icon(self, path):
        if path.startswith("smb") or path.startswith("ssh") or path.startswith("ftp") or path.startswith("network"):
            icon_name = "folder-remote"    
        else:
            f = Gio.File.new_for_uri(path)
            try:   
                info = f.query_info(Gio.FILE_ATTRIBUTE_STANDARD_ICON, 0, None)
                icon = info.get_icon()
                icon_name = icon.get_names()[0] if icon.get_names()[0] != '(null)' else 'folder'
            except (NameError):
                icon_name = "folder"
        
        return icon_name

    # This methind creates a menu
    def update_menu(self, widget = None, data = None):
        try:
            bookmarks = open(self.LEGACY_BOOKMARKS_PATH).readlines()
        except IOError:
            bookmarks = open(self.BOOKMARKS_PATH).readlines()
        except IOError:
            bookmarks = []

        # Create menu
        menu = Gtk.Menu()
        self.ind.set_menu(menu)

        # Home folder menu item
        item = self.create_menu_item("Home Folder", "user-home") 
        item.connect("activate", self.on_bookmark_click, os.getenv('HOME'))
        menu.append(item)

        # Computer menu item
        item = self.create_menu_item("Computer", "computer" )
        item.connect("activate", self.on_bookmark_click, 'computer:')
        menu.append(item)

        # Computer menu item
        item = self.create_menu_item("Network", "network-workgroup")
        item.connect("activate", self.on_bookmark_click, 'network:')
        menu.append(item)

        # Trash
        trash = Gio.File.new_for_uri("trash:")
        trash_items = trash.query_info(Gio.FILE_ATTRIBUTE_TRASH_ITEM_COUNT,
                                       Gio.FileQueryInfoFlags.NONE, None).get_attribute_uint32(
                                           Gio.FILE_ATTRIBUTE_TRASH_ITEM_COUNT)
        item = self.create_menu_item("Trash", "user-trash")

        if trash_items > 0:
            image = Gtk.Image()
            image.set_from_icon_name("user-trash-full", 24)
            item.set_image(image)
            
        item.connect("activate", self.on_bookmark_click, 'trash:')
        menu.append(item)

        # Show separator
        item = Gtk.SeparatorMenuItem()
        menu.append(item)

        # Populate bookmarks menu items
        for bm in bookmarks:
            path, label = bm.strip().partition(' ')[::2]

            if not label:
                label = os.path.basename(os.path.normpath(path))

            label = unquote(label)
            item = self.create_menu_item(label, self.get_bookmark_icon(path))
            item.connect("activate", self.on_bookmark_click, path)

            # Append the item to menu
            menu.append(item)

        # Show the menu
        menu.show_all()

    # Open clicked bookmark
    def on_bookmark_click(self, widget, path):
        subprocess.Popen(self.FM + ' %s' % path, shell = True)
        
    def on_bookmarks_changed(self, filemonitor, file, other_file, event_type):
        if event_type == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            print ('Bookmarks changed, updating menu...')
            self.update_menu()

    def on_update_menu(self, filemonitor, file, other_file, event_type):
        if event_type == Gio.FileMonitorEvent.CHANGES_DONE_HINT or Gio.FileMonitorEvent.DELETED:
            print ('Trash changed, updating menu...')
            self.update_menu()

            
    def find_trash(self):
        home = os.getenv('HOME')
        for dirpath, dirnames, filenames in os.walk(home):
            for dirname in dirnames:
                if dirname.find("Trash") == 0 or dirname.find("trash") == 0:
                    dirname = os.path.join(dirpath, dirname) + "/files"
                    return dirname

if __name__ == "__main__":
    # Run the indicator
    i = IndicatorPlaces()
    
    # Monitor bookmarks changes 
    if os.path.isfile(i.LEGACY_BOOKMARKS_PATH):
        file = Gio.File.new_for_path(i.LEGACY_BOOKMARKS_PATH)
    else:
        file = Gio.File.new_for_path(i.BOOKMARKS_PATH)
           
    monitor = file.monitor_file(Gio.FileMonitorFlags.NONE, None)
    monitor.connect("changed", i.on_bookmarks_changed)

    # Monitor Trash changes
    trash_path = i.find_trash()
    trash = Gio.File.new_for_path(trash_path)
    t_monitor = trash.monitor_directory(Gio.FileMonitorFlags.NONE, None)
    t_monitor.connect("changed", i.on_update_menu)
    
    # Main gtk loop
    Gtk.main()
