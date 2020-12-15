# ----------------------------------------- #
#                                           #
#         Discord Data Extractor            #
#   To be used with `DiscordChatExporter`   #
#        Developed by HelpMeGame            #
#                                           #
# ----------------------------------------- #
import os
import json
from datetime import datetime as dt

fileContents = []
currentFile = ""
currentFileType = ""
startTime = dt.now()


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def GetFile():
    global currentFile, fileContents, currentFileType
    print(
        "Note: This tool currently only supports JSON and HTML.\nJSON is Recommend -- HTML has less features and is a bit buggy and slower.\n")
    currentFile = input("Location of the exported chat log:\n")

    if not os.path.exists(currentFile):
        clear()
        print("That file could not be found. Please try again.")
        GetFile()

    CalcTime()
    file = open(currentFile, "r", encoding="utf8")

    if currentFile.split(".")[-1].lower() == "json":
        currentFileType = "json"

        fileContents = json.loads(file.read())
        num_lines = sum(1 for line in open(currentFile))

    elif currentFile.split(".")[-1].lower() == "html":
        currentFileType = "html"
        data = file.read().split("\n")
        for line in data:
            if "span" in line:
                line.replace(" ", "").replace("\t", "")
                fileContents.append(line)
        num_lines = len(fileContents)
    else:
        file.close()
        clear()
        print("That is not a valid file type, please try a different file.")
        GetFile()
    file.close()

    print(f"The selected file has {num_lines} lines, and took {CalcTime(True)} microseconds to read.")
    clear()
    MainMenu()


def MainMenu():
    inpt = input(
        f'Current Selected Log: {currentFile}\nWhat would you like to do?\n1. Strip IDs\n2. Get Messages\n3. Get Pins\n4. New File\n')
    if inpt == "1":
        if currentFileType == "html":
            GetAuthorsHTML()
        elif currentFileType == "json":
            GetAuthorsJSON()
    elif inpt == "2":
        if currentFileType == "html":
            GetMessagesHTML(input("Please enter the User's ID:\n"))
        elif currentFileType == "json":
            GetMessagesJSON(input("Please enter the User's ID:\n"))
    elif inpt == "3":
        if currentFileType == "json":
            GetPins()
        else:
            clear()
            print("'Get Messages' only works with JSON files.")
            MainMenu()
    elif inpt == "4":
        clear()
        GetFile()
    else:
        clear()
        print("That is not available. Please try again:")
        MainMenu()


def GetAuthorsHTML():
    CalcTime()
    Authors = ""
    for line in fileContents:
        userID = GetUserIDHTML(line)
        if userID is not None and userID not in Authors:
            Authors += userID + "\n"

    WriteFile(Authors, "UserIDs.txt")
    clear()
    print(f"A file has been made with all the User IDs. The process took {CalcTime(True)} microseconds.")
    MainMenu()


def GetMessagesHTML(AuthorID: str):
    CalcTime()
    collect = False
    messages = ""
    for line in fileContents:
        if '<span class="chatlog__author-name" title=' in line:
            userID = GetUserIDHTML(line)
            if userID == AuthorID:
                collect = True
            else:
                collect = False
        elif collect:
            messages += GetMessageHTML(line) + "\n"
    WriteFile(messages, AuthorID + "_Messages.txt")
    clear()
    print(f"A file has been made with all the messages from {AuthorID}.  The process took {CalcTime(True)} microseconds.")
    MainMenu()


def GetUserIDHTML(dataLine: str):
    dataLine = dataLine.split(" ")
    for part in dataLine:
        if "data-user-id=" in part:
            part = part.replace('data-user-id=', "").replace('"', "")

            return part


def GetMessageHTML(dataLine: str):
    dataLine = dataLine.split("<")
    dataLine = CombineArray(dataLine, "\n").split(">")

    finalMsg = dataLine[1].replace("span", "").replace("/n\\", "").replace("\n", "").replace("/", "").replace(
        ' title="', "").replace('img class="emoji "', "").replace('src="https:cdn.discordapp.comemojis',
                                                                  "https://cdn.discordapp.com/emojis/").replace(
        'png"',
        "png").replace(
        'alt=', "").replace('href="', "").replace("https:tenor.com", "https://tenor.com/").replace('gif"', "gif")
    return finalMsg


def GetAuthorsJSON():
    CalcTime()
    Authors = ""
    messages = fileContents['messages']
    for message in messages:
        if message['author']['id'] not in Authors:
            Authors += message['author']['id'] + "\n"
    WriteFile(Authors, f"{fileContents['channel']['name']}-User-IDs.txt")
    clear()
    print(f"A file has been made with all the User IDs. The process took {CalcTime(True)} microseconds.")
    MainMenu()


def GetMessagesJSON(AuthorID: str):
    CalcTime()
    fromUser = []
    messages = fileContents['messages']
    for message in messages:
        if message['author']['id'] == AuthorID:
            fromUser.append(message['content'])

    WriteFile(CombineArray(fromUser, "\n"), f"{fileContents['channel']['name']}-{AuthorID}-Messages.txt")
    clear()
    print(f"A file has been made with all the messages from {AuthorID}. The process took {CalcTime(True)} microseconds.")
    MainMenu()


def GetPins():
    CalcTime()
    messages = fileContents['messages']
    pinnedMessages = []
    for message in messages:
        if message['isPinned']:
            pinnedMessages.append(
                f"{message['author']['name']}#{message['author']['discriminator']} ---> {message['content']}")
    WriteFile(CombineArray(pinnedMessages, "\n"), f"{fileContents['channel']['name']}-Pinned-Messages.txt")
    clear()
    print(f"Saved {len(pinnedMessages)} pinned messages. The process took {CalcTime(True)} microseconds.")
    MainMenu()


def WriteFile(toWrite, name):
    f = open(name, "w", encoding="utf8")
    f.write(toWrite)
    f.close()


def CombineArray(array, separator: str):
    combined = ""
    for item in array:
        combined += item + separator;
    return combined


def CalcTime(GetEnd=False):
    global startTime
    if not GetEnd:
        startTime = dt.now()
    else:
        return (startTime - dt.now()).microseconds


GetFile()
