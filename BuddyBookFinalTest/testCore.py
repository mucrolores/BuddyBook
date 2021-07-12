import json
import uuid
import socket
import time
import datetime
import base64
import threading
import imghdr
import os

dataSheetHeader = {
    "user_list": ["ID", "name", "IP"],
    "friend_list": ["ID"],
    "article_list": ["latest_edit_time", "article_ID", "owner_ID", "content", "image_content", "like_list", "position_tag", "friend_tag"],
    "personal_data_list": ["ID", "name", "profile_picture", "profile_context", "background_picture", "latest_edit_time"]
}

port = 9487


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

    def PictureNameToSendAbleData(self, fileName):
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

    def SendAbleDataToPictureName(self, fileDictionary):
        fileName = str(uuid.uuid4())
        fileType = fileDictionary["file_type"]
        fileFullName = fileName + "." + fileType
        file = open(fileFullName, "wb")
        file.write(base64.b64decode(fileDictionary["binary"]))
        file.close()

        return fileFullName

    # ========================================= User =========================================

    def getUserList(self):
        return self.DataBase["user_list"]

    def addUser(self, user_ID, user_name, user_IP):
        for userData in self.DataBase["user_list"]:
            if user_ID == userData["ID"]:
                return
        tmp = {"ID": user_ID, "name": user_name, "IP": user_IP}
        self.DataBase["user_list"].append(tmp)

    # ========================================= Friend =========================================

    # notice that targetID must getting from the DataBase["user_list"]
    def getFriendName(self, targetID):
        for i in self.DataBase["user_list"]:
            if i["ID"] == targetID:
                return i["name"]
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
        result = self.DataBase["article_list"].copy()
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
        print(type(deletion))
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
        for i in self.DataBase["article_list"]:
            if i["article_ID"] == article_ID and deletion:
                self.DataBase["article_list"][self.DataBase["article_list"].index(i)] = tmp
                return
            elif i["article_ID"] == article_ID and latest_edit_time > i["latest_edit_time"] and not deletion:
                for oldPicture in i["image_content"]:
                    os.remove(oldPicture["file_name"])
                ImageList = []
                for picture in tmp["image_content"]:
                    pictureRaw = base64.b64decode(picture["binary"])
                    pictureType = picture["file_type"]
                    pictureName = str(uuid.uuid4())
                    fullPictureName = pictureName + "." + pictureType
                    f = open(fullPictureName, "wb")
                    f.write(pictureRaw)
                    f.close()
                    pictureData = {"file_name": fullPictureName}
                    ImageList.append(pictureData)
                tmp["image_content"] = ImageList
                self.DataBase["article_list"][self.DataBase["article_list"].index(i)] = tmp
                return
            elif i["article_ID"] == article_ID and latest_edit_time <= i["latest_edit_time"]:
                return
        ImageList = []
        for picture in tmp["image_content"]:
            print(picture)
            pictureRaw = base64.b64decode(picture["binary"])
            pictureType = picture["file_type"]
            pictureName = str(uuid.uuid4())
            fullPictureName = pictureName + "." + pictureType
            f = open(fullPictureName, "wb")
            f.write(pictureRaw)
            f.close()
            pictureData = {"file_name": fullPictureName}
            ImageList.append(pictureData)
        tmp["image_content"] = ImageList
        self.DataBase["article_list"].append(tmp)

    # ========================================= Personal Data =========================================

    def getPersonalDataList(self):
        return self.DataBase["personal_data_list"]

    def getNewerPersonalData(self, PersonalDataList):
        result = self.DataBase["personal_data_list"].copy()
        for inputTest in PersonalDataList:
            for originData in result:
                if inputTest["ID"] == originData["ID"] and inputTest["latest_edit_time"] >= originData["latest_edit_time"]:
                    result.remove(originData)
        return result

    def updatePersonalData(self, user_ID, user_name, profile_picture, profile_context, background_picture, latest_edit_time):
        tmp = {
            "ID": user_ID,
            "user_name": user_name,
            "profile_picture": profile_picture,
            "profile_context": profile_context,
            "background_picture": background_picture,
            "latest_edit_time": latest_edit_time
        }
        for i in self.DataBase["personal_data_list"]:
            if user_ID == i["ID"] and latest_edit_time > i["latest_edit_time"]:
                OldProfilePicture = self.DataBase["personal_data_list"][self.DataBase["personal_data_list"].index(i)]["profile_picture"]
                OldBackgroundPicture = self.DataBase["personal_data_list"][self.DataBase["personal_data_list"].index(i)]["background_picture"]
                os.remove(OldProfilePicture)
                os.remove(OldBackgroundPicture)
                NewProfilePictureName = self.SendAbleDataToPictureName(tmp["profile_picture"])
                NewBackgroundPictureName = self.SendAbleDataToPictureName(tmp["background_picture"])
                tmp["profile_picture"] = NewProfilePictureName
                tmp["background_picture"] = NewBackgroundPictureName
                self.DataBase["personal_data_list"][self.DataBase["personal_data_list"].index(i)] = tmp
                return
            elif user_ID == i["ID"] and latest_edit_time <= i["latest_edit_time"]:
                return
        NewProfilePictureName = self.SendAbleDataToPictureName(tmp["profile_picture"])
        NewBackgroundPictureName = self.SendAbleDataToPictureName(tmp["background_picture"])
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
        self.BuddyBookDB = systemOperator("LocalDataBase.json")
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

        self.BuddyBookDB.Save()

    def PictureNameToSendAbleData(self, fileName):
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

    def SendAbleDataToPictureName(self, fileDictionary):
        fileName = str(uuid.uuid4())
        fileType = fileDictionary["file_type"]
        fileFullName = fileName + "." + fileType
        file = open(fileFullName, "wb")
        file.write(base64.b64decode(fileDictionary["binary"]))
        file.close()

        return fileFullName

    def RecAddFriendRequest(self, address, MessageDictionary):
        AddFriendRequestList = self.BuddyBookDB.getFriendRequestList()
        RequestBody = MessageDictionary["body"]
        if len(AddFriendRequestList) > 0:
            for dataRow in AddFriendRequestList:
                if dataRow["ID"] == RequestBody["selfs_ID"]:
                    return
        fileName = self.SendAbleDataToPictureName(RequestBody["profile_picture"])
        self.BuddyBookDB.addFriendRequest(RequestBody["selfs_ID"], RequestBody["user_name"], fileName)

    def RecAddFriendReply(self, address, MessageDictionary):
        friendList = self.BuddyBookDB.getFriendList()
        for data in friendList:
            if data["ID"] == MessageDictionary["body"]["selfs_ID"]:
                return
        if MessageDictionary["body"]["response"]:
            self.BuddyBookDB.addFriend(MessageDictionary["body"]["selfs_ID"])
            self.SendUpdatePersonalData(address[0],9487,self.BuddyBookDB.getPersonalDataList())

    def RecUpdatePersonalData(self, address, MessageDictionary):
        for personalData in MessageDictionary["body"]["personal_data_list"]:
            self.BuddyBookDB.updatePersonalData(
                personalData["ID"], personalData["user_name"], personalData["profile_picture"],
                personalData["profile_context"], personalData["background_picture"], personalData["latest_edit_time"])

    def RecPostArticle(self, address, MessageDictionary):
        UpdateArticleList = MessageDictionary["body"]["article_list"]
        for article in UpdateArticleList:
            self.BuddyBookDB.updateArticle(
                article["latest_edit_time"], article["article_ID"], article["owner_ID"],
                article["parent_ID"], article["root_article_ID"], article["content"],
                article["image_content"], article["like_list"], article["position_tag"],
                article["friend_tag"], article["deletion"]
            )

    def RecLikeUp(self, address, MessageDictionary):
        tmp = self.BuddyBookDB.getTargetArticle(MessageDictionary["body"]["article_ID"])
        # tmp is an article unit
        if tmp != {}:
            if MessageDictionary["body"]["self_ID"] not in tmp["like_list"]:
                tmp["like_list"].append(MessageDictionary["body"]["self_ID"])
                tmp["latest_edit_time"] = MessageDictionary["body"]["latest_edit_time"]
            self.BuddyBookDB.updateArticle(
                tmp["latest_edit_time"], tmp["article_ID"], tmp["owner_ID"],
                tmp["parent_ID"], tmp["root_article_ID"], tmp["content"],
                tmp["image_content"], tmp["like_list"], tmp["position_tag"],
                tmp["friend_tag"], tmp["deletion"]
            )

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

        self.SendSync1Response(address, port, AllNewerData)

    def RecSync1Response(self, address, MessageDictionary):
        return

    def RecSync2Request(self, address, MessageDictionary):
        return

    def SendAddFriendRequest(self, IP, port):
        selfInformation = self.BuddyBookDB.getSelfInformation()
        profilePictureData = self.PictureNameToSendAbleData(selfInformation["profile_picture"])
        Request = {"header": "add_friend_request", "body": {}}
        Request["body"]["selfs_ID"] = selfInformation["ID"]
        Request["body"]["user_name"] = selfInformation["user_name"]
        Request["body"]["profile_picture"] = {"file_type": profilePictureData["file_type"], "binary": profilePictureData["binary"]}
        Request["body"]["profile_context"] = selfInformation["profile_context"]

        self.TCPSend(IP, port, json.dumps(Request))
        print(json.dumps(Request, indent="\t", ensure_ascii=False))

    def SendAddFriedReply(self, IP, port, accept):
        selfInformation = self.BuddyBookDB.getSelfInformation()

        ToReplyUserData = {}
        UserList = self.BuddyBookDB.getUserList()
        for data in UserList:
            if data["IP"] == IP:
                ToReplyUserData = data

        AddFriendRequestList = self.BuddyBookDB.getFriendRequestList()
        for data in AddFriendRequestList:
            if data["ID"] == ToReplyUserData["ID"]:
                self.BuddyBookDB.deleteFriendRequest(ToReplyUserData["ID"])

                Request = {"header": "add_friend_reply", "body": {}}
                Request["body"]["selfs_ID"] = selfInformation["ID"]
                Request["body"]["response"] = accept

                self.TCPSend(IP, port, json.dumps(Request))
                print(json.dumps(Request, indent="\t", ensure_ascii=False))
        self.BuddyBookDB.Save()

    def SendUpdatePersonalData(self, IP, port, personalDataList):
        for personalDataRow in personalDataList:
            profilePictureData = self.PictureNameToSendAbleData(personalDataRow["profile_picture"])
            personalDataRow["profile_picture"] = profilePictureData
            backgroundPictureData = self.PictureNameToSendAbleData(personalDataRow["background_picture"])
            personalDataRow["background_picture"] = backgroundPictureData
        Request = {"header": "update_personal_data", "body": {"personal_data_list": personalDataList}}
        self.TCPSend(IP, port, json.dumps(Request))
        print(json.dumps(Request, indent="\t", ensure_ascii=False))

    def SendPostArticle(self, IP, port, articleDataList):
        Request = {"header": "post_article", "body": {}}
        ModifiedArticleList = []
        for article in articleDataList:
            image_content_list = []
            for pictures in article["image_content"]:
                print(pictures["file_name"])
                articlePictureData = self.PictureNameToSendAbleData(pictures["file_name"])
                picture = articlePictureData
                image_content_list.append(picture)
            article["image_content"] = image_content_list
            ModifiedArticleList.append(article)
        Request["body"]["article_list"] = ModifiedArticleList

        self.TCPSend(IP, port, json.dumps(Request))
        print(json.dumps(Request, indent="\t", ensure_ascii=False))

    def SendLikeUp(self, IP, port, article_ID, latest_edit_time):
        selfInformation = self.BuddyBookDB.getSelfInformation()
        Request = {"header": "like_up", "body": {}}
        Request["body"]["article_ID"] = article_ID
        Request["body"]["self_ID"] = selfInformation["ID"]
        Request["body"]["latest_edit_time"] = latest_edit_time

        self.TCPSend(IP, port, json.dumps(Request))
        print(json.dumps(Request, indent="\t", ensure_ascii=False))

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

    # OK
    def SendSync1Response(self, IP, port, selfNewerArticleList):
        Request = {"header": "sync2_Response", "body": {}}
        Request["body"]["data_list"] = selfNewerArticleList

        print(json.dumps(Request, indent="\t", ensure_ascii=False))

    def SendSync2Request(self, IP, port, NeedUpdateArticleList):
        Request = {"header": "sync2_Response", "body": {}}
        Request["body"]["data_list"] = NeedUpdateArticleList


