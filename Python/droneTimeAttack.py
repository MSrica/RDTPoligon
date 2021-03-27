#Libraries
##########################################################################################
from tkinter import *
from tkinter import messagebox
from tkinter import Scale, Tk, Frame, Label, Button
from tkinter.ttk import Notebook,Entry
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
from ttkthemes import ThemedTk


import serial
import serial.tools.list_ports
from serial import *
from serial import Serial

import sys
from threading import Thread 

from playsound import playsound

#Root window
##########################################################################################
root = ThemedTk(theme="equilux")
root.title("DTA")
root.geometry("1300x700")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.configure(background="#464646")
root.iconbitmap('../pictures/drone.ico')
root.iconphoto(True, tk.PhotoImage(file='../pictures/drone.png'))

def onClosing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        
root.protocol("WM_DELETE_WINDOW", onClosing)

#Fonts
##########################################################################################
buttonFont = font.Font(family='Helvetica', size='20')
textFont = font.Font(family='Helvetica', size='14')
highscoreButtonFont = font.Font(family='Helvetica', size='15')
titleFont = font.Font(family='Helvetica', size='30')
stopwatchFont = font.Font(family='Helvetica', size='32', weight='bold')
settingsTitleFont = font.Font(family='Helvetica', size='20')
tableHeadingFont = font.Font(family='Helvetica', size='17')
tableContentFont = font.Font(family='Helvetica', size='14')
toplevelButtonFont = font.Font(family='Helvetica', size='12')

#Main Frame
##########################################################################################
mainframe = ttk.Frame(root)
mainframe.grid(column=0, row=0, sticky = N)

statisticsHeadingBlankLabel = ttk.Label(mainframe, text=" ")
statisticsHeadingBlankLabel.grid(column=0, row=0, columnspan=2, sticky=N)
statisticsHeadingBlankLabel['font'] = titleFont

statisticsHeadingLabel = ttk.Label(mainframe, text="Drone Time Attack")
statisticsHeadingLabel.grid(column=0, row=1, columnspan=2, sticky=N)
statisticsHeadingLabel['font'] = titleFont

timeValue = ttk.Label(mainframe, text="00:00:00")
timeValue.grid(column=0, row=2, columnspan=2, sticky=N)
timeValue['font'] = stopwatchFont

#Serial
##########################################################################################
serialThreadBoolean = False
line = "0"
state = False
global currentGate 
currentGate = 0

def playPassed():
	playsound('../sounds/passed.mp3', False)

def playConnected():
	playsound('../sounds/connected.mp3', False)

def playFinished():
	playsound('../sounds/finished.mp3', False)

def serialInit():
	global serialPort
	serialPort = serial.Serial()
	serialPort.baudrate = 9600
	serialPort.port = COMPortCombobox.get()
	serialPort.open()
	main()

def serialClose():
	serialPort.close()

def main():
	if serialThreadBoolean:
		global line
		global currentColumn
		global state
		global isConnected
		global isStarted
		global timer
		global resetTimer
		global currentGate 
	#Input from receiver
		bLine = serialPort.readline()
		line = str(bLine)
		line = line[2:len(line)-5]

		if line != "":
	#Ready				
			if line == "connected":
				playConnected()
				isConnected = True
				startButton.configure(text="Ready")
				generateTable()
	#Liftoff		 	
			elif line == "0":
				playPassed()
				state = True
				isStarted = True
				startButton.configure(text="Running")
				timeStringToTimesArray()
	#Passing trough gate
			elif int(line) == currentGate+1:
				passedOrFinished = 0
				currentGate = currentGate+1
				timeStringToTimesArray()
				if int(line) == int(gateNumberComboBox.get()):
					timeStringToLaptimesArray()
					generateTable()
					currentGate = 0
					if currentColumn >= int(lapNumberComboBox.get()):
						passedOrFinished = 1

				if passedOrFinished == 0:
					playPassed()
				else:
					playFinished()


	#Last colummn and row generate best times
			if currentColumn >= int(lapNumberComboBox.get()):
				if int(line) == int(gateNumberComboBox.get()):
					bestCurrentLap()
					bestOverallLap()
					bestOverallTime()
					stopSerialThread()
					serialClose()
					startButton.configure(text="Finished")
					finalMin = int(times[int(line)-1][currentColumn-1][0:2])
					finalSec = int(times[int(line)-1][currentColumn-1][3:5])
					finalMsc = int(times[int(line)-1][currentColumn-1][6:8])
					timer = [finalMin, finalSec, finalMsc]
					resetTimer = False
					resetData()

		time.sleep(.01)
		main()
	else:
		print("not refreshing from arduino")

