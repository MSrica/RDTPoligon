from tkinter import *
import tkinter as tk
import tkinter.ttk as ttk

import serial
import serial.tools.list_ports
from serial import *
from serial import Serial

from threading import Thread 
import time

# --- functions --------------------------------------------------------------------
def serialPorts():
	return [p.device for p in serial.tools.list_ports.comports()]

def selectionClear(*args):
	root.focus()

def main():
	if serialOpened:
		bLine = serialPort.readline()
		line = str(bLine)
		line = line[2:len(line)-5]

		if line != "":
			text.insert("end", time.strftime("%H:%M:%S") + " -> " + line + "\n")

		text.see("end")
		root.after(10, main)
	

def serialInit(self):
	global serialOpened
	global serialPort
	if not serialOpened:
		serialOpened = True
		serialPort = serial.Serial()
		serialPort.baudrate = 9600
		serialPort.port = COMPortCombobox.get()
		serialPort.open()
		selectionClear()
		main()

def onClosing():
	global serialOpened
	if serialOpened:
		serialPort.close()
	serialOpened = False
	root.destroy()

# --- main -------------------------------------------------------------------------
global serialOpened
serialOpened = False
root = tk.Tk()
root.title("Serial Monitor")
root.geometry("200x700")
root.protocol("WM_DELETE_WINDOW", onClosing)

COMPortLabel = ttk.Label(root, text="COM port")
COMPortLabel.pack()

COMPortCombobox = ttk.Combobox(root, values=serialPorts(), width=10)
COMPortCombobox.pack()
COMPortCombobox.set('None')
COMPortCombobox.state(["readonly"])
COMPortCombobox.bind('<<ComboboxSelected>>', serialInit)

text = tk.Text(root, height=6, width=40)
text.pack(side="left", fill="both", expand=True)

vsb = tk.Scrollbar(root, orient="vertical", command=text.yview)
vsb.pack(side="right", fill="y")

text.configure(yscrollcommand=vsb.set)

root.mainloop()