from imapc import imapc
import os
import termcolor
import base64
import os
import PIL.Image as Image
import io

class mcli:
    def __init__(self):
        self.imapc = imapc("mail.baaboe.fun", 993)

    def clear(self):
        os.system("clear")

    def download(self, attachment):
        imgData = ""
        if attachment["encoding"] == "base64":
            imgData = base64.decodebytes(attachment["data"].encode())

        path = f"{os.path.expanduser('~')}/TestDownload/{attachment['fileName']}"
        i = 1
        while True:
            if os.path.exists(path):
                path = f"{os.path.expanduser('~')}/Download/({i}){attachment['fileName']}"
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
            print(f"From: {mailDict['from']['name']}<{mailDict['from']['mail']}>" if mailDict['from']['name'] else {mailDict['from']['mail']})
            print(f"Subject: {mailDict['subject']}")
            print(f"Date: {mailDict['date']}")
            print(termcolor.colored("--------------------------------", "blue"))
            for c in mailDict["content"]:
                if c["type"] == "text/plain":
                    if c["encoding"] == "base64":
                        print("encodign shit")
                    else:
                        print(c["data"])
                elif c["type"].startswith("image"):
                    print(termcolor.colored("----------------", "blue"))
                    print(termcolor.colored("There is a image attached", "red"))
                    attachments = True
            print(termcolor.colored("--------------------------------", "blue"))
            print("n. Next mail")
            if index > 0: print("p. Previous mail")
            if attachments: print("d. Download attachments")
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
            elif choice == "d" and attachments:
                self.download_attachment(mailDict["content"])


    def checkInbox(self):
        seeing = 10
        refresh = True
        while True:
            self.clear()
            if refresh:
                headerList = []
                for i in range(10):
                    mail = self.imapc.getMail(i+seeing-10)
                    mailDict, content = self.imapc.parseHeader(mail)
                    name = ""
                    if mailDict["from"]["name"]:
                        name = mailDict["from"]["name"]
                    else:
                        name = mailDict["from"]["mail"]
                    headerList.append({"out": f"Subject: {mailDict['subject']}, From: {name}'", "index": i+seeing-10})
                    refresh = False
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



    def main(self):
        self.clear()
        while True:
            if self.imapc.login():
                break
        while True:
            self.clear()
            print("1. Check Inbox")
            print("q. Quit")
            print("More coming soon")
            choice = input(termcolor.colored("> ", "green")).lower()
            if choice == "1":

                self.checkInbox()
            elif choice.lower() == "q":
                quit()
            else:
                pass


if __name__ == "__main__":
    cli = mcli()
    cli.main()