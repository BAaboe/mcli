from imapc import imapc
from smtpc import smtpc
import PIL.Image as Image
import cv2, io, os, base64, termcolor
import numpy as np
from tqdm import tqdm

class mcli:
    def __init__(self):
        self.imapc = imapc("mail.baaboe.fun", 993)
        self.smtpc = imapc("mail.baaboe.fun", 25)
        self.mail = ""
        self.password = ""

    def clear(self):
        os.system("clear")

    def download(self, attachment):
        imgData = ""
        if attachment["encoding"] == "base64":
            imgData = base64.decodebytes(attachment["data"].encode())

        path = f"{os.path.expanduser('~')}/Downloads/{attachment['fileName']}"
        i = 1
        while True:
            if os.path.exists(path):
                path = f"{os.path.expanduser('~')}/Downloads/({i}){attachment['fileName']}"
                i += 1
            else: break

        img = Image.open(io.BytesIO(imgData))
        img.save(path)

        return path

    def download_attachment(self, c):
        attachments_list = []
        for content in c:
            if content["type"].startswith("image"):
                attachments_list.append(content)
        self.clear()
        while True:
            for i, a in enumerate(attachments_list):
                print(f"{i+1}. {a['fileName']}")
            
            print(termcolor.colored("--------------------------------", "blue"))
            print("a. Download all")
            print("b. Go back")
            print("q. Quit")

            choice = input(termcolor.colored("> ", "green")).lower()

            if choice == "q":
                quit()
            elif choice == "b":
                return
            elif choice == "a":
                self.clear()
                for i in attachments_list:
                    path = self.download(i)
                    print(termcolor.colored(f"{attachment['fileName']} downloaded to {path}", "green"))
                    print(termcolor.colored("--------------------------------", "blue"))
            else:
                try:
                    if int(choice) > 0 and int(choice) < len(attachments_list)+1:
                        index = int(choice)
                        attachment = attachments_list[index-1]
                        path = self.download(attachment)
                        self.clear()
                        print(termcolor.colored(f"{attachment['fileName']} downloaded to {path}", "green"))
                        print(termcolor.colored("--------------------------------", "blue"))
                    else:
                        self.clear()
                except ValueError:
                    self.clear()
    
    def show_attachment(self, c):
        attachments_list = []
        for content in c:
            if content["type"].startswith("image"):
                attachments_list.append(content)
        self.clear()
        while True:
            for i, a in enumerate(attachments_list):
                print(f"{i+1}. {a['fileName']}")
            
            print(termcolor.colored("--------------------------------", "blue"))
            print("d. Download attachments")
            print("b. Go back")
            print("q. Quit")

            choice = input(termcolor.colored("> ", "green")).lower()

            if choice == "q":
                quit()
            elif choice == "b":
                return
            elif choice == "d":
                self.download_attachment(c)
                self.clear()
            else:
                try:
                    if int(choice) > 0 and int(choice) < len(attachments_list)+1:
                        index = int(choice)
                        attachment = attachments_list[index-1]

                        imgData = ""
                        if attachment["encoding"] == "base64":
                            imgData = base64.decodebytes(attachment["data"].encode())

                        nparr = np.fromstring(imgData, np.uint8)
                        image = cv2.imdecode(nparr, -1)

                        cv2.imshow(attachment["fileName"], image)
                        while True:
                            k = cv2.waitKey(10)
                            if k == 27:
                                cv2.destroyAllWindows()
                                break

                        self.clear()
                    else:
                        self.clear()
                except ValueError:
                    self.clear()

    def check_for_attachments(self, content):
        i = 0
        for c in content:
            if c["type"].startswith("image"):
                i += 1
            elif c["type"].startswith("video"):
                i += 1
        return i

    def see_mail(self, index):
        refresh = True
        attachments = False
        while True:
            self.clear()
            if refresh:
                mail = self.imapc.getMail(index)
                mailDict, content = self.imapc.parseHeader(mail)
                mailDict["content"] = self.imapc.parseContent(content, mail)
                refresh = False
            num_attachments = self.check_for_attachments(mailDict["content"])
            print(f"From: {mailDict['from']['name']}<{mailDict['from']['mail']}>" if mailDict['from']['name'] else {mailDict['from']['mail']})
            print(f"Subject: {mailDict['subject']}")
            print(f"Date: {mailDict['date']}")
            print(termcolor.colored(f"Number of attachments: {num_attachments}", "red")) if num_attachments > 0 else print(f"Number of attachments: None")
            print(termcolor.colored("--------------------------------", "blue"))
            for c in mailDict["content"]:
                if c["type"] == "text/plain":
                    if c["encoding"] == "base64":
                        print(base64.decodebytes(c["data"].encode()))
                    else:
                        print(c["data"])
            print(termcolor.colored("--------------------------------", "blue"))
            print("n. Next mail")
            if index > 0: print("p. Previous mail")
            if num_attachments > 0: print("s. Show attachments")
            print("b. Go back")
            print("q. quit")
            choice = input(termcolor.colored("> ", "green")).lower()
            if choice == "q":
                quit()
            elif choice == "n":
                refresh = True
                index += 1
            elif choice == "p" and index >= 1:
                refresh = True
                index -= 1
            elif choice == "b":
                return
            elif choice == "s" and num_attachments > 0:
                self.show_attachment(mailDict["content"])


    def checkInbox(self):
        seeing = 10
        refresh = True
        while True:
            self.clear()
            if refresh:
                headerList = []
                print(termcolor.colored("Fetching mails", "green"))
                for i in tqdm(range(10)):
                    mail = self.imapc.getMail(i+seeing-10)
                    mailDict, content = self.imapc.parseHeader(mail)
                    name = ""
                    if mailDict["from"]["name"]:
                        name = mailDict["from"]["name"]
                    else:
                        name = mailDict["from"]["mail"]
                    headerList.append({"out": f"Subject: {mailDict['subject']}, From: {name}'", "index": i+seeing-10})
                    refresh = False
            self.clear()
            for i in headerList:
                print(f"{i['index']+1}. {i['out']}")
            print(termcolor.colored("----------------------------------------------------------------", "blue"))
            print("n. Next page")
            if seeing != 10: print("p. Previous page")
            print("r. Refresh")
            print("b. Go back")
            print("q. Quit")
            print(f"showing {seeing-9}-{seeing} mails")

            choice = input(termcolor.colored("> ", "green")).lower()
            if choice == "q":
                quit()
            elif choice == "n":
                seeing += 10
                refresh = True
            elif choice == "p" and seeing != 10:
                seeing -= 10
                refresh = True
            elif choice == "r":
                refresh = True
                continue
            elif choice == "b":
                return
            else:
                try:
                    if int(choice) < seeing+1 and int(choice) > seeing-10-1:
                        self.see_mail(int(choice)-1)
                    else:
                        continue
                except ValueError:
                    continue

    def send_mail(self):
        pass


    def main(self):
        self.clear()
        while True:
            email = input("Enter your email address: ")
            password = input("Enter your password: ")
            if "@" not in email:
                self.clear()
                print("Not a valid email address")
            else:
                if self.imapc.login(email, password):
                    self.mail = email
                    self.password = password
                    break
                
        while True:
            self.clear()
            print("1. Check Inbox")
            print("2. Send Mail")
            print("q. Quit")
            choice = input(termcolor.colored("> ", "green")).lower()
            if choice == "1":
                self.checkInbox()
            elif choice == "2":
                self.send_mail()
            elif choice.lower() == "q":
                quit()
            else:
                pass


if __name__ == "__main__":
    cli = mcli()
    cli.main()