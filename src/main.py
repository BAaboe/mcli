from imapc import imapc
import os
import termcolor

class mcli:
    def __init__(self):
        self.imapc = imapc("mail.baaboe.fun", 993)
        self.imapc.login()

    def clear(self):
        os.system("clear")

    def seemail(self, index):
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
            print("b. Go back")
            print("n. Next mail")
            if index > 0: print("p. Previous mail")
            if attachments: print("d. Download attachments")
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
                break
            elif choice == "d" and attachments:
                pass


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
            else:
                try:
                    if int(choice) < seeing+1 and int(choice) > seeing-10-1:
                        self.seemail(int(choice)-1)
                    else:
                        continue
                except ValueError:
                    continue



    def main(self):
        self.clear()
        while True:
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