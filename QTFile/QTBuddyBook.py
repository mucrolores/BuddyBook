import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class MyQt(QWidget):

    def __init__(self):
        super().__init__()

        self.setGeometry(300, 200, 800, 600)  # start X, start Y, WindowSizeX, WindowSizeY
        self.setWindowTitle("BuddyBook")
        self.pageStringList = ['個人資料', '好友邀請', '文章清單', '好友列表']

        self.MainLayout = QHBoxLayout()
        self.PageSelectLayout = QVBoxLayout()
        self.PageContextLayout = QVBoxLayout()

        self.PageSelectListWidget = QListWidget()
        self.CreatePageListWidget()

        self.PageContextListWidget = QListWidget()

        self.PageSelectLayout.addWidget(self.PageSelectListWidget)
        self.PageContextLayout.addWidget(self.PageContextListWidget)

        # Not set fixed as PersonalLayout

        self.MainLayout.addLayout(self.PageSelectLayout, 1)
        self.MainLayout.addLayout(self.PageContextLayout, 2)
        self.setLayout(self.MainLayout)
        self.show()

    def CreatePageListWidget(self):
        for i in self.pageStringList:
            item = QListWidgetItem()
            item.setText(i)
            item.setSizeHint(QSize(0, 100))
            tmp = QFont()
            tmp.setPointSize(20)
            item.setFont(tmp)
            self.PageSelectListWidget.addItem(item)
        self.PageSelectListWidget.itemClicked.connect(self.PageSelectedListWidgetOnclickListener)

    def SetPersonalPage(self):
        self.PageContextListWidget.clear()
        backGroundPicture = QListWidgetItem()
        backGroundPicture.setText("Background_Picture")
        backGroundPicture.setSizeHint(QSize(0, 200))

        ProfilePicture = QListWidgetItem()
        ProfilePicture.setText("ProfilePicture")
        ProfilePic = QLabel()
        ProfilePic.setPixmap(QPixmap("test.JPEG"))
        ProfilePic.setMaximumSize(100, 100)
        ProfilePicture.setSizeHint(QSize(0, 100))

        UserName = QListWidgetItem()
        UserName.setText("Mucolores")
        UserName.setSizeHint(QSize(0, 50))

        ProfileContext = QListWidgetItem()
        ProfileContext.setText("你好我是謝秉寰")
        ProfileContext.setSizeHint(QSize(0, 100))

        self.PageContextListWidget.addItem(backGroundPicture)
        self.PageContextListWidget.addItem(ProfilePicture)
        self.PageContextListWidget.setItemWidget(ProfilePicture, ProfilePic)
        self.PageContextListWidget.addItem(UserName)
        self.PageContextListWidget.addItem(ProfileContext)

    def SetAddFriendPage(self):
        self.PageContextListWidget.clear()
        # TODO :Make list to store input add friend request
        # TODO:Check the buttons in the item are able to be deleted by created object
        self.tmpList = []
        ItemWidget = self.AskedFriend(self)
        ItemWidget.setProfilePicture("test.jpg")
        ItemWidget.setUserName("1mucolores")
        ItemWidget.setUserID("0001")
        self.tmpList.append({"itemWidget": ItemWidget, "ID": "0001"})
        ItemWidget = self.AskedFriend(self)
        ItemWidget.setProfilePicture("test.jpg")
        ItemWidget.setUserName("2mucolores")
        ItemWidget.setUserID("0002")
        self.tmpList.append({"itemWidget": ItemWidget, "ID": "0002"})
        ItemWidget = self.AskedFriend(self)
        ItemWidget.setProfilePicture("test.jpg")
        ItemWidget.setUserName("3mucolores")
        ItemWidget.setUserID("0003")
        self.tmpList.append({"itemWidget": ItemWidget, "ID": "0003"})

        for Item in self.tmpList:
            container = QListWidgetItem()
            container.setSizeHint(QSize(200, 100))
            self.PageContextListWidget.addItem(container)
            self.PageContextListWidget.setItemWidget(container, Item["itemWidget"])

    def SetArticleListPage(self):
        self.PageContextListWidget.clear()

    def SetFriendListPage(self):
        self.PageContextListWidget.clear()
        FriendList = ["user1","user2","user3","user4","user5","user6","user7","user8"]
        for friendName in FriendList:
            tmp = QListWidgetItem()
            tmp.setSizeHint(QSize(300,100))
            tmpFont = QFont()
            tmpFont.setPointSize(20)
            tmp.setFont(tmpFont)
            tmp.setText(friendName)
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

    class AskedFriend(QWidget):
        def __init__(self, parent):
            super().__init__()
            self.UserProfilePicture = QLabel()
            self.UserProfilePicture.setMaximumSize(100, 100)
            self.UserName = QLabel()
            self.AcceptButton = QPushButton("Accept")
            self.RejectButton = QPushButton("Reject")
            self.userID = ""

            self.AcceptButton.clicked.connect(lambda: parent.AcceptFriendOCL(self.userID))

            self.ItemLayout = QHBoxLayout()
            self.ItemLayout.addWidget(self.UserProfilePicture)
            self.ItemLayout.addWidget(self.UserName)
            self.ItemLayout.addWidget(self.AcceptButton)
            self.ItemLayout.addWidget(self.RejectButton)
            self.setLayout(self.ItemLayout)

        def setProfilePicture(self, picturePath):
            self.UserProfilePicture.setPixmap(QPixmap(picturePath))

        def setUserName(self, userName):
            self.UserName.setText(userName)

        def getSelf(self):
            return self

        def setUserID(self, targetID):
            self.userID = targetID

        def getUserID(self):
            return self.userID

    def AcceptFriendOCL(self, ID):
        for i in range(self.PageContextListWidget.count()):
            if self.tmpList[i]["ID"] == ID:
                self.PageContextListWidget.takeItem(i)
                self.tmpList.remove(self.tmpList[i])
                break

        self.PageContextListWidget.update()

    def RejectFriendOCL(self, ToDeleteTarget):
        pass

    def FriendListPageOCL(self,index):
        print(index)
        Dialog = QDialog()
        UserPage = QHBoxLayout()




def main():
    app = QApplication(sys.argv)
    myQt = MyQt()
    sys.exit(app.exec())


main()
