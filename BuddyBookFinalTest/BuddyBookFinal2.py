import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import json
import uuid
import socket
import time
import datetime
import base64
import threading
import imghdr
import os
import copy

dataSheetHeader = {
    "user_list": ["ID", "name", "IP"],
    "friend_list": ["ID"],
    "article_list": ["latest_edit_time", "article_ID", "owner_ID", "content", "image_content", "like_list", "position_tag", "friend_tag"],
    "personal_data_list": ["ID", "name", "profile_picture", "profile_context", "background_picture", "latest_edit_time"]
}

GlobalServerPort = 9420
GlobalClientPort = 9487


def PictureNameToSendAbleData(fileName):
    if fileName:
        file = open(fileName, "rb")
        pictureRaw = file.read()
        profilePicType = str(imghdr.what("", pictureRaw))
        if profilePicType == "None":
            profilePicType = "jpg"
        profilePicBinary = str(base64.b64encode(pictureRaw), "utf8")
        return {"file_type": profilePicType, "binary": profilePicBinary}
    else:
        return {"file_type": "", "binary": ""}


def SendAbleDataToPictureName(fileDictionary):
    fileName = str(uuid.uuid4())
    fileType = fileDictionary["file_type"]
    fileFullName = fileName + "." + fileType
    file = open(fileFullName, "wb")
    file.write(base64.b64decode(fileDictionary["binary"]))
    file.close()

    return fileFullName


class systemOperator:
    DataBase = {}
    fileName = ""

    def __init__(self, dataBaseFileName):
        self.fileName = dataBaseFileName
        tmpFile = open(self.fileName, "r", encoding="utf-8")
        self.DataBase = json.load(tmpFile)
        tmpFile.close()

    def Save(self):
        tmpFile = open(self.fileName, "w", encoding="utf-8")
        tmpFile.write(json.dumps(self.DataBase, indent="\t", ensure_ascii=False))
        tmpFile.close()

    # ========================================= User =========================================

    # def getUserList(self):
    #     return self.DataBase["user_list"]
    #
    # def updateUser(self, user_ID, user_name, user_IP):
    #     for i in range(len(self.DataBase["user_list"])):
    #         if user_ID == self.DataBase["user_list"][i]["ID"]:
    #             self.DataBase["user_list"][i] = {"ID": user_ID,"name": user_name,"IP":user_IP}
    #             return
    #     tmp = {"ID": user_ID, "name": user_name, "IP": user_IP}
    #     self.DataBase["user_list"].append(tmp)

    # ========================================= Friend =========================================

    def getFriendName(self, targetID):
        if targetID in self.DataBase["friend_list"]:
            for personalData in self.DataBase["personal_data_list"]:
                if personalData["ID"] == targetID:
                    return personalData["name"]
        return "Null"

    def getFriendList(self):
        return self.DataBase["friend_list"]

    def addFriend(self, user_ID):
        tmp = {"ID": user_ID}
        self.DataBase["friend_list"].append(tmp)

    # ========================================= Article =========================================

    def getArticleList(self):
        return self.DataBase["article_list"]

    def getLegalArticle(self):
        legalArticle = []
        for articles in self.DataBase["article_list"]:
            for friendNames in self.DataBase["friend_list"]:
                if articles["owner_ID"] == friendNames["ID"]:
                    legalArticle.append(articles)

        return legalArticle

    def getNewerArticle(self, ArticleList):  # ArticleList attribute["ID","latest_edit_time"]
        result = self.DataBase["article_list"]
        for inputTest in ArticleList:
            for originData in result:
                if inputTest["article_ID"] == originData["article_ID"] and inputTest["latest_edit_time"] >= originData["latest_edit_time"]:
                    result.remove(originData)
        return result

    def getTargetArticle(self, targetID):
        for targetArticle in self.DataBase["article_list"]:
            if targetArticle["article_ID"] == targetID:
                return targetArticle
        return {}

    def updateArticle(self, latest_edit_time, article_ID, owner_ID, parent_ID, root_article_ID, content, image_content, like_list, position_tag, friend_tag, deletion):
        if deletion:
            tmp = {"latest_edit_time": latest_edit_time,
                   "article_ID": "",
                   "owner_ID": "",
                   "parent_ID": parent_ID,
                   "root_article_ID": root_article_ID,
                   "content": "",
                   "image_content": [],
                   "like_list": [],
                   "position_tag": [],
                   "friend_tag": [],
                   "deletion": True}
        else:
            tmp = {"latest_edit_time": latest_edit_time,
                   "article_ID": article_ID,
                   "owner_ID": owner_ID,
                   "parent_ID": parent_ID,
                   "root_article_ID": root_article_ID,
                   "content": content,
                   "image_content": image_content,
                   "like_list": like_list,
                   "position_tag": position_tag,
                   "friend_tag": friend_tag,
                   "deletion": deletion}
        for article in self.DataBase["article_list"]:
            if article["article_ID"] == article_ID and deletion:
                self.DataBase["article_list"][self.DataBase["article_list"].index(article)] = tmp
                return
            elif article["article_ID"] == article_ID and latest_edit_time > article["latest_edit_time"] and not deletion:
                for oldPicture in article["image_content"]:
                    os.remove(oldPicture["file_name"])
                ImageList = []
                for picture in tmp["image_content"]:
                    NewPictureName = SendAbleDataToPictureName(picture)
                    pictureData = {"file_name": NewPictureName}
                    ImageList.append(pictureData)
                tmp["image_content"] = ImageList
                self.DataBase["article_list"][self.DataBase["article_list"].index(article)] = tmp
                return
            elif article["article_ID"] == article_ID and latest_edit_time <= article["latest_edit_time"]:
                return
        ImageList = []
        for picture in tmp["image_content"]:
            NewPictureName = SendAbleDataToPictureName(picture)
            pictureData = {"file_name": NewPictureName}
            ImageList.append(pictureData)
        tmp["image_content"] = ImageList
        self.DataBase["article_list"].append(tmp)

    # ========================================= Personal Data =========================================

    def getPersonalDataList(self):
        return self.DataBase["personal_data_list"]

    def getNewerPersonalData(self, PersonalDataList):
        result = self.DataBase["personal_data_list"]
        for inputTest in PersonalDataList:
            for originData in result:
                if inputTest["ID"] == originData["ID"] and inputTest["latest_edit_time"] >= originData["latest_edit_time"]:
                    result.remove(originData)
        return result

    def updatePersonalData(self, user_ID, user_name, profile_picture, profile_context, background_picture, latest_edit_time, userIP):
        tmp = {
            "ID": user_ID,
            "user_name": user_name,
            "profile_picture": profile_picture,
            "profile_context": profile_context,
            "background_picture": background_picture,
            "latest_edit_time": latest_edit_time,
            "IP": userIP
        }
        for i in range(len(self.DataBase["personal_data_list"])):
            PersonalData = self.DataBase["personal_data_list"][i]
            if user_ID == PersonalData["ID"] and latest_edit_time > PersonalData["latest_edit_time"]:
                OldProfilePicture = self.DataBase["personal_data_list"][i]["profile_picture"]
                OldBackgroundPicture = self.DataBase["personal_data_list"][i]["background_picture"]
                os.remove(OldProfilePicture)
                os.remove(OldBackgroundPicture)
                NewProfilePictureName = SendAbleDataToPictureName(tmp["profile_picture"])
                NewBackgroundPictureName = SendAbleDataToPictureName(tmp["background_picture"])
                tmp["profile_picture"] = NewProfilePictureName
                tmp["background_picture"] = NewBackgroundPictureName
                self.DataBase["personal_data_list"][i] = tmp
                return
            elif user_ID == PersonalData["ID"] and latest_edit_time <= PersonalData["latest_edit_time"]:
                return
        NewProfilePictureName = SendAbleDataToPictureName(tmp["profile_picture"])
        NewBackgroundPictureName = SendAbleDataToPictureName(tmp["background_picture"])
        tmp["profile_picture"] = NewProfilePictureName
        tmp["background_picture"] = NewBackgroundPictureName
        self.DataBase["personal_data_list"].append(tmp)

    def getSelfInformation(self):
        return self.DataBase["personal_data_list"][0]

    # =========================================Add Friend Request =========================================

    def getFriendRequestList(self):
        return self.DataBase["add_friend_request"]

    def addFriendRequest(self, userID, userName, userProfilePicture):
        self.DataBase["add_friend_request"].append({"ID": userID, "user_name": userName, "user_profile_picture": userProfilePicture})

    def deleteFriendRequest(self, userID):
        for dataRow in self.DataBase["add_friend_request"]:
            if dataRow["ID"] == userID:
                self.DataBase["add_friend_request"].remove(dataRow)


