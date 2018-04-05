# Rabia Mohiuddin
# Winter 2018

import os.path
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox as tkmb
import re
import platform
import threading

from filesearch import FileSearch

class FindWin(tk.Tk):
    def __init__(self) :
        ''' Constructor - sets up main window to search for files '''
        super().__init__()      # initialize Tk parent class    
        self.title("File Find")                 # add title to window   
        self.resizable(True, True)          
        #self.countSearches = 0
        self.continueSearch = threading.Event()       # create Event object
        
        Lcurrent = tk.Label(self, text="Current Folder: ").grid(row=0, column=0, sticky='e')       # label for current folder
        self.folder = tk.StringVar() 
        self.folder.set(os.path.expanduser('~'))
        current = tk.Label(self, textvariable=self.folder).grid(row=0, column=1, sticky='w')  # current folder        
            
        tk.Button(self, text = "Change Folder", command=lambda:self.__selectDir__()).grid(row=1, column=0, sticky='e')
        
        Lregex = tk.Label(self, text="Regex Filter:").grid(row=2, column=0, sticky='e')       # label for Regex filter
        self.reg = tk.StringVar()
        entReg = tk.Entry(self, textvariable=self.reg, highlightcolor='light blue')
        entReg.grid(row=2, column=1, sticky='we')
        
        Lsearch = tk.Label(self, text="Search String:").grid(row=3, column=0, sticky='e')       # label for Search filter
        self.search = tk.StringVar()
        entSearch = tk.Entry(self, textvariable=self.search, highlightcolor='light blue')
        entSearch.grid(row=3, column=1, sticky='we')        
        
        self.grid_columnconfigure(1, weight=1)        
        self.initial_focus = entReg
        self.initial_focus.focus_set()          # set the focus
        
        entReg.focus_set()
        entReg.bind("<Return>", self.__search__)        # bind() method connects a pressed key event
        entSearch.bind("<Return>", self.__search__)
        
        s = tk.Scrollbar(self)           # create scrollbar         
        self.lbox = tk.Listbox(self, yscrollcommand=s.set)     # listbox for results
        self.lbox.grid(row=4, column=0, sticky='nswe', padx=5, pady=5, columnspan=2)
        self.grid_rowconfigure(4, weight=2)
        # connect scrollbar to listbox
        s.config(command=self.lbox.yview)    # as you scroll it will show with the lbox
        s.grid(row=4, column=3, sticky='nsw', pady=5)  # put scroll bar in the grid        
        
        self.numFiles = tk.StringVar()        
        LnumFiles = tk.Label(self, textvariable=self.numFiles).grid(row=5, column=0, sticky='w')
        
        self.results = []
        self.continueSearch.clear()               # initialize the event flag to be clear 
        
        self.protocol("WM_DELETE_WINDOW", self._exit)
        self.update()
        self._fsearch = FileSearch(self.folder.get())
    
    def _exit(self):
        ''' When user clicks on 'X' in window '''
        if self.continueSearch.isSet(): self.__cancelSearch__()
        #self.after_cancel(self._searchThread)        # _searchThread is NOT an after thread, therefore cant use after_cancel
        self.destroy()
    
    def __selectDir__(self):
        '''callback function for the "Change Folder" button '''
        p = tk.filedialog.askdirectory(initialdir=".")
        if p:
            self.folder.set(p)      # if user selected a new folder, set it
            self.update()
            self._fsearch = FileSearch(self.folder.get())
            self.__search__()
    
    def __search__(self, *args):
        ''' callback for the "Regex filter" entry box '''
        try:
            regex = re.compile(self.reg.get(), re.I)    # case insensitive
        except re.error:
            tkmb.showerror("Invalid Regex", "Invalid Regular Expression. Please try again")
            return
        
        if self.continueSearch.isSet(): self.__cancelSearch__()    # if the search thread is currently searching, cancel the search
        #if self.countSearches > 0:
            #self.__cancelSearch__()
            #self.results.clear()
            #self.lbox.delete(0, tk.END)
        
        self.lbox.delete(0, tk.END)     # clear the listbox
        self.results.clear()        # clear results list
        self.continueSearch.set()
        
        #self.countSearches += 1  
        
        self._searchThread = threading.Thread(target= self._fsearch.searchName, args=(regex, self.search.get(), self.results, self.continueSearch), name='search')
        self._searchThread.start()
        
        #self._updateListBoxThread = None
        self._updateListBoxThread = self.after(100,self.__updateListBox__)     # update listbox 100 ms later
        
    def __updateListBox__(self):      
        if self._searchThread.isAlive():
            self._updateListBoxThread = self.after(100,self.__updateListBox__)     # update listbox 100 ms later
        else:
            self.continueSearch.clear()   # When search is complete, clear the search flag         
            if len(self.results) > 1000:
                self.numFiles.set("Found more than 1000 files")                        
                tkmb.showerror("Too many files", "Why are you looking for a needle in a haystack? Be more specific!")
                return 
            else:
                self.numFiles.set("Found " + str(len(self.results)) + " files")                        
                if len(self.results) == 0: tkmb.showerror("No files found", "No files found with given search parameters")
                
        self.lbox.insert(tk.END, *self.results[self.lbox.size():])      # Regardless of a current search thread, populate listbox
        '''
        if len(self.results) > 999:
            tkmb.showerror("Too many files", "Why are you looking for a needle in a haystack? Be more specific!")
            return 
        else:
            self.lbox.insert(tk.END, *self.results[self.lbox.size():])
            self.numFiles.set("Found " + str(len(self.results)) + " files")              
        
        if self._searchThread.isAlive() and not self.continueSearch.isSet():
            print("_pdateListBoxThread created")        
            self._updateListBoxThread = self.after(100, self.__updateListBox__())     
        '''
    
    def __cancelSearch__(self):
        ''' cancel the after() thread, tell the child thread to stop the search, wait for the child thread to end '''
        #if self._updateListBoxThread is not None and self._updateListBoxThread.isAlive():
        self.after_cancel(self._updateListBoxThread)
        self.continueSearch.clear()
        self._searchThread.join()
        

def main():
    win = FindWin()
    if platform.system() == 'Darwin': 
        tmpl = 'tell application "System Events" to set frontmost of every process whose unix id is %d to true'
        os.system("/usr/bin/osascript -e '%s'" % (tmpl % os.getpid()))
    win.mainloop()  
    

main()