# ==============================Test Row==============================


communicator = Communicator("127.0.0.1", 9487)
communicator.SendAddFriendRequest("127.0.0.1",9420)


# articleID = str(uuid.uuid4())
# f = open("test.jpg", "rb")
# PicRaw = f.read()
# ImageBinary = str(base64.b64encode(PicRaw), "UTF-8")
# fileType = str(imghdr.what("", PicRaw))
# ImageDict = {"file_type": fileType, "binary": ImageBinary}
# ImageList = [
#     {
#         "file_name": "aff5e3f8-c48d-4628-90c4-1a0a6956f993.png"
#     }
# ]
# Article = {
#     "latest_edit_time": "2019.11.20.11.11.34",
#     "article_ID": "2a1610f2-9cbb-4c1a-abf1-e0a32eaf17e7",
#     "owner_ID": "77da02d8-1f41-42ff-bd7a-2f02380c27f6",
#     "parent_ID": "",
#     "root_article_ID": "",
#     "content": "林口好冷ㄤㄤ",
#     "image_content": ImageList,
#     "like_list": [],
#     "position_tag": ["林口"],
#     "friend_tag": ["f4ae4397-c823-4f26-b16d-87c6e96d5b24"],
#     "deletion": True
# }
# communicator.SendPostArticle("127.0.0.1", 9420, [Article])