class Communicator:
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, ServerIP, ServerPort):
        self.serverSocket.bind((ServerIP, int(ServerPort)))
        self.BuddyBookDB = systemOperator("LocalDataBase2.json")
        serverThread = threading.Thread(target=self.startServer)
        serverThread.start()

    def startServer(self):
        self.serverSocket.listen(10)
        while True:
            (connection, address) = self.serverSocket.accept()
            tmp = connection.recv(4096).decode()
            messageBuffer = ""
            while tmp:
                messageBuffer += tmp
                tmp = connection.recv(4096).decode()
            self.messageHandler(address, messageBuffer)
            connection.close()

    def TCPSend(self, IP, port, FullRequest):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if len(FullRequest) % 4096 == 0:
                FullRequest["extend"] = "extendMessage"
            clientSocket.connect((IP, port))
            clientSocket.send(FullRequest.encode("UTF8"))
            clientSocket.close()
            pass
        except:
            print("Connection Error")

    def messageHandler(self, address, messageBuffer):
        print(messageBuffer)
        Message = json.loads(messageBuffer)
        if Message["header"] == "add_friend_request":
            self.RecAddFriendRequest(address, Message)
        elif Message["header"] == "add_friend_reply":
            self.RecAddFriendReply(address, Message)
        elif Message["header"] == "update_personal_data":
            self.RecUpdatePersonalData(address, Message)
        elif Message["header"] == "post_article":
            self.RecPostArticle(address, Message)
        elif Message["header"] == "like_up":
            self.RecLikeUp(address, Message)
        elif Message["header"] == "sync1_request":
            self.RecSync1Request(address, Message)
        elif Message["header"] == "sync1_response":
            self.RecSync1Response(address, Message)
        elif Message["header"] == "sync2_request":
            self.RecSync2Request(address, Message)

    def RecAddFriendRequest(self, address, MessageDictionary):
        AddFriendRequestList = self.BuddyBookDB.getFriendRequestList()
        ToRecAddFriendRequestList = copy.deepcopy(AddFriendRequestList)
        RequestBody = MessageDictionary["body"]
        if len(ToRecAddFriendRequestList) > 0:
            for dataRow in ToRecAddFriendRequestList:
                if dataRow["ID"] == RequestBody["selfs_ID"]:
                    return
        fileName = SendAbleDataToPictureName(RequestBody["profile_picture"])
        self.BuddyBookDB.addFriendRequest(RequestBody["selfs_ID"], RequestBody["user_name"], fileName)

    def RecAddFriendReply(self, address, MessageDictionary):
        FriendList = self.BuddyBookDB.getFriendList()
        ToRecFriendList = copy.deepcopy(FriendList)
        for data in ToRecFriendList:
            if data["ID"] == MessageDictionary["body"]["selfs_ID"]:
                return
        if MessageDictionary["body"]["response"]:
            self.BuddyBookDB.addFriend(MessageDictionary["body"]["selfs_ID"])
            ToSendPersonalDataList = copy.deepcopy(self.BuddyBookDB.getPersonalDataList())
            ToSendArticleList = copy.deepcopy(self.BuddyBookDB.getArticleList())
            self.SendUpdatePersonalData(address[0], GlobalClientPort, ToSendPersonalDataList)
            self.SendPostArticle(address[0], GlobalClientPort, ToSendArticleList)

    def RecUpdatePersonalData(self, address, MessageDictionary):
        ToRecPersonalDataList = copy.deepcopy(MessageDictionary["body"]["personal_data_list"])
        for personalData in ToRecPersonalDataList:
            self.BuddyBookDB.updatePersonalData(
                personalData["ID"], personalData["user_name"], personalData["profile_picture"],
                personalData["profile_context"], personalData["background_picture"], personalData["latest_edit_time"], address[0])
        self.BuddyBookDB.Save()

    def RecPostArticle(self, address, MessageDictionary):
        ToRecUpdateArticleList = copy.deepcopy(MessageDictionary["body"]["article_list"])
        for article in ToRecUpdateArticleList:
            self.BuddyBookDB.updateArticle(
                article["latest_edit_time"], article["article_ID"], article["owner_ID"],
                article["parent_ID"], article["root_article_ID"], article["content"],
                article["image_content"], article["like_list"], article["position_tag"],
                article["friend_tag"], article["deletion"]
            )
        self.BuddyBookDB.Save()

    def RecLikeUp(self, address, MessageDictionary):
        tmp = self.BuddyBookDB.getTargetArticle(MessageDictionary["body"]["article_ID"])
        # tmp is an article unit
        if tmp != {}:
            if MessageDictionary["body"]["self_ID"] not in tmp["like_list"]:
                tmp["like_list"].append(MessageDictionary["body"]["self_ID"])
                tmp["latest_edit_time"] = MessageDictionary["body"]["latest_edit_time"]
        self.BuddyBookDB.Save()

    def RecSync1Request(self, address, MessageDictionary):
        othersDataList = MessageDictionary["body"]["data_list"]
        otherArticleList = []
        otherPersonalList = []
        for data in othersDataList:
            if data["current_ID_type"] == "article" or data["current_ID_type"] == "comment":
                otherArticleList.append(data)
            if data["current_ID_type"] == "personal_data":
                otherPersonalList.append(data)
        selfNewerArticleList = self.BuddyBookDB.getNewerArticle(otherArticleList)
        selfNewerPersonalList = self.BuddyBookDB.getNewerPersonalData(otherPersonalList)
        AllNewerData = []
        for data in selfNewerArticleList:
            if data["parent_ID"] == "":
                tmp = {"ID": data["article_ID"], "latest_edit_edit_time": data["latest_edit_time"], "current_ID_type": "article"}
                AllNewerData.append(tmp)
            elif data["parent_ID"] != "":
                tmp = {"ID": data["article_ID"], "latest_edit_edit_time": data["latest_edit_time"], "current_ID_type": "comment"}
                AllNewerData.append(tmp)
        for data in selfNewerPersonalList:
            tmp = {"ID": data["ID"], "latest_edit_edit_time": data["latest_edit_time"], "current_ID_type": "personal_data"}
            AllNewerData.append(tmp)

        self.SendSync1Response(address, GlobalClientPort, AllNewerData)

    def RecSync1Response(self, address, MessageDictionary):
        return

    def RecSync2Request(self, address, MessageDictionary):
        return

    def SendAddFriendRequest(self, IP, port):
        selfInformation = self.BuddyBookDB.getSelfInformation()
        ToSendSelfInformation = copy.deepcopy(selfInformation)
        profilePictureData = PictureNameToSendAbleData(ToSendSelfInformation["profile_picture"])
        Request = {"header": "add_friend_request", "body": {}}
        Request["body"]["selfs_ID"] = ToSendSelfInformation["ID"]
        Request["body"]["user_name"] = ToSendSelfInformation["user_name"]
        Request["body"]["profile_picture"] = {"file_type": profilePictureData["file_type"], "binary": profilePictureData["binary"]}
        Request["body"]["profile_context"] = ToSendSelfInformation["profile_context"]
        print("Last selfInformation : ", ToSendSelfInformation)
        self.TCPSend(IP, port, json.dumps(Request))
        print(json.dumps(Request, indent="\t", ensure_ascii=False))

        self.BuddyBookDB.Save()

    def SendAddFriendReply(self, IP, port, accept):
        selfInformation = self.BuddyBookDB.getSelfInformation()
        ToSendSelfInformation = copy.deepcopy(selfInformation)
        ToReplyUserData = {}
        PersonalDataList = self.BuddyBookDB.getPersonalDataList()
        ToSendPersonalDataList = copy.deepcopy(PersonalDataList)
        for PersonalData in ToSendPersonalDataList:
            if PersonalData["IP"] == IP:
                ToReplyUserData = PersonalData
        AddFriendRequestList = self.BuddyBookDB.getFriendRequestList()
        for addFriendRequest in AddFriendRequestList:
            if addFriendRequest["ID"] == ToReplyUserData["ID"]:
                self.BuddyBookDB.deleteFriendRequest(ToReplyUserData["ID"])
                Request = {"header": "add_friend_reply", "body": {}}
                Request["body"]["selfs_ID"] = ToSendSelfInformation["ID"]
                Request["body"]["response"] = accept
                self.TCPSend(IP, port, json.dumps(Request))
                print(json.dumps(Request, indent="\t", ensure_ascii=False))
        self.BuddyBookDB.Save()

    def SendUpdatePersonalData(self, IP, port, personalDataList):
        ToSendPersonalDataList = copy.deepcopy(personalDataList)
        for index in range(len(ToSendPersonalDataList)):
            personalData = ToSendPersonalDataList[index]
            profilePictureData = PictureNameToSendAbleData(personalData["profile_picture"])
            personalData["profile_picture"] = profilePictureData
            backgroundPictureData = PictureNameToSendAbleData(personalData["background_picture"])
            personalData["background_picture"] = backgroundPictureData
            ToSendPersonalDataList[index] = personalData
        Request = {"header": "update_personal_data", "body": {"personal_data_list": ToSendPersonalDataList}}
        self.TCPSend(IP, port, json.dumps(Request))
        print(json.dumps(Request, indent="\t", ensure_ascii=False))

        self.BuddyBookDB.Save()

    def SendPostArticle(self, IP, port, articleDataList):
        Request = {"header": "post_article", "body": {}}
        ModifiedArticleList = []
        ToSendArticleDataList = copy.deepcopy(articleDataList)
        for article in ToSendArticleDataList:
            image_content_list = []
            for picture in article["image_content"]:
                articlePictureData = PictureNameToSendAbleData(picture["file_name"])
                image_content_list.append(articlePictureData)
            article["image_content"] = image_content_list
            ModifiedArticleList.append(article)
        Request["body"]["article_list"] = ModifiedArticleList

        self.TCPSend(IP, port, json.dumps(Request))
        print(json.dumps(Request, indent="\t", ensure_ascii=False))

        self.BuddyBookDB.Save()

    def SendLikeUp(self, IP, port, article_ID, latest_edit_time):
        selfInformation = self.BuddyBookDB.getSelfInformation()
        ToSendSelfInformation = copy.deepcopy(selfInformation)
        Request = {"header": "like_up", "body": {}}
        Request["body"]["article_ID"] = article_ID
        Request["body"]["self_ID"] = ToSendSelfInformation["ID"]
        Request["body"]["latest_edit_time"] = latest_edit_time

        ArticleList = self.BuddyBookDB.getArticleList()
        ToSendArticleList = copy.deepcopy(ArticleList)
        for article in ToSendArticleList:
            if article["article_ID"] == article_ID:
                if selfInformation["ID"] not in article["like_list"]:
                    article["like_list"].append(selfInformation["ID"])
                    article["latest_edit_time"] = latest_edit_time

        self.TCPSend(IP, port, json.dumps(Request))
        print(json.dumps(Request, indent="\t", ensure_ascii=False))

        self.BuddyBookDB.Save()

    # OK
    def SendSync1Request(self, IP, port):
        ArticleList = self.BuddyBookDB.getArticleList()
        PersonalDataList = self.BuddyBookDB.getPersonalDataList()
        ToSendList = []
        for article in ArticleList:
            if article["parent_ID"] == "":
                ToSendList.append({"ID": article["article_ID"], "latest_edit_time": article["latest_edit_time"], "current_ID_type": "article"})
            else:
                ToSendList.append({"ID": article["article_ID"], "latest_edit_time": article["latest_edit_time"], "current_ID_type": "comment"})
        for personal_data in PersonalDataList:
            ToSendList.append({"ID": personal_data["ID"], "latest_edit_time": personal_data["latest_edit_time"], "current_ID_type": "personal_data"})
        Request = {"header": "sync1_request", "body": {}}
        Request["body"]["data_list"] = ToSendList
        print(json.dumps(Request, indent="\t", ensure_ascii=False))
        self.BuddyBookDB.Save()

    # OK
    def SendSync1Response(self, IP, port, selfNewerArticleList):
        Request = {"header": "sync2_Response", "body": {}}
        Request["body"]["data_list"] = selfNewerArticleList

        print(json.dumps(Request, indent="\t", ensure_ascii=False))

    def SendSync2Request(self, IP, port, NeedUpdateArticleList):
        Request = {"header": "sync2_Response", "body": {}}
        Request["body"]["data_list"] = NeedUpdateArticleList


