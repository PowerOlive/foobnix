'''
Created on Mar 11, 2010

@author: ivan
'''
import os

from foobnix.util import LOG



from foobnix.directory.directory_model import DirectoryModel
from foobnix.model.entity import CommonBean
from foobnix.util.confguration import FConfiguration
from foobnix.util.file_utils import isDirectory, getExtenstion
from foobnix.util.mouse_utils import is_double_click
import gtk
from foobnix.directory.virtuallist_controller import VirturalLIstCntr
class DirectoryCntr():
    
    VIEW_ARTIST_ALBUM = 0
    VIEW_RADIO_STATION = 1
    VIEW_VIRTUAL_LISTS = 2
    
    
    def __init__(self, gxMain, playlistCntr, radioListCntr, virtualListCntr):
        self.playlistCntr = playlistCntr
        self.radioListCntr = radioListCntr
        self.virtualListCntr = virtualListCntr
        
        widget = gxMain.get_widget("direcotry_treeview")
        self.model = DirectoryModel(widget)
        widget.connect("button-press-event", self.onMouseClick)
        
        #widget.connect("drag-begin", self.all)
        #widget.connect("drag-data-get", self.all)
        #widget.connect("drag-data-received", self.all)
        #widget.connect("drag-drop", self.all)
        widget.connect("drag-end", self.on_drag_get)
        #widget.connect("drag-failed", self.all)
        #widget.connect("drag-leave", self.all)
        
        
        
        self.filter = gxMain.get_widget("filter-combobox-entry")
        self.filter.connect("key-release-event", self.onFiltering)
        
        self.view_list = gxMain.get_widget("view_list_combobox")
        cell = gtk.CellRendererText()
        self.view_list.pack_start(cell, True)
        self.view_list.add_attribute(cell, 'text', 0)  
        liststore = gtk.ListStore(str)
        self.view_list.set_model(liststore)
        self.view_list.append_text("by artist/album")
        self.view_list.append_text("by radio/stations")
        self.view_list.append_text("by play lists")
        self.view_list.set_active(0)
        
        self.view_list.connect("changed", self.onChangeView)
    
    def all(self, *args):
        for arg in args:
            print args
    
    
    def getModel(self):
        return self.model
    
    def on_drag_get(self, *args):    
        self.populate_playlist(append=True)

    def onChangeView(self, *args):
        active_index = self.view_list.get_active()  
        if active_index == self.VIEW_ARTIST_ALBUM:
            self.clear()
            self.addAll()
        elif active_index == self.VIEW_RADIO_STATION:
            self.clear()
            beans = self.radioListCntr.getState()[0]
            print beans
            for bean in beans:
                self.model.append(None, CommonBean(bean.name, bean.path, "normal", True, CommonBean.TYPE_MUSIC_URL))
        elif active_index == self.VIEW_VIRTUAL_LISTS:
            self.clear()  
            items = self.virtualListCntr.get_items()
            for item in items:
                self.model.append(None, CommonBean(item.name, item.path, "normal", True, CommonBean.TYPE_MUSIC_URL))
    
    def append_virtual(self, bean):
        self.virtualListCntr.append(bean)
        self.clear()
        items = self.virtualListCntr.get_items()
        parent = None
        for item in items:
            if bean.type == CommonBean.TYPE_FOLDER:
                parent = self.model.append(parent, CommonBean(item.name, item.path, "normal", True, CommonBean.TYPE_FOLDER))
            else:
                self.model.append(parent, CommonBean(item.name, item.path, "normal", True, CommonBean.TYPE_MUSIC_URL))
        
    
    def onFiltering(self, *args):   
        text = self.filter.get_children()[0].get_text()
        if text : 
            self.model.filterByName(text)
    
    def onMouseClick(self, w, e):
        if is_double_click(e): 
            self.populate_playlist()
    
    def populate_playlist(self, append=False):
        directoryBean = self.model.getSelectedBean()
        if directoryBean.type == CommonBean.TYPE_MUSIC_FILE:
            if append:                                                                            
                self.playlistCntr.appendPlaylist([directoryBean])
            else:
                self.playlistCntr.setPlaylist([directoryBean])
        elif directoryBean.type == CommonBean.TYPE_FOLDER:
            songs = self.getAllSongsByPath(directoryBean.path)
            if append:                                                                            
                self.playlistCntr.appendPlaylist(songs)
            else:
                self.playlistCntr.setPlaylist(songs)
        else:
            if append:                                       
                directoryBean.type=CommonBean.TYPE_MUSIC_URL                                     
                self.playlistCntr.appendPlaylist([directoryBean])
            else:
                directoryBean.type=CommonBean.TYPE_MUSIC_URL
                self.playlistCntr.setPlaylist([directoryBean])
            
    
    
    def getALLChildren(self, row, string):        
        for child in row.iterchildren():
            name = child[self.POS_NAME].lower()            
            if name.find(string) >= 0:
                print "FIND SUB :", name, string
                child[self.POS_VISIBLE] = True        
            else:               
                child[self.POS_VISIBLE] = False
        
                    
        
    def updateDirectoryByPath(self, path):
        print "Update path", path
        self.musicFolder = path
        self.model.clear()
        self.addAll()
    
    def clear(self):
        self.model.clear()
        
    def getAllSongsByPath(self, path):
        dir = os.path.abspath(path)
        list = os.listdir(dir)
        list = sorted(list)
        result = []            
        for file_name in list:
            if getExtenstion(file_name) not in FConfiguration().supportTypes:
                    continue
                        
            full_path = path + "/" + file_name
            
            if not isDirectory(full_path):                                
                bean = CommonBean(name=file_name,path=full_path,type=CommonBean.TYPE_MUSIC_FILE)
                result.append(bean)
                
        LOG.debug(result)
        return result 
    
    
    def addAll(self):
        level = None;
        #print "DIABLE ADD ALLLLLL"
        self.go_recursive(self.musicFolder, level) 
        
    def sortedDirsAndFiles(self, path, list):        
        files = []
        directories = []
        #First add dirs
        for file in list:            
            full_path = path + "/" + file
            if isDirectory(full_path):
                directories.append(file)
            else:    
                files.append(file)
                
        return sorted(directories) + sorted(files)
    
    def isDirectoryWithMusic(self, path):
        if isDirectory(path):
            dir = os.path.abspath(path)
            list = os.listdir(dir)
            for file in list:
                full_path = path + "/" + file
                if isDirectory(full_path):                              
                    if self.isDirectoryWithMusic(full_path):
                        return True                    
                else:
                    if getExtenstion(file) in FConfiguration().supportTypes:
                        return True
                    
        return False            
    
    def go_recursive(self, path, level):
        dir = os.path.abspath(path)
        list = os.listdir(dir)
        list = self.sortedDirsAndFiles(path, list)
                
        for file in list:
            
            full_path = path + "/" + file
            
            if not isDirectory(full_path) and getExtenstion(file) not in FConfiguration().supportTypes:
                continue
      
            
            if self.isDirectoryWithMusic(full_path):
                #LOG.debug("directory", file)                
                sub = self.model.append(level, CommonBean(name=file, path=full_path, font="bold", is_visible=True, type=CommonBean.TYPE_FOLDER))                    
                self.go_recursive(full_path, sub) 
            else:
                if not isDirectory(full_path):
                    self.model.append(level, CommonBean(name=file, path=full_path, font="normal", is_visible=True, type=CommonBean.TYPE_MUSIC_FILE))
                    #LOG.debug("file", file)                             

