######################################################################
# Author : Aaron Benkoczy
# Date : 2019.06.05.
######################################################################
# https://stackoverflow.com/questions/28132055/not-able-to-display-multiple-json-keys-in-tkinter-gui
import fnmatch
import os
import re
import xml.etree.ElementTree as ET
import sys
from Tkinter import *
import tkFont
import ttk

class App:

    logFile = ""

    def Killme():
        self.root.quit()
        self.root.destroy()

    # refresh menu
    def RefreshMenu(self):
        self._tree.delete(*self._tree.get_children())
        self.ReReadFile()

    # double click on a node
    def OnDoubleClick(self, event):
        selected_item = self._tree.focus()
        #value = self._tree.item(selected_item, "values") # "values when"
        value = self._tree.item(selected_item, "values")
        #print(value)
        if (len(value) > 0):

            string_line = str(value[1])
            lineArray = string_line.split(",")
            line = str(lineArray)
            line = line.replace("'", " ")
            line = line.strip()
            to_clipboard = line[line.find("/home"):line.find(": ")]
            #print(to_clipboard)
            self.root.clipboard_clear()
            self.root.clipboard_append(to_clipboard.decode('utf-8'))
            print ("===============================================================")
            print (to_clipboard.decode('utf-8'))
            print ("===============================================================")
    def __init__(self):

        self.root=Tk()
        self.root.title("Make Log Parser")
        self.root.geometry('10x10+0+0')
        self.dFont=tkFont.Font(family="Arial", size=14)

        # Menu elements
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)
        self.fileMenu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.fileMenu)
        self.fileMenu.add_command(label="Refresh", command=self.RefreshMenu)

        # init tree
        self._tree = ttk.Treeview(self.root)
        #_tree.LabelEdit = TRUE
        self._tree["columns"]=("one","two")
        self._tree.heading("#0", text="Tags")
        self._tree.heading("one", text="Problem")
        self._tree.heading("two", text="Place")
        self._tree.column("#0", minwidth=35, stretch=FALSE)        
        self._tree.column("one", minwidth=60, stretch=FALSE)
        self._tree.column("two", minwidth=45, stretch=FALSE)
        self._tree.grid(row=0, column=0, stic="nsew")

        # event listener double click
        self._tree.bind("<Double-1>", self.OnDoubleClick)
        #ttk.Style().configure('Treeview', rowheight=50)
        
        # scroll bar to root
        self.yscrollbar=Scrollbar(self.root, orient=VERTICAL, command=self._tree.yview)
        self.yscrollbar.pack(side=RIGHT, fill=Y)

        self.xscrollbar=Scrollbar(self.root, orient=HORIZONTAL, command=self._tree.xview)
        self.xscrollbar.pack(side=BOTTOM, fill=X)

        self._tree.configure(yscrollcommand=self.yscrollbar.set, xscrollcommand=self.xscrollbar.set)

        self.root.geometry('600x600+0+0')
        self._tree.pack(side=LEFT, fill=BOTH, expand = YES)

        ###############################
        # lets read the content: ######

        # file name
        global logFile
        logFile = sys.argv[1]

        if(os.path.exists(logFile)):
            self.ReReadFile()
        else:
            print(logFile + " is not a valid file")
            sys.exit(-1)
    # content reader
    def ReReadFile(self):

        global logFile
        allWarnings = 0

        # open the file
        with open(logFile, "r") as f:
            content = f.read()
            content = content.strip()


            # split the content by the pointer arrow ^
            contentList = content.split("^")
            tagTypes = set()

            # the first root tag what shows "All Warnings"
            tagMap = {"[root]": 0}
            tagMap["[root]"] = self._tree.insert("", 0, "[root]", text="[All Warnings: 0]")

            tagIndex = 1

            # iterate throu the splitted elements
            for i, line in enumerate(contentList):
                #line = line.strip()

                #get the tag, like: [-Wsomething]
                if re.search("\[\-W.*\]", line):
                    #tag = "["+line[line.find("[")+1:line.find("]")]+"]"
                    tag = re.search("\[\-W.*\]", line).group()

                    # insert a tag if it is not exsist
                    if(tag not in tagTypes):
                        tagTypes.add(tag)
                        tagMap[tag] = self._tree.insert("", tagIndex, tag, text=tag + " [1]")
                        ++tagIndex

                    # update the tags child counter
                    if(len(self._tree.get_children(tagMap[tag])) > 0):
                        self._tree.item(tag, text=tag + " ["+ str(len(self._tree.get_children(tagMap[tag]))+1) +"]")

                    # Tags - column
                    tagColumn = line[line.find(": warning: ")+1:line.find("[")]

                    # Place - column
                    placeColumn = line[line.find("/home"):line.find(": ")]
                    #placeColumn = line.search("/:]", line).group()

                    # Problem - column
                    lineArray = line.splitlines()
                    problemColumn = lineArray[len(lineArray)-2]
                    #problemColumn = line[line.find("]\n"):]
                    #insert an element under the tag
                    self._tree.insert(tagMap[tag], "end", i, 
                        text=tagColumn, values=(problemColumn, placeColumn)); 

                # if can't find a tag then add it to the "root" "All warnings"
                else:
                    # Tags - column
                    tagColumn = line[line.find(": warning: ")+1:line.find("[")]
                    # Place - column
                    placeColumn = line[line.find("/home"):line.find(": ")]
                    # Problem - column
                    lineArray = line.splitlines()

                    problemColumn = lineArray[len(lineArray)-2]
                    #problemColumn = line[line.find("]\n"):]

                    #insert an element under the tag
                    self._tree.insert(tagMap["[root]"], "end", i, 
                        text=tagColumn, values=(problemColumn, placeColumn));

                allWarnings = i;

        # count all of the warnings
        # get the elements under the all warnings to the second counter
        self._tree.item("[root]", text="[All Warnings: " + str(allWarnings) +"]"
            " ["+ str(len(self._tree.get_children(tagMap["[root]"]))+1) +"]")

        #self._tree.pack()
        self.root.mainloop();
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("usage: " + os.path.basename(sys.argv[0]) + " [logfile]")
        print("example: ")
        print("python " + os.path.basename(sys.argv[0]) + " \"Make.log\"")
        print("")
        print("Features:")
        print("- You can double click on a node to copy the path!")
        print("- There is a \"File > Refresh\" menu where you can reread the makelog file.")
        sys.exit(0)
    
    app = App()