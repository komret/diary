#!/usr/bin/env python3
from collections import OrderedDict
import datetime
import os
import sys

from peewee import *


db = SqliteDatabase("diary.db")


class Entry(Model):
    content = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        database = db
        
        
def initialize():
    """Creates the database and table if they do not exist"""
    clear()
    db.connect()
    db.create_tables([Entry], safe=True)
    
    
def clear():
    """Clears screen"""
    os.system("cls" if os.name == "nt" else "clear")
    
    
def define_entries():
    """Selects all entries"""
    return Entry.select().order_by(Entry.timestamp.desc())
        
        
def menu_loop():
    """Shows the menu"""
    choice = None
    
    while True:
        print("There are {} entries in the database.\n".format(Entry.select().count()))
        for key, value in menu.items():
            print("{}) {}".format(key, value.__doc__))     
        choice = input("\nAction: ").lower().strip()
        clear()
        
        if choice in menu:
            menu[choice]()
    

def add_entry():
    """Add entry"""
    print("Type your entry. Press ctrl + d to finish.\n")
    data = sys.stdin.read().strip()
    
    if data:
        if input("\nSave entry? [Yn] ").lower().strip() != "n":
            clear()
            Entry.create(content=data)
            print("Saved succesfully.\n")
        else:
            clear()
            
        
def view_entries(search_query=None):
    """View entries"""
    entries = define_entries()
    
    if search_query:
        entries = search_query
           
    if entries.count() > 0:
        max_characters = 50
        i = 0
        for entry in entries:
            i += 1
            split_content = entry.content.split("\n")
            print("{} | {} | {}".format(
                    i,
                    entry.timestamp.strftime("%d/%m/%Y %H:%M"),
                    split_content[0][:max_characters]
                ), end = "")
            
            if len(entry.content) > max_characters or len(split_content) > 1:
                print("...")
            else:
                print("")
                
        try:
            select_entry = int(input("\nSelect entry [1–{}] ".format(i)))
            clear()
            if 1  <= select_entry <= i:
                view_entry(entries.offset(select_entry-1)[0])
        except ValueError:
            clear()
        
        
def search_entries():
    """Search entries"""
    entries = define_entries()
    search_query = input("What are you searching for? ")
    clear()
    
    if search_query:
        clear()
        results = entries.where(Entry.content.contains(search_query))
        print("Results found: {}\n".format(results.count()))
        
        if results.count() > 1:
            view_entries(results)
        elif results.count() == 1:
            view_entry(results[0])
        
        
def delete_entries():
    """Delete entries"""
    if input("Are you sure to delete all entries? [yN] ").lower().strip() == "y":
        for entry in define_entries():
            entry.delete_instance()
        clear()
        print("Deleted sucessfully.\n")
    else:
        clear()
            
        
def quit():
    """Quit"""
    exit()
    
    
def view_entry(num):
    """View selected entry"""
    entries = define_entries()
    timestamp = num.timestamp.strftime("%A %B %d, %Y %I:%M%p")
    print(timestamp)
    print("="*len(timestamp))
    print(num.content)
    print("="*len(timestamp)+"\n")
    if num.id != entries.select(fn.Max(Entry.id)).scalar():
        print("n) Newer entry")
    if num.id != entries.select(fn.Min(Entry.id)).scalar():
        print("o) Older entry")
    print("d) Delete entry")
    print("q) Main menu")
    
    next_action = input("\nAction: ").lower().strip()
    if next_action == "n" and num.id != entries.select(fn.Max(Entry.id)).scalar():
        clear()
        view_entry(Entry.select().order_by(Entry.timestamp).asc().where(Entry.id>num.id).get())
    elif next_action == "o" and num.id != entries.select(fn.Min(Entry.id)).scalar():
        clear()
        view_entry(entries.where(Entry.id<num.id).get())
    elif next_action == "d":
        clear()
        delete_entry(num)
    else:
        clear()
    
    
def delete_entry(entry):
    """Deletes selected entry"""
    if input("Are you sure to delete the entry? [yN] ").lower().strip() == "y":
        entry.delete_instance()
        clear()
        print("Deleted sucessfully.\n")
    else:
        clear()
    

menu = OrderedDict([
    ("a", add_entry),
    ("v", view_entries),
    ("s", search_entries),
    ("d", delete_entries),
    ("q", quit)
])
    
if __name__ == "__main__":
    initialize()
    menu_loop()