class MyQt(QWidget):

    def __init__(self):
        super().__init__()

        self.communicator = Communicator("127.0.0.1", GlobalServerPort)

        self.setGeometry(300, 200, 800, 600)  # start X, start Y, WindowSizeX, WindowSizeY
        self.setWindowTitle("BuddyBook")
        self.pageStringList = ['個人資料', '好友邀請', '文章清單', '好友列表']

        self.MainLayout = QHBoxLayout()
        self.PageSelectLayout = QVBoxLayout()
        self.PageContextLayout = QVBoxLayout()
        self.FunctionLayout = QVBoxLayout()

        self.PageSelectListWidget = QListWidget()
        self.CreatePageListWidget()

        self.PageContextListWidget = QListWidget()

        self.CreateFunctionLayout()

        self.PageSelectLayout.addWidget(self.PageSelectListWidget)
        self.PageContextLayout.addWidget(self.PageContextListWidget)

        # Not set fixed as PersonalLayout

        self.MainLayout.addLayout(self.PageSelectLayout, 1)
        self.MainLayout.addLayout(self.PageContextLayout, 5)
        self.MainLayout.addLayout(self.FunctionLayout, 1)
        self.setLayout(self.MainLayout)
        self.show()

    class AskedFriend(QWidget):
        def __init__(self, parent, picturePath, userName, inUserID):
            super().__init__()
            self.UserProfilePicture = QLabel()
            self.UserProfilePicture.setMaximumSize(100, 100)
            self.UserProfilePicture.setPixmap(QPixmap(picturePath).scaled(100, 100, Qt.KeepAspectRatio))
            self.UserName = QLabel()
            self.UserName.setText(userName)
            self.AcceptButton = QPushButton("Accept")
            self.RejectButton = QPushButton("Reject")
            self.userID = inUserID

            self.AcceptButton.clicked.connect(lambda: parent.AcceptFriendOCL(self.userID))
            self.RejectButton.clicked.connect(lambda: parent.RejectFriendOCL(self.userID))

            self.ItemLayout = QHBoxLayout()
            self.ItemLayout.addWidget(self.UserProfilePicture)
            self.ItemLayout.addWidget(self.UserName)
            self.ItemLayout.addWidget(self.AcceptButton)
            self.ItemLayout.addWidget(self.RejectButton)
            self.setLayout(self.ItemLayout)

    class ArticleWidget(QWidget):
        def __init__(self, parent, InArticleID, InOwnerProfilePic, InOwnerName, InArticleContext, InPositionTag, InFriendTag, InImageContextList, InLikeList):
            super().__init__()
            self.articleID = InArticleID

            self.ownerProfilePic = QLabel()
            self.ownerProfilePic.setPixmap(QPixmap(InOwnerProfilePic).scaled(100, 100, Qt.KeepAspectRatio))
            self.ownerName = QLabel()
            self.ownerName.setText(InOwnerName)
            self.Row1 = QHBoxLayout()
            self.Row1.addWidget(self.ownerProfilePic)
            self.Row1.addWidget(self.ownerName)

            self.articleContext = QLabel()
            self.articleContext.setText(InArticleContext)
            self.Row2 = QHBoxLayout()
            self.Row2.addWidget(self.articleContext)

            self.positionTag = QLabel()
            self.positionTag.setText("At : " + InPositionTag)
            self.Row3 = QHBoxLayout()
            self.Row3.addWidget(self.positionTag)

            self.friendTag = QLabel()
            self.friendTag.setText("With : " + InFriendTag)
            self.Row4 = QHBoxLayout()
            self.Row4.addWidget(self.friendTag)

            self.ImageContextListWidget = QListWidget()
            for image in InImageContextList:
                LabelImage = QLabel()
                LabelImage.setPixmap(QPixmap(image).scaled(100, 100, Qt.KeepAspectRatio))
                container = QListWidgetItem()
                container.setSizeHint(QSize(100, 100))
                self.ImageContextListWidget.addItem(container)
                self.ImageContextListWidget.setItemWidget(container, LabelImage)
            self.Row5 = QHBoxLayout()
            self.Row5.addWidget(self.ImageContextListWidget)

            self.countLikeList = QLabel()
            self.countLikeList.setText("讚數：" + str(len(InLikeList)))
            self.likeButton = QPushButton("讚")
            self.likeButton.clicked.connect(lambda: parent.LikeUpOCL(self.articleID))
            self.checkLikeListButton = QPushButton("查看")
            self.checkLikeListButton.clicked.connect(lambda: parent.CheckLikeUpList(self.articleID))
            self.Row6 = QHBoxLayout()
            self.Row6.addWidget(self.countLikeList)
            self.Row6.addWidget(self.likeButton)
            self.Row6.addWidget(self.checkLikeListButton)

            self.CommentButton = QPushButton("留言")
            self.CommentButton.clicked.connect(lambda: parent.commentArticle(self.articleID))
            self.Row7 = QHBoxLayout()
            self.Row7.addWidget(self.CommentButton)

            ArticleWidgetALLLayout = QVBoxLayout()
            ArticleWidgetALLLayout.addLayout(self.Row1)
            ArticleWidgetALLLayout.addLayout(self.Row2)
            ArticleWidgetALLLayout.addLayout(self.Row3)
            ArticleWidgetALLLayout.addLayout(self.Row4)
            ArticleWidgetALLLayout.addLayout(self.Row5)
            ArticleWidgetALLLayout.addLayout(self.Row6)
            ArticleWidgetALLLayout.addLayout(self.Row7)

            self.setLayout(ArticleWidgetALLLayout)

    class AddArticleDialog(QDialog):
        def __init__(self, parent, Parent_ID, Root_ID):
            super().__init__()

            self.contentMessageLabel = QLabel()
            self.contentMessageLabel.setText("文章內容")
            self.contentMessage = QTextEdit()

            self.positionTagLabel = QLabel()
            self.positionTagLabel.setText("地點標記")
            self.positionTag = QTextEdit()

            self.friendTagLabel = QLabel()
            self.friendTagLabel.setText("朋友標記")
            self.friendTag = QTextEdit()
            self.AddImageButton = QPushButton("Add Image")
            self.PostButton = QPushButton("Post")

            # Be careful of FriendTag and PositionTag
            self.PostButton.clicked.connect(lambda: parent.PostArticleOCL(Parent_ID, Root_ID, self.contentMessage.toPlainText(), [], self.positionTag.toPlainText(), self.friendTag.toPlainText()))

            self.TotalLayout = QVBoxLayout()

            self.TotalLayout.addWidget(self.contentMessageLabel, 1)
            self.TotalLayout.addWidget(self.contentMessage, 20)
            self.TotalLayout.addWidget(self.positionTagLabel, 1)
            self.TotalLayout.addWidget(self.positionTag, 1)
            self.TotalLayout.addWidget(self.friendTagLabel, 1)
            self.TotalLayout.addWidget(self.friendTag, 1)
            self.TotalLayout.addWidget(self.AddImageButton, 1)
            self.TotalLayout.addWidget(self.PostButton, 1)

            self.setLayout(self.TotalLayout)

    class PersonalDialog(QDialog):
        def __init__(self):
            super().__init__()

    def CreatePageListWidget(self):
        for i in self.pageStringList:
            item = QListWidgetItem()
            item.setText(i)
            item.setSizeHint(QSize(0, 100))
            tmp = QFont()
            tmp.setPointSize(12)
            item.setFont(tmp)
            self.PageSelectListWidget.addItem(item)
        self.PageSelectListWidget.itemClicked.connect(self.PageSelectedListWidgetOnclickListener)

    def SetPersonalPage(self):
        PersonalData = self.communicator.BuddyBookDB.getSelfInformation()

        self.PageContextListWidget.clear()

        backGroundPicture = QListWidgetItem()
        backGroundPicture.setSizeHint(QSize(0, 200))
        backgroundPic = QLabel()
        backgroundPic.setPixmap(QPixmap(PersonalData["background_picture"]).scaled(200, 200, Qt.KeepAspectRatio))

        ProfilePicture = QListWidgetItem()
        ProfilePicture.setSizeHint(QSize(0, 100))
        ProfilePic = QLabel()
        ProfilePic.setPixmap(QPixmap(PersonalData["profile_picture"]).scaled(100, 100, Qt.KeepAspectRatio))

        UserName = QListWidgetItem()
        UserName.setText(PersonalData["user_name"])
        UserName.setSizeHint(QSize(0, 50))

        ProfileContext = QListWidgetItem()
        ProfileContext.setText(PersonalData["profile_context"])
        ProfileContext.setSizeHint(QSize(0, 100))

        self.PageContextListWidget.addItem(backGroundPicture)
        self.PageContextListWidget.setItemWidget(backGroundPicture, backgroundPic)
        self.PageContextListWidget.addItem(ProfilePicture)
        self.PageContextListWidget.setItemWidget(ProfilePicture, ProfilePic)
        self.PageContextListWidget.addItem(UserName)
        self.PageContextListWidget.addItem(ProfileContext)

    def SetAddFriendPage(self):
        friendRequestList = self.communicator.BuddyBookDB.getFriendRequestList()
        FriendRequestWidgetList = []
        self.PageContextListWidget.clear()

        for friendRequest in friendRequestList:
            ItemWidget = self.AskedFriend(self, friendRequest["user_profile_picture"], friendRequest["user_name"], friendRequest["ID"])
            FriendRequestWidgetList.append({"itemWidget": ItemWidget, "ID": friendRequest["ID"]})

        for Item in FriendRequestWidgetList:
            container = QListWidgetItem()
            container.setSizeHint(QSize(200, 100))
            self.PageContextListWidget.addItem(container)
            self.PageContextListWidget.setItemWidget(container, Item["itemWidget"])

    def SetArticleListPage(self):
        self.PageContextListWidget.clear()
        ArticleList = self.communicator.BuddyBookDB.getArticleList()

        for i in range(0,len(ArticleList)):
            for j in range(i,len(ArticleList)):
                if ArticleList[i]["latest_edit_time"] < ArticleList[j]["latest_edit_time"] and i != j:
                    tmp = ArticleList[i]
                    ArticleList[i] = ArticleList[j]
                    ArticleList[j] = tmp

        for article in ArticleList:
            if article["deletion"] == False:
                InArticleID = article["article_ID"]
                InOwnerProfilePic = ""
                InOwnerName = ""
                for PersonalData in self.communicator.BuddyBookDB.getPersonalDataList():
                    if PersonalData["ID"] == article["owner_ID"]:
                        InOwnerName = PersonalData["user_name"]
                        InOwnerProfilePic = PersonalData["profile_picture"]
                InArticleContext = article["content"]
                InPositionTag = ""
                for position in article["position_tag"]:
                    InPositionTag = InPositionTag + position + ","
                InFriendTag = ""
                for friendTagID in article["friend_tag"]:
                    for PersonalData in self.communicator.BuddyBookDB.getPersonalDataList():
                        if friendTagID == PersonalData["ID"]:
                            InFriendTag = InFriendTag + PersonalData["user_name"] + ","
                InImageContextList = []
                for Image in article["image_content"]:
                    InImageContextList.append(Image["file_name"])
                InLikeListName = []
                InLikeListName = self.getLikeUpListName(article["like_list"])

                articleWidget = self.ArticleWidget(self, InArticleID, InOwnerProfilePic, InOwnerName, InArticleContext, InPositionTag, InFriendTag, InImageContextList, InLikeListName)

                container = QListWidgetItem()
                container.setSizeHint(QSize(500, 500))

                self.PageContextListWidget.addItem(container)
                self.PageContextListWidget.setItemWidget(container, articleWidget)

    def SetFriendListPage(self):
        self.PageContextListWidget.clear()
        FriendList = copy.deepcopy(self.communicator.BuddyBookDB.getFriendList())
        PersonalDatList = copy.deepcopy(self.communicator.BuddyBookDB.getPersonalDataList())
        for Friend in FriendList:
            tmp = QListWidgetItem()
            tmp.setSizeHint(QSize(300, 100))
            tmpFont = QFont()
            tmpFont.setPointSize(20)
            tmp.setFont(tmpFont)
            for PersonalData in PersonalDatList:
                if PersonalData.get("ID") == Friend.get("ID"):
                    tmp.setText(PersonalData.get("user_name"))
            self.PageContextListWidget.addItem(tmp)

        self.PageContextListWidget.clicked.connect(lambda: self.FriendListPageOCL(self.PageContextListWidget.currentRow()))

    def PageSelectedListWidgetOnclickListener(self, item):
        if item.text() == self.pageStringList[0]:
            self.SetPersonalPage()
        elif item.text() == self.pageStringList[1]:
            self.SetAddFriendPage()
        elif item.text() == self.pageStringList[2]:
            self.SetArticleListPage()
        elif item.text() == self.pageStringList[3]:
            self.SetFriendListPage()
        self.PageContextLayout.update()
        self.MainLayout.update()

    def CreateFunctionLayout(self):
        self.AddFriendButton = QPushButton("Add Friend")
        self.PostArticleButton = QPushButton("Post Article")
        self.ModifyProfileButton = QPushButton("Modify Profile")

        self.AddFriendButton.clicked.connect(self.AddFriendDialogOCL)
        self.PostArticleButton.clicked.connect(self.PostArticleDialogOCL)
        self.ModifyProfileButton.clicked.connect(self.ModifyProfileOCL)

        self.FunctionLayout.addWidget(self.AddFriendButton)
        self.FunctionLayout.addWidget(self.PostArticleButton)
        self.FunctionLayout.addWidget(self.ModifyProfileButton)

    def AddFriendDialogOCL(self):
        AddFriendDialog = QDialog()
        AddFriendDialogLayout = QVBoxLayout()
        label1 = QLabel("IP")
        IPEditText = QLineEdit()
        SendAddFriendButton = QPushButton("Send")
        SendAddFriendButton.clicked.connect(lambda: self.SendAddFriendOCL(IPEditText.text()))

        AddFriendDialogLayout.addWidget(label1)
        AddFriendDialogLayout.addWidget(IPEditText)
        AddFriendDialogLayout.addWidget(SendAddFriendButton)

        AddFriendDialog.setLayout(AddFriendDialogLayout)
        AddFriendDialog.exec()

    def PostArticleDialogOCL(self):
        Dialog = self.AddArticleDialog(self, "", "")
        Dialog.exec()

    def ModifyProfileOCL(self):
        Dialog = QDialog()
        DialogLayout = QVBoxLayout()

        Label1 = QLabel("個人名稱")
        UserName = QLineEdit()

        Label2 = QLabel("個人簡介")
        UserProfile = QTextEdit()

        UpdateButton = QPushButton("Update")
        UpdateButton.clicked.connect(lambda: self.UpdateProfileOCL(UserName.text(),UserProfile.toPlainText()))

        DialogLayout.addWidget(Label1)
        DialogLayout.addWidget(UserName)
        DialogLayout.addWidget(Label2)
        DialogLayout.addWidget(UserProfile)
        DialogLayout.addWidget(UpdateButton)

        Dialog.setLayout(DialogLayout)
        Dialog.exec()

    def UpdateProfileOCL(self,UpdateName,UpdateProfile):
        timeTag = str(datetime.datetime.now().strftime("%Y.%m.%d.%H.%M.%S"))

        OriginSelfData = self.communicator.BuddyBookDB.getSelfInformation()
        OriginSelfData["user_name"] = UpdateName
        OriginSelfData["profile_context"] = UpdateProfile
        OriginSelfData["latest_edit_time"] = timeTag

        PersonalDataList = self.communicator.BuddyBookDB.getPersonalDataList()
        for PersonalData in PersonalDataList:
            self.communicator.SendUpdatePersonalData(PersonalData["IP"],GlobalClientPort,[OriginSelfData])

        self.communicator.BuddyBookDB.Save()


    def SendAddFriendOCL(self, IP):
        self.communicator.SendAddFriendRequest(IP, GlobalClientPort)

        personalDataList = copy.deepcopy(self.communicator.BuddyBookDB.getPersonalDataList())

        self.communicator.SendUpdatePersonalData(IP, GlobalClientPort, personalDataList)

    def AcceptFriendOCL(self, ID):
        friendRequestList = self.communicator.BuddyBookDB.getFriendRequestList()
        FriendList = self.communicator.BuddyBookDB.getFriendList()
        FriendExistFlag = False
        for i in range(len(friendRequestList)):
            if friendRequestList[i]["ID"] == ID:
                personalDataList = self.communicator.BuddyBookDB.getPersonalDataList()
                ToSendPersonalDataList = copy.deepcopy(personalDataList)
                for personalData in ToSendPersonalDataList:
                    if personalData["ID"] == ID:
                        self.communicator.SendAddFriendReply(personalData["IP"], GlobalClientPort, True)
                        for Friend in FriendList:
                            if Friend["ID"] == personalData["ID"]:
                                FriendExistFlag = True
                        if FriendExistFlag == False:
                            self.communicator.BuddyBookDB.addFriend(personalData["ID"])
                        self.communicator.SendUpdatePersonalData(personalData["IP"], GlobalClientPort, ToSendPersonalDataList)
                        self.communicator.SendPostArticle(personalData["IP"], GlobalClientPort, self.communicator.BuddyBookDB.getArticleList())
                        break

        self.SetAddFriendPage()

    def RejectFriendOCL(self, ID):
        friendRequestList = self.communicator.BuddyBookDB.getFriendRequestList()
        for i in range(len(friendRequestList)):
            if friendRequestList[i]["ID"] == ID:
                personalDataList = self.communicator.BuddyBookDB.getPersonalDataList()
                for personalData in personalDataList:
                    if personalData["ID"] == ID:
                        self.communicator.SendAddFriendReply(personalData["ID"], GlobalClientPort, False)
                    break

        self.SetAddFriendPage()

    def FriendListPageOCL(self, index):
        Friend = copy.deepcopy(self.communicator.BuddyBookDB.getFriendList()[index])
        for personalData in copy.deepcopy(self.communicator.BuddyBookDB.getPersonalDataList()):
            if personalData["ID"] == Friend["ID"]:
                Dialog = QDialog()
                Dialog.setGeometry(400, 300, 600, 500)
                UserPage = QVBoxLayout()
                UserListWidget = QListWidget()

                userBackgroundPicture = QLabel()
                userBackgroundPicture.setPixmap(QPixmap(personalData["background_picture"]).scaled(100, 100, Qt.KeepAspectRatio))
                container = QListWidgetItem()
                container.setSizeHint(QSize(100, 100))
                UserListWidget.addItem(container)
                UserListWidget.setItemWidget(container, userBackgroundPicture)

                userProfilePicture = QLabel()
                userProfilePicture.setPixmap(QPixmap(personalData["profile_picture"]).scaled(100, 100, Qt.KeepAspectRatio))
                container = QListWidgetItem()
                container.setSizeHint(QSize(100, 100))
                UserListWidget.addItem(container)
                UserListWidget.setItemWidget(container, userProfilePicture)

                userName = QLabel()
                userName.setText(personalData["user_name"])
                container = QListWidgetItem()
                container.setSizeHint(QSize(100, 100))
                UserListWidget.addItem(container)
                UserListWidget.setItemWidget(container, userName)

                userProfileContext = QLabel()
                userProfileContext.setText(personalData["profile_context"])
                container = QListWidgetItem()
                container.setSizeHint(QSize(100, 100))
                UserListWidget.addItem(container)
                UserListWidget.setItemWidget(container, userProfileContext)

                UserPage.addWidget(UserListWidget)
                Dialog.setLayout(UserPage)

                Dialog.exec()
                break

    def LikeUpOCL(self, articleID):
        PersonalDataList = copy.deepcopy(self.communicator.BuddyBookDB.getPersonalDataList())
        SelfData = copy.deepcopy(self.communicator.BuddyBookDB.getSelfInformation())
        timTag = str(datetime.datetime.now().strftime("%Y.%m.%d.%H.%M.%S"))
        for PersonalData in PersonalDataList:
            self.communicator.SendLikeUp(PersonalData["IP"], GlobalClientPort, articleID, timTag)
        SelfCommand = {"header": "like_up", "body": {}}
        SelfCommand["body"]["article_ID"] = articleID
        SelfCommand["body"]["self_ID"] = SelfData["ID"]
        SelfCommand["body"]["latest_edit_time"] = timTag
        self.communicator.RecLikeUp("127.0.0.1", SelfCommand)

        self.communicator.BuddyBookDB.Save()

        self.SetArticleListPage()

    def PostArticleOCL(self, parent_ID, root_article_ID, content, image_content, position_tag, friend_tag):
        PersonalDataList = copy.deepcopy(self.communicator.BuddyBookDB.getPersonalDataList())
        SelfData = copy.deepcopy(self.communicator.BuddyBookDB.getSelfInformation())

        PositionTagList = str(position_tag).split()
        FriendTagList = str(friend_tag).split()

        FriendTagIDList = []

        for Friend in FriendTagList:
            ExistFlag = False
            IDBuffer = ""
            for PersonalData in PersonalDataList:
                if PersonalData["user_name"] == Friend:
                    ExistFlag = True
                    IDBuffer = PersonalData["ID"]
            if ExistFlag == True:
                FriendTagIDList.append(IDBuffer)

        timeTag = str(datetime.datetime.now().strftime("%Y.%m.%d.%H.%M.%S"))
        articleID = str(uuid.uuid4())

        ArticleTemplate = {
            "latest_edit_time": timeTag,
            "article_ID": articleID,
            "owner_ID": SelfData["ID"],
            "parent_ID": parent_ID,
            "root_article_ID": root_article_ID,
            "content": content,
            "image_content": image_content,
            "like_list": [],
            "position_tag": PositionTagList,
            "friend_tag": FriendTagIDList,
            "deletion": False
        }

        for PersonalData in PersonalDataList:
            self.communicator.SendPostArticle(PersonalData["IP"], GlobalClientPort, [ArticleTemplate])

        self.communicator.BuddyBookDB.updateArticle(
            ArticleTemplate["latest_edit_time"], ArticleTemplate["article_ID"], ArticleTemplate["owner_ID"],
            ArticleTemplate["parent_ID"], ArticleTemplate["root_article_ID"], ArticleTemplate["content"],
            ArticleTemplate["image_content"], ArticleTemplate["like_list"], ArticleTemplate["position_tag"],
            ArticleTemplate["friend_tag"], ArticleTemplate["deletion"])

        self.communicator.BuddyBookDB.Save()

    def CheckLikeUpList(self, articleID):
        ArticleList = self.communicator.BuddyBookDB.getArticleList()
        ArticleLikeList = []
        for article in ArticleList:
            if article["article_ID"] == articleID:
                ArticleLikeList = article["like_list"]
                ArticleLikeList = self.getLikeUpListName(ArticleLikeList)
                break
        ArticleLikeString = ""
        for user in ArticleLikeList:
            ArticleLikeString = ArticleLikeString + user + "，"
        Liker = QLabel()
        Liker.setText("喜歡這篇文章的有：" + ArticleLikeString)
        DialogLayout = QVBoxLayout()
        DialogLayout.addWidget(Liker)
        Dialog = QDialog()
        Dialog.setGeometry(700, 500, 200, 100)
        Dialog.setLayout(DialogLayout)
        Dialog.exec()

    def getLikeUpListName(self, LikeUpList):
        TrueNameLikeUpList = []
        personalDataList = self.communicator.BuddyBookDB.getPersonalDataList()
        for likeUser in LikeUpList:
            for personalData in personalDataList:
                if personalData["ID"] == likeUser:
                    TrueNameLikeUpList.append(personalData["user_name"])
        return TrueNameLikeUpList

    def commentArticle(self, parentArticleID):
        FriendList = self.communicator.BuddyBookDB.getFriendList()

        TargetArticle = self.communicator.BuddyBookDB.getTargetArticle(parentArticleID)
        Root_ID = ""
        if TargetArticle["root_article_ID"] == "":
            Root_ID = parentArticleID
        else:
            Root_ID = TargetArticle["root_article_ID"]
        commentDialog = self.AddArticleDialog(self, parentArticleID, Root_ID)
        commentDialog.setGeometry(500, 300, 300, 500)
        commentDialog.exec()


def main():
    app = QApplication(sys.argv)
    myQt = MyQt()
    sys.exit(app.exec())


main()
