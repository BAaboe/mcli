#!/usr/bin/env python

import imaplib
from getpass import getpass
import base64
import os
import termcolor
import cv2
import numpy as np

class imapc:
    def __init__(self, host, port, silent=True):
        self.host = host
        self.port = port

        self.username = ""
        self.passw = ""

        self.name = None

        self.selectedMailbox = False
        self.silent = silent

    
    def Log(self, msg, logType="[DEBUG]",level=1):
        if self.silent:
            return
        levels = {"1": "green", "2": "red", "3": "yellow"}
        try:
            print(termcolor.colored(logType, levels[str(level)]), msg)
        except Exception as e:
            print(termcolor.colored("[ERRO]", "red"), str(e))

    def connect(self):
        self.server = imaplib.IMAP4_SSL(self.host, self.port)
        try:
            self.server.login(self.username, self.passw)
            return True
        except imaplib.IMAP4.error as e:
            if "Authentication failed" in str(e):
                print("Wrong Username or Password")
                return False
            else: 
                print(str(e))

    def login(self, mail=None, passw=None):
        if mail and passw:
            self.username = mail
            self.passw = passw
            if self.connect(): return True
            else: return False
        tries = 0
        while True:
            self.username = input("Username: ")
            self.passw = getpass("Password: ")
            if self.connect(): break
            if tries > 2:
                quit()
            else:
                tries += 1


    def logout(self):
        self.server.logout()

    def getMailFromMailBox(self, index):
        self.server.select("INBOX")
        mails = []
        typ, data = self.server.search(None, "ALL")
        typ, data = self.server.fetch(data[0].decode().split()[-1-index], "(RFC822)")
        self.Log("Mail fetched", "[COMPLETED]")

        mail = data[0][1].decode("utf-8")

        self.Log("Mail decoded", "[COMPLETED]")

        self.server.unselect()
        return mail

    def selectMailbox(self):
        trueMailboxes = self.getMailboxes()

        mailboxes = []

        for mailbox in trueMailboxes:
            mailboxes.append(mailbox.lower())

        i = 0
        for mailbox in mailboxes:
            print(f"{i+1} {mailbox[0].upper()+mailbox[1:].lower()}")
            i += 1
        
        while True:
            selected = input("Choose a mailbox: ")
            try:
                selected = int(selected)
                if selected <= len(mailboxes) and selected != 0:
                    self.selectedMailbox = mailboxes[selected-1]
                    return True
            except TypeError as e:
                if selected.lower() in mailboxes:
                    self.selectedMailbox = selected
                    return True
                elif selected.lower() == "q":
                    return False
            print("Select on of the available mailboxes")
    
    def deselectMailbox(self):
        self.selectedMailbox = False
        try:
            self.server.close()
        except imaplib.IMAP4.error as e:
            print("Nothing selected")
    
    def getMailTest(self, index=0):
        mail = self.getMailFromMailBox(index)

        #print(mail)
        fileW = open("mail", "w")
        fileW.write(mail)
        fileW.close()

        mail = mail.split("\n")
        #mailDict = {"from":"", "to": "", "cc": "", "subject": "", "content": "", "date": "", "messageid": ""}

        for mailPart in mail:
            index = mail.index(mailPart)
            mail[index] = mailPart.replace("\n", "").replace("\r", "")
        self.Log("Shits been replaced", "[COMPLETED]")
        
        mailDict, content = self.parseHeader(mail)



        contentDict = self.parseContent(content, mail)
        mailDict["content"] = contentDict

        

        return mailDict

    def getMail(self, index=0):
        mail = self.getMailFromMailBox(index)
        
        #fileW = open("mail", "w")
        #fileW.write(mail)
        #fileW.close()
        
        mail = mail.split("\n")
        for mailPart in mail:
            index = mail.index(mailPart)
            mail[index] = mailPart.replace("\n", "").replace("\r", "")
        self.Log("Shits been replaced", "[COMPLETED]")
    
        return mail

    def parseHeader(self, mail):
        self.Log("Parsing header", "[STARTED]")

        mailDict = {"from":"", "to": "", "cc": "", "subject": "", "content": "", "date": "", "messageid": ""}
        content = []

        i = 0
        for mailPart in mail:
            if mailPart.startswith("From: "):
                fr = mailPart.split(":")[1][1:]
                if "<" in fr:
                    frParts = fr.split("<")
                    frName = frParts[0][:-1]
                    frMail = frParts[1][:-1]
                    mailDict["from"] = {"name": frName, "mail": frMail}
                else:
                    mailDict["fr"] = {"name": False, "mail": fr}
            elif mailPart.startswith("To: "):
                to = mailPart.split(":")[1][1:]
                if "<" in to:
                    toParts = to.split("<")
                    toName = toParts[0]
                    toMail = toParts[1][:-1]
                    mailDict["to"] = {"name": toName, "mail": toMail}
                else:
                    mailDict["to"] = {"name": False, "mail": to}
            elif mailPart.startswith("Cc: "):
                cc = mailPart.split(":")[1][1:]
                if "<" in cc:
                    ccParts = cc.split("<")
                    ccName = ccParts[0][:-1]
                    ccMail = ccParts[1][:-1]
                    mailDict["cc"] = {"name": ccName, "mail": ccMail}
                else:
                    mailDict["cc"] = {"name": False, "mail": cc}
            elif mailPart.startswith("Subject: "):
                subject = mailPart.split(":");subject.pop(0)
                subject  = ":".join(subject)[1:]
                mailDict["subject"] = subject
            elif mailPart.startswith("Date: "):
                date = mailPart.split(":");date.pop(0)
                date = ":".join(date)[1:]
                mailDict["date"] = date
            elif mailPart.startswith("Message-ID: "):
                messageid = mailPart.split(":"); messageid.pop(0)
                messageid = ":".join(messageid)[1:]
                mailDict["messageid"] = messageid[1:-1]
            elif mailPart.startswith("Content"):
                content.append(mailPart)
            elif mailPart == (""):
                content += mail[i:]
                break
            i += 1

        self.Log("Parsing header", "[COMPLETED]")
        return mailDict, content

    def parseContent(self, content, mail):
        self.Log("Parsing content", "[STARTED]")
        contentDict = []
        
        mailJoined = "\n".join(mail)

        isMultiparted = False

        boundry = False

        if content[0].startswith("Content-Type: multipart/mixed;") or content[0].startswith("Content-Type: multipart/related;"):
            isMultiparted = True
            boundry = True
        elif content[0].startswith("Content-Type: multipart/alternative;"):
            isMultiparted = False
            boundry = True
        elif content[0].startswith("Content"):
            contentDict = False
            boundry = False
        else:
            contentDict.append({"type": "text/plain", "data": content, "encoding": None, "fileName": None})
            return  contentDict

        if isMultiparted:
            contentDict = self.parseMultiparted(content)
            print("should be here")
        else:
            contentDict = self.parseSingleparted(content, boundry)
            print("should not be here")

        self.Log("Parsing content", "[COMPLETED]")
        return contentDict

    def parseSingleparted(self, content, hasBoundry=True):
        contentDict = []
        boundry = "THERE IS NO BOUNDRY"
        if hasBoundry:
            boundry = content[0].split("=")[1][1:-1]
        contentSplit = []
        remaningContent = content
        while True:
            if "--"+boundry in remaningContent:
                index = remaningContent.index("--"+boundry)
                contentSplit.append(remaningContent[:index-1])
                remaningContent = remaningContent[index+1:]
            else:
                contentSplit.append(remaningContent)
                break
        for contentPart in contentSplit:
            contentType = ""
            contentFormat = ""
            contentEncoding = ""
            name = ""
            data = ""
            skip = False
            i = 0
            for line in contentPart:
                if line.startswith("Content-Type"):
                    contentType, contentFormat = line.split(":")[1][1:].split(";")[0].split("/")
                    if contentType == "multipart": 
                        skip = True
                        break
                    detail = line.split(":")[1][1:].split(";")[1][1:]
                    if detail.startswith("name"):
                        name = detail.split("=")[1][1:-1]
                elif line.startswith("Content-Transfer-Encoding"):
                    contentEncoding = line.split(":")[1][1:]
                elif line == "":
                    i +=1
                    break
                i += 1
            if not skip:
                data = "\n".join(contentPart[i:])
                data = data.replace(f"--{boundry}--", "")
                contentDict.append({"type": f"{contentType.strip()}/{contentFormat.strip()}", "data": data, "encoding": contentEncoding, "fileName": name})
        
        return contentDict
    def parseMultiparted(self, content):
        contentDict = []
        boundryMixed = content[0].split("=")[1][1:-1]

        contentSplit = []
        remaningContent = content
        while True:
            if "--"+boundryMixed in remaningContent:
                index = remaningContent.index("--"+boundryMixed)
                contentSplit.append(remaningContent[:index-1])
                remaningContent = remaningContent[index+1:]
            else:
                if "--"+boundryMixed+"--" in remaningContent:
                    index = remaningContent.index("--"+boundryMixed+"--")
                    contentSplit.append(remaningContent[:index])
                break

        for contentPart in contentSplit:
            if contentPart[0].startswith("Content-Type: multipart/alternative;"):
                contentAlternBound = contentPart[0].split("=")[1][1:-1]
                contentAlterSplit = []
                remaningContentAlter = contentPart
                while True:
                    if "--"+contentAlternBound in remaningContentAlter:
                        index = remaningContentAlter.index("--"+contentAlternBound)
                        contentAlterSplit.append(remaningContentAlter[:index-1])
                        remaningContentAlter = remaningContentAlter[index+1:]
                    else:
                        contentAlterSplit.append(remaningContentAlter)
                        break
                for contentPartPart in contentAlterSplit:
                    contentType = ""
                    contentFormat = ""
                    contentEncoding = ""
                    name = ""
                    data = ""
                    skip = False
                    i = 0
                    for line in contentPartPart:
                        if line.startswith("Content-Type"):
                            contentType, contentFormat = line.split(":")[1][1:].split(";")[0].split("/")
                            if contentType == "multipart": 
                                skip = True
                                break
                            detail = line.split(":")[1][1:].split(";")[1][1:]
                            if detail.startswith("name"):
                                name = detail.split("=")[1][1:-1]
                        elif line.startswith("Content-Transfer-Encoding"):
                            contentEncoding = line.split(":")[1][1:]
                        elif line == "":
                            i +=1
                            break
                        i += 1
                    if not skip:
                        data = "\n".join(contentPartPart[i:])
                        contentDict.append({"type": f"{contentType.strip()}/{contentFormat.strip()}", "data": data, "encoding": contentEncoding, "fileName": name})

        for contentPartPart in contentSplit:
            contentType = ""
            contentFormat = ""
            contentEncoding = ""
            name = ""
            data = ""
            skip = False
            i = 0
            for line in contentPartPart:
                if line.startswith("Content-Type"):
                    contentType, contentFormat = line.split(":")[1][1:].split(";")[0].split("/")
                    if contentType == "multipart": 
                        skip = True
                        break
                    detail = line.split(":")[1][1:].split(";")[1][1:]
                    if detail.startswith("name"):
                        name = detail.split("=")[1][1:-1]
                elif line.startswith("Content-Transfer-Encoding"):
                    contentEncoding = line.split(":")[1][1:]
                elif line == "":
                    i +=1
                    break
                i += 1
            if not skip:
                data = "\n".join(contentPartPart[i:])
                contentDict.append({"type": f"{contentType.strip()}/{contentFormat.strip()}", "data": data, "encoding": contentEncoding, "fileName": name})

        return contentDict
    def test(self):
        self.login()

        mail = self.getMail()
        
        for content in mail["content"]:
            if content["type"] == "image/png":
                imgData = base64.decodebytes(content["data"].encode())
                nparr = np.fromstring(imgData, np.uint8)
                image = cv2.imdecode(nparr, -1)

                cv2.imshow(content["fileName"], image)
                cv2.waitKey(0)
            if content["type"].startswith("text"):
                print(content["data"])
        
        self.logout()
                


if __name__ == "__main__":
    
    client = imapc("mail.baaboe.fun", 993)
    client.test()
