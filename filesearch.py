# Lab 5
# Rabia Mohiuddin
# CIS 41B
# Winter 2018

import os.path
import os
import re

import strsearch

class FileSearch:
    def __init__(self, startDir):
        ''' recursively walks down and caches subdirectories of start directory in dictionary '''
        
        #self.resultList = []
        #for (path, dirlist, filelist) in os.walk(startDir) :
            #for f in filelist :
                #self.resultList.append((path, f))      
        self.resultList = [(path, f) for (path, dirlist, filelist) in os.walk(startDir) for f in filelist]
        
    def searchName(self, regfilter, searchStr, Lresult, continueSearch):
        ''' accepts regular expression as filter and searches through result list for all file names matching filter.
        Returns the corresponding paths in a sorted list '''
        for (path, file) in sorted(self.resultList):
            if len(Lresult) <= 1000 and continueSearch.isSet():
                if regfilter.search(file) and (searchStr=='' or strsearch.strIsInFile(searchStr, os.path.join(path, file)) == True) :
                    Lresult.append(os.path.join(path, file))
            else:
                return
        # continueSearch.set()