def serialPorts():
	return [p.device for p in serial.tools.list_ports.comports()]

def startSerialThread():
	global serialThreadBoolean
	serialThreadBoolean = True
	serialThread = Thread(target=serialInit, daemon=True)
	serialThread.start()

def stopSerialThread():
	global serialThreadBoolean
	serialThreadBoolean = False
			
"""
def lockComboboxes():
	COMPortCombobox.state(["disabled"])
	gateNumberComboBox.state(["disabled"])
	lapNumberComboBox.state(["disabled"])

def unlockComboboxes():
	global COMPortCombobox
	global gateNumberComboBox
	global lapNumberComboBox
	COMPortCombobox.state(["readonly"])
	gateNumberComboBox.state(["readonly"])
	lapNumberComboBox.state(["readonly"])
"""

#Stopwatch
##########################################################################################
timer = [0, 0, 0]
global pattern
pattern = '{0:02d}:{1:02d}.{2:02d}'
isConnected = False
isStarted = False

def resetData():
	global isConnected
	isConnected = False
	global isStarted
	isStarted = False
	global startSecondsBuffer
	startSecondsBuffer = 0
	global startMinutesBuffer
	startMinutesBuffer = 0
	global currentColumn
	currentColumn = 0
	global state
	state = False
	global laptimes
	laptimes = ["00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00"]
	global times
	times = [["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"]]
	global resetAchived
	if resetAchived:
		global timeAchived
		timeAchived = False
		global lapAchived
		lapAchived = False
	if resetTimer:
		global timer
		timer = [0, 0, 0]

def updateStopwatchTimeText():
	if state and isStarted:
		timer[2] += 1

		if (timer[2] >= 100):
		    timer[2] = 0
		    timer[1] += 1
		if (timer[1] >= 60):
		    timer[0] += 1
		    timer[1] = 0

	else:
		pass

	global timeString
	timeString = pattern.format(timer[0], timer[1], timer[2])
	timeString = timeString
	timeValue.configure(text=timeString)

	root.after(10, updateStopwatchTimeText)

def startStopwatch():
	global state
	if not state and not (COMPortCombobox.get() == 'None' or COMPortCombobox.get() == ''):
		state = True
		startSerialThread()	
		#lockComboboxes()	
	else:
		messagebox.showinfo(title="Error", message="COM port not chosen or\nstopwatch already started")

def resetStopwatch():
	global resetTimer
	resetTimer = True
	resetData()
	#unlockComboboxes()
	if serialThreadBoolean:
		stopSerialThread()
		serialClose()
	generateTable()
	startButton.configure(text="Start")

startButton = tk.Button(mainframe, text='Start', command=startStopwatch, bg="#808080", fg="#a6a6a6")
startButton.grid(row=3, column=0)
startButton['font'] = buttonFont

resetButton = tk.Button(mainframe, text='Reset', command=resetStopwatch, bg="#808080", fg="#a6a6a6")
resetButton.grid(row=3, column=1)
resetButton['font'] = buttonFont

stopwatchThread = Thread(target=updateStopwatchTimeText, daemon=True)

for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=3)

#Table Frame
##########################################################################################
global startSecondsBuffer
startSecondsBuffer = 0
global startMinutesBuffer
startMinutesBuffer = 0
global currentColumn
currentColumn = 0
global createTable
createTable = True
global times
times = [["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"]]
global laptimes
laptimes = ["00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00"]
global bestLap
bestLap = 9999999
global bestLapStr
bestLapStr = "--:--.--"
global bestTimeStr
bestTimeStr = ["--:--.--", "--:--.--", "--:--.--", "--:--.--", "--:--.--"]

global timeAchived
global lapAchive
global resetAchived
resetAchived = False

def tableFrameInit():
	global tableframe
	tableframe = ttk.Frame(root)
	tableframe.grid(column=0, row=0, pady=(270, 10), sticky = N)

def timeStringToTimesArray():
	global times
	times[int(line)-1][currentColumn] = timeString

def timeStringToLaptimesArray():
	global timeString
	global currentColumn
	global startSecondsBuffer
	global startMinutesBuffer

	minutes = int(timeString[0:2]) - startMinutesBuffer
	secondsAndMilisecond = str(float(timeString[3:8]) - startSecondsBuffer).split('.')
	if len(secondsAndMilisecond[1]) == 1:
		secondsAndMilisecond[1] += "0"
	elif len(secondsAndMilisecond[1]) > 2:
		secondsAndMilisecond[1] = secondsAndMilisecond[1][0:2]
	laptimes[currentColumn] = pattern.format(minutes, int(secondsAndMilisecond[0]), int(secondsAndMilisecond[1]))
	startSecondsBuffer = float(timeString[3:8])
	startMinutesBuffer = int(timeString[0:2])
	currentColumn += 1

def bestCurrentLap():
	global bestLap
	bestLapThisRace = 99999999
	bestLapIndex = 0

	for r in range(currentColumn):
		currentMinutes = int(laptimes[r][0:2]) * 60
		currentSeconds = float(laptimes[r][3:8])
		currentBestLap = currentMinutes + currentSeconds
		if currentBestLap <= bestLapThisRace:
			bestLapThisRace = currentBestLap
			bestLapIndex = r

	currentBestLapStr = laptimes[bestLapIndex]

def bestOverallLap():
	global bestLap
	global bestLapStr
	global lapAchived
	lapAchived = False

	for r in range(currentColumn):
		currentMinutes = int(laptimes[r][0:2]) * 60
		currentSeconds = float(laptimes[r][3:8])
		currentBestLap = currentMinutes + currentSeconds
		if currentBestLap <= bestLap:
			bestLap = currentBestLap
			bestLapStr = laptimes[r]
			lapAchived = True

def bestOverallTime():
	global bestTimeStr
	global lapNuberEnum
	lapNuberEnum = 0

	if int(lapNumberComboBox.get()) == 1:
		lapNuberEnum = 0
	elif int(lapNumberComboBox.get()) == 3:
		lapNuberEnum = 1
	elif int(lapNumberComboBox.get()) == 5:
		lapNuberEnum = 2
	elif int(lapNumberComboBox.get()) == 7:
		lapNuberEnum = 3
	elif int(lapNumberComboBox.get()) == 10:
		lapNuberEnum = 4

	global timeAchived
	timeAchived = False
	for x in range(8):
		if times[int(line)-1][currentColumn-1][x] != bestTimeStr[lapNuberEnum][x]:
			if times[int(line)-1][currentColumn-1][x] < bestTimeStr[lapNuberEnum][x] or bestTimeStr[lapNuberEnum][x] == "-":
				bestTimeStr[lapNuberEnum] = times[int(line)-1][currentColumn-1]
				timeAchived = True
				break

	if lapAchived or timeAchived:
		highscoreWindow()

def highscoreWindow():
	hscWindow = tk.Toplevel()
	hscWindow.configure(background="#464646")
	
	global timeUsername
	global lapUsername
	timeUsername = tk.StringVar(hscWindow)
	lapUsername = tk.StringVar(hscWindow)

	title = ttk.Label(hscWindow, text="New highscore!")
	title.grid(row=0, column=0, columnspan=2, padx=20, pady=4)
	title['font'] = textFont

	name = ttk.Label(hscWindow, text="Please write your name")
	name.grid(row=1, column=0, columnspan=2, padx=20, pady=4)
	name['font'] = textFont


	timeNameLabel = ttk.Label(hscWindow, text="Best Time!")
	timeNameLabel.grid(row=2, column=0)
	timeNameLabel['font'] = textFont
	timeNameEntry = ttk.Entry(hscWindow, textvariable=timeUsername)
	timeNameEntry.grid(row=2, column=1)
	if not timeAchived:
		timeNameLabel.grid_remove()
		timeNameEntry.grid_remove()

	lapNameLabel = ttk.Label(hscWindow, text="Best Lap!")
	lapNameLabel.grid(row=3, column=0)
	lapNameLabel['font'] = textFont
	lapNameEntry = ttk.Entry(hscWindow, textvariable=lapUsername)
	lapNameEntry.grid(row=3, column=1)
	if not lapAchived:
		lapNameLabel.grid_remove()
		lapNameEntry.grid_remove()

	global resetAchived
	resetAchived = False
	global submitButton
	submitButton = tk.Button(hscWindow, text="Submit", command=usernamesToHighscore, bg="#808080", fg="#a6a6a6")
	submitButton.grid(row=4, column=0, columnspan=2, padx=20, pady=4)
	submitButton['font'] = toplevelButtonFont

	closeButton = tk.Button(hscWindow, text="Close", command=hscWindow.destroy, bg="#808080", fg="#a6a6a6")
	closeButton.grid(row=5, column=0, columnspan=2, padx=20, pady=4)
	closeButton['font'] = toplevelButtonFont

