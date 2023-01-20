import os

from os import path, mkdir, listdir, remove
class fileJobs:
    def __init__(self, bc, fl):
        self.buttonCount = bc
        self.fileLocation = fl

    def generateFolders(self):
        for file in range(self.buttonCount):
            file += 1
            if not path.isdir(self.fileLocation + str(file)):
                mkdir(self.fileLocation + str(file))

    def getFiles(self, folder:  int) -> list:
        pathway = self.fileLocation + str(folder) + "/"
        return [os.path.splitext(filename)[0] for filename in os.listdir(pathway)]

    def saveFile(self, button: int, fileName: str, content):
        pathway = self.fileLocation + str(button) + "/"
        file = open(pathway + fileName + ".pdf", "wb")
        file.write(content)
        file.close()

    def deleteFiles(self, button: int, files: list):
        for file in files:
            pathway = self.fileLocation + str(button) + "/" + file + '.pdf'
            if path.exists(pathway):
                remove(pathway)
