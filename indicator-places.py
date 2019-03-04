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

from gi.repository import Gtk, Gio, GLib
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

        self.volume_monitor = Gio.VolumeMonitor.get()
        self.volume_monitor.connect('drive-connected', self.update_menu)
        self.volume_monitor.connect('drive-changed', self.update_menu)
        self.volume_monitor.connect('drive-disconnected', self.update_menu)
        self.volume_monitor.connect('mount-added', self.update_menu)
        self.volume_monitor.connect('mount-changed', self.update_menu)
        self.volume_monitor.connect('mount-removed', self.update_menu)
        self.volume_monitor.connect('volume-added', self.update_menu)
        self.volume_monitor.connect('volume-changed', self.update_menu)
        self.volume_monitor.connect('volume-removed', self.update_menu)

        self.update_menu()

    def create_menu_item(self, label, icon_name):
        image = Gtk.Image()
        image.set_from_icon_name(icon_name, Gtk.IconSize.MENU)

        item = Gtk.ImageMenuItem()
        item.set_label(label)
        item.set_image(image)
        item.set_always_show_image(True)
        return item

    def _get_icon_name_from_gicon(self, gicon):
        assert type(gicon) == Gio.ThemedIcon
        name = "image-missing"
        theme = Gtk.IconTheme.get_default()
        for n in gicon.get_names():
            if theme.lookup_icon(n, Gtk.IconSize.MENU, 0):
                name = n
                break
        return n
    
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

        # Desktop folder menu item
        item = self.create_menu_item("Desktop", "desktop")
        path = str(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DESKTOP)).replace(' ', '\\ ')
        item.connect("activate", self.on_bookmark_click, path)
        menu.append(item)

        # Documents folder menu item
        item = self.create_menu_item("Documents", "folder-documents")
        item.connect("activate", self.on_bookmark_click, GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS))
        menu.append(item)

        # Downloads folder menu item
        item = self.create_menu_item("Downloads", "folder-download")
        item.connect("activate", self.on_bookmark_click, GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD))
        menu.append(item)

        # Pictures folder menu item
        item = self.create_menu_item("Pictures", "folder-pictures")
        item.connect("activate", self.on_bookmark_click, GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES))
        menu.append(item)

        # Music folder menu item
        item = self.create_menu_item("Music", "folder-music")
        item.connect("activate", self.on_bookmark_click, GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_MUSIC))
        menu.append(item)

        # Videos folder menu item
        item = self.create_menu_item("Videos", "folder-video")
        item.connect("activate", self.on_bookmark_click, GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS))
        menu.append(item)

        # Trash
        trash = Gio.File.new_for_uri("trash:")
        item = self.create_menu_item("Trash", "user-trash")
        item.connect("activate", self.on_bookmark_click, 'trash:')
        
        trash_items = trash.query_info(Gio.FILE_ATTRIBUTE_TRASH_ITEM_COUNT,
                                       Gio.FileQueryInfoFlags.NONE, None).get_attribute_uint32(
                                           Gio.FILE_ATTRIBUTE_TRASH_ITEM_COUNT)
        if trash_items > 0:
            image = Gtk.Image()
            image.set_from_icon_name("user-trash-full", Gtk.IconSize.MENU)
            item.set_image(image)
               
        menu.append(item)

        # Show separator
        item = Gtk.SeparatorMenuItem()
        menu.append(item)

        # Computer menu item
        item = self.create_menu_item("Computer", "computer" )
        item.connect("activate", self.on_bookmark_click, 'computer:')
        menu.append(item)

        # Computer menu item
        item = self.create_menu_item("Network", "network-workgroup")
        item.connect("activate", self.on_bookmark_click, 'network:')
        menu.append(item)

        # Populate bookmarks menu items
        counter = 0
        for bm in bookmarks:
            counter += 1
            if counter == 1:
                # Show separator
                item = Gtk.SeparatorMenuItem()
                menu.append(item)
            path, label = bm.strip().partition(' ')[::2]

            if not label:
                label = os.path.basename(os.path.normpath(path))

            label = unquote(label)
            item = self.create_menu_item(label, self.get_bookmark_icon(path))
            item.connect("activate", self.on_bookmark_click, path)

            # Append the item to menu
            menu.append(item)

        # Mounts
        connected_drives = self.volume_monitor.get_connected_drives()
        mounts = self.volume_monitor.get_mounts()
        counter = 0
        mounts_list = []
        for drive in connected_drives:
            for volume in drive.get_volumes():
                if volume.can_eject or volume.can_mount:
                    counter += 1
                    if counter == 1:
                        # Show separator
                        item = Gtk.SeparatorMenuItem()
                        menu.append(item)
                    vol_name = volume.get_name()
                    item = self.create_menu_item(vol_name, self._get_icon_name_from_gicon(volume.get_icon()))
                    menu.append(item)
                    # Open submenu
                    submenu = Gtk.Menu()
                    item.set_submenu(submenu)
                    open_menu =  self.create_menu_item("Open", "document-open")
                    open_menu.connect('activate', self.on_removible_media_click, volume)
                    submenu.append(open_menu)
                    mounts_list.append(vol_name)
                    
        for mount in mounts:
            if mount.can_unmount:
                if not (mount.get_name() in mounts_list):
                    counter += 1
                    if counter == 1:
                        # Show separator
                        item = Gtk.SeparatorMenuItem()
                        menu.append(item)
                    item = self.create_menu_item(mount.get_name(), self._get_icon_name_from_gicon(mount.get_icon()))
                    item.connect('activate', self.on_bookmark_click, mount.get_root().get_path())
                    menu.append(item)
                 
        # Show the menu
        menu.show_all()

    # Open clicked bookmark
    def on_bookmark_click(self, widget, path):
        subprocess.Popen(self.FM + ' %s' % path, shell = True)

    def on_removible_media_click_cb(self, task, result, volume):
        try:
            volume.mount_finish(result)
        except GLib.Error:
            None
        mount = volume.get_mount()
        path = mount.get_root().get_path()
        subprocess.Popen(self.FM + ' %s' % path, shell = True)
        self.update_menu()

    def on_removible_media_click(self, widget, volume):
        volume.mount(Gio.MountMountFlags.NONE, None, None, self.on_removible_media_click_cb, volume)
        
    def on_bookmarks_changed(self, filemonitor, file, other_file, event_type):
        if event_type == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            # print ('Bookmarks changed, updating menu...')
            self.update_menu()

    def on_trash_changed(self, filemonitor, file, other_file, event_type):
        if event_type == Gio.FileMonitorEvent.CHANGES_DONE_HINT or Gio.FileMonitorEvent.DELETED:
            # print ('Trash changed, updating menu...')
            self.update_menu()
            
    def empty_trash(self, widget):
        os.system("gio trash --empty")

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
    trash_folder = Gio.File.new_for_uri("trash:")
    t_monitor = trash_folder.monitor_directory(Gio.FileMonitorFlags.NONE, None)
    t_monitor.connect("changed", i.on_trash_changed)
    
    # Main gtk loop
    Gtk.main()