def timeUsernameToHighscore():
	if submitButton['text'] == "Submit":
		global bestTimeStr
		bestTimeStr[lapNuberEnum] += " " + timeUsername.get()
		submitButton.configure(text="Sent")

def lapUsernameToHighscore():
	if submitButton['text'] == "Submit":
		global bestLapStr
		bestLapStr += " " + lapUsername.get()
		submitButton.configure(text="Sent")

def usernamesToHighscore():
	global lapAchived
	global timeAchived
	if lapAchived and timeAchived:
		timeUsernameToHighscore()
		submitButton.configure(text="Submit")
		lapUsernameToHighscore()
	elif lapAchived:
		lapUsernameToHighscore()
	elif timeAchived:
		timeUsernameToHighscore()
	lapAchived = False
	timeAchived = False
	global resetAchived
	resetAchived = True

def showHighscoreWindow():
	hsWindow = tk.Toplevel()
	hsWindow.configure(background="#464646")

	blLabel = ttk.Label(hsWindow, text="Best lap: ")
	blLabel.grid(row=0, column=0, padx=3, pady=3, sticky=E)
	blLabel['font'] = textFont

	blLabelStr = ttk.Label(hsWindow, text=bestLapStr)
	blLabelStr.grid(row=0, column=1, padx=3, pady=3, sticky=W)
	blLabelStr['font'] = textFont

	cnt = 1
	for x in range(5):
		if cnt == 1:	
			btLabel = ttk.Label(hsWindow, text="Best time for " + str(cnt) + " lap: ")
			btLabel.grid(row=x+1, column=0, padx=3, pady=3, sticky=E)
			btLabel['font'] = textFont

			btLabelStr = ttk.Label(hsWindow, text=bestTimeStr[x])
			btLabelStr.grid(row=x+1, column=1, padx=3, pady=3, sticky=W)
			btLabelStr['font'] = textFont
		else:
			btLabel = ttk.Label(hsWindow, text="Best time for " + str(cnt) + " laps: ")
			btLabel.grid(row=x+1, column=0, padx=3, pady=3, sticky=E)
			btLabel['font'] = textFont

			btLabelStr = ttk.Label(hsWindow, text=bestTimeStr[x])
			btLabelStr.grid(row=x+1, column=1, padx=3, pady=3, sticky=W)
			btLabelStr['font'] = textFont
		
		if cnt == 7:
			cnt += 3
		else:
			cnt += 2

	closeButton = tk.Button(hsWindow, text="Close", command=hsWindow.destroy, bg="#808080", fg="#a6a6a6")
	closeButton.grid(row=x+2, column=0, columnspan=2, pady=10)
	closeButton['font'] = toplevelButtonFont

def resetHighscores():
	global bestLap
	bestLap = 9999999
	global bestLapStr
	bestLapStr = "--:--.--"
	global bestTimeStr
	bestTimeStr = ["--:--.--", "--:--.--", "--:--.--", "--:--.--", "--:--.--"]

def generateTable():
	global tableframe
	global createTable

	if createTable:
		createTable = False
	else:
		tableframe.destroy()
	
	tableFrameInit()

	for k in range(1, int(gateNumberComboBox.get())+1):
		l = ttk.Label(tableframe, text="Gate "+ str(k), relief=RIDGE)
		l.grid(row=k, column=0, padx=3, pady=3,  sticky=NSEW)
		l['font'] = tableHeadingFont

	l = ttk.Label(tableframe, text="Lap time", relief=RIDGE)
	l.grid(row=int(gateNumberComboBox.get())+2, column=0, padx=3, pady=3,  sticky=NSEW)
	l['font'] = tableHeadingFont

	for i in range(int(gateNumberComboBox.get())+1):
		for j in range(int(lapNumberComboBox.get())):
			if i == 0:
				l = ttk.Label(tableframe, text="Lap "+ str(j+1), relief=RIDGE)
				l.grid(row=i, column=j+1, padx=3, pady=3,  sticky=NSEW)
				l['font'] = tableHeadingFont	
			else:
				l = ttk.Label(tableframe, text=times[i-1][j], relief=RIDGE)
				l.grid(row=i, column=j+1, padx=3, pady=3, sticky=NSEW)
				l['font'] = tableContentFont

	for z in range(int(lapNumberComboBox.get())):
		t = ttk.Label(tableframe, text=laptimes[z], relief=RIDGE)
		t.grid(row=int(gateNumberComboBox.get())+2, column=z+1, padx=3, pady=3,  sticky=NSEW)
		t['font'] = tableContentFont


#Settings Frame
##########################################################################################
global COMPortCombobox
global gateNumberComboBox
global lapNumberComboBox

def selectionClear(*args):
	root.focus()

def resettingHighscores():
    if messagebox.askokcancel("Reset", "Do you want to reset?"):
        resetHighscores()

settingsframe = ttk.Frame(root)
settingsframe.grid(column=1, row=0, sticky = E+N)

settingsHeadingBlankLabel = ttk.Label(settingsframe, text=" ")
settingsHeadingBlankLabel.grid(column=0, row=0, columnspan=2, sticky=N)
settingsHeadingBlankLabel['font'] = titleFont

settingsHeadingLabel = ttk.Label(settingsframe, text="Settings")
settingsHeadingLabel.grid(column=1, row=1, columnspan =2, pady=20, sticky=N)
settingsHeadingLabel['font'] = settingsTitleFont

COMPortLabel = ttk.Label(settingsframe, text="COM port")
COMPortLabel.grid(column=1, row=2, pady=20, sticky=N)
COMPortLabel['font'] = textFont

COMPortCombobox = ttk.Combobox(settingsframe, values=serialPorts(), width=10)
COMPortCombobox.grid(column=2, row=2, sticky=N)
COMPortCombobox.set('None')
COMPortCombobox.state(["readonly"])
COMPortCombobox.bind('<<ComboboxSelected>>', selectionClear)

settingsWidthBlankLabel = ttk.Label(settingsframe, text="     ")
settingsWidthBlankLabel.grid(column=3, row=2, sticky=N)
settingsWidthBlankLabel['font'] = titleFont

gateNumberLabel = ttk.Label(settingsframe, text="Number Of Gates")
gateNumberLabel.grid(column=1, row=3, pady=20, sticky=N)
gateNumberLabel['font'] = textFont

gateNumberVariable = StringVar()
gateNumberComboBox = ttk.Combobox(settingsframe, textvariable=gateNumberVariable, width=10)
gateNumberComboBox.grid(column=2, row=3, sticky=N)
gateNumberComboBox['values'] = ('2', '3', '4', '5', '6', '7', '8')
gateNumberComboBox.set('3')
gateNumberComboBox.state(["readonly"])
gateNumberComboBox.bind('<<ComboboxSelected>>', selectionClear)


lapNumberLabel = ttk.Label(settingsframe, text="Number Of Laps")
lapNumberLabel.grid(column=1, row=4, pady=20, sticky=N)
lapNumberLabel['font'] = textFont

lapNumberVariable = StringVar()
lapNumberComboBox = ttk.Combobox(settingsframe, textvariable=lapNumberVariable, width=10)
lapNumberComboBox.grid(column=2, row=4, sticky=N)
lapNumberComboBox['values'] = ('1', '3', '5', '7', '10')
lapNumberVariable.set('3')
lapNumberComboBox.state(["readonly"])
lapNumberComboBox.bind('<<ComboboxSelected>>', selectionClear)

settingsButtonsBlankLabel = ttk.Label(settingsframe, text="\n")
settingsButtonsBlankLabel.grid(column=0, row=6, columnspan=2, sticky=N)
settingsButtonsBlankLabel['font'] = titleFont

showHighscoresButton = tk.Button(settingsframe, text='Show\nHighscores', command=showHighscoreWindow, bg="#808080", fg="#a6a6a6")
showHighscoresButton.grid(row=7, column=1, columnspan=2)
showHighscoresButton['font'] = highscoreButtonFont

settingsButtonsBlankLabel = ttk.Label(settingsframe, text="")
settingsButtonsBlankLabel.grid(column=0, row=8, sticky=N)
settingsButtonsBlankLabel['font'] = textFont

resetHighscoresButton = tk.Button(settingsframe, text='Reset\nHighscores', command=resettingHighscores, bg="#808080", fg="#a6a6a6")
resetHighscoresButton.grid(row=9, column=1, columnspan=2)
resetHighscoresButton['font'] = highscoreButtonFont

for child in settingsframe.winfo_children(): 
    child.grid_configure(padx=5, pady=3)

stopwatchThread.start()
root.mainloop() 