#Libraries
##########################################################################################
from tkinter import *
from tkinter import Scale, Tk, Frame, Label, Button
import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import simpledialog

import threading

#Root window
##########################################################################################
root = ThemedTk(theme="equilux")
root.title("Zavrsni rad")
root.geometry("200x200")
root.configure(background="#888888")

def startThread():
    from main import mainLoop
    th = threading.Thread(target=mainLoop)
    th.start()

def trackNamePopup():
    newWin = Tk()
    newWin.withdraw()
    trackNameString = simpledialog.askstring("Track Name","Enter track name here:", parent = newWin)
    newWin.destroy()
    
    return trackNameString
  
def main():
    videoFeedButton = tk.Button(root, text ="Open camera window", command=startThread)
    checkButton = tk.Button(root, text ="Test", command=trackNamePopup)

    videoFeedButton.pack()
    checkButton.pack()

    root.mainloop()

if __name__ == '__main__':
    main()