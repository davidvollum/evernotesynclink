__author__ = 'davidvollum'
from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types
import os
import hashlib
import evernote.edam.error.ttypes as Errors
import sys
import logging


#Constants

#Must be a legal directory with only pdfs and text files in it; must end in a "/"/Users/davidvollum/Documents/testing/
directoryPath="/files/webdav/"

#where the actual python sctipt is stored
infoPath = "/home/administrator/Documents/Evernote/"

#determines weather to use manifests to prevent duplicate uploads Normal = True
useManifest=True

#badFiles contains a list of special files used by the OS that should not be uploaded or messed with:
badFiles=[".DS_Store"]

#logging.basicConfig(level=logging.INFO)

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename=infoPath +'evernote.log',level=logging.INFO)
#logging.debug('This message should go to the log file')
#logging.info('So should this')
#logging.warning('And this, too')



dev_token = "S=s311:U=331bcad:E=16100618828:C=159a8b05ad8:P=1cd:A=en-devtoken:V=2:H=c086f429ae16e1c1532f3e2893e09fd1"
client = EvernoteClient(token=dev_token, sandbox=False)
userStore = client.get_user_store()
user = userStore.getUser()

logging.info("Starting upload for user: " +  user.username)
#logging.info("")
noteStore = client.get_note_store()
notebooks = noteStore.listNotebooks()


def readfile(path):
    file = open(path)
    data=file.read()
    file.close()
    return data


class TheFile:
    def __init__(self, fileName, filePath, fileType, notebook, data=None):
        self.fileName = fileName
        self.filePath = filePath
        self.fileType = fileType
        self.notebook = notebook
        self.dateModified = str(os.path.getatime(filePath))
        self.data = data
    def getNoteName(self):
        noteName=self.fileName.split(".")
        return noteName[0]
    def getData(self):
        #print self.fileType
        if self.data:
            return self.data
        elif self.fileType == ".txt":
            data = readfile(self.filePath)
            #print data + "that data though"
            return data
        else:
            return "no data so you get this instead"





# **noteStore.createNote
# for n in notebooks:
#   print n.name
# os.path.getatime(/volumes)
# os.listdir()


def createNote(authToken, noteStore, noteTitle, noteBody, fileType, pathToFile=None, notebook=None):
        # Create the new note
        note = Types.Note()
        note.title = noteTitle
        if notebook:
            note.notebookGuid=notebook.guid
        note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        note.content += '<en-note>'
        note.content += noteBody
        note.content += '<br/>'

        # Calculate the md5 hash of the pdf
        if fileType == ".pdf":
            md5 = hashlib.md5()
            pdfFile = open(pathToFile,'rb')
            pdf_bytes = pdfFile.read()
            md5.update(pdf_bytes)
            md5hash = md5.hexdigest()

            # Create the Data type for evernote that goes into a resource
            pdf_data = Types.Data()
            pdf_data.bodyHash = md5hash
            pdf_data.size = len(pdf_bytes)
            pdf_data.body = pdf_bytes

            # Add a link in the evernote boy for this content
            link = '<en-media type="application/pdf" hash="%s"/>' % md5hash
            note.content += link

            # Create a resource for the note that contains the pdf
            pdf_resource = Types.Resource()
            pdf_resource.data = pdf_data
            #print pdf_resource.mime
            pdf_resource.mime = "application/pdf"

            # Create a resource list to hold the pdf resource
            resource_list = []
            resource_list.append(pdf_resource)

            # Set the note's resource list
            note.resources = resource_list
        note.content += '</en-note>'



        try:
            theNote = noteStore.createNote(authToken, note)
        except Errors.EDAMUserException, edue:
            ## Something was wrong with the note data
            ## See EDAMErrorCode enumeration for error code explanation
            ## http://dev.evernote.com/documentation/reference/Errors.html#Enum_EDAMErrorCode
            logging.error("EDAMUserException:" + str(edue))
            return None
        except Errors.EDAMNotFoundException, ednfe:
            ## Parent Notebook GUID doesn't correspond to an actual notebook
            logging.error("EDAMNotFoundException: Invalid parent notebook GUID")
            return None
        ## Return created note object
        return note


def getNotebook(notebookName, noteStore, authToken,  stack=None):
        notebooks = noteStore.listNotebooks()
        logging.debug(notebooks)
        notebookNames={}
        for theNotebook in notebooks:
            notebookNames[theNotebook.name]=theNotebook
        if notebookName in notebookNames.keys():
            logging.debug("found something")
            # Existing notebook, so just update the stack if needed
            notebook = notebookNames[notebookName]
            if stack:
                notebook.stack = stack
                noteStore.updateNotebook(notebook)
            return notebook
        else:
            # Need to create a new notebook
            notebook = Types.Notebook()
            notebook.name = notebookName
            logging.info("manifestPath " + notebook.name + "Notebook name " + notebookName)
            if stack:
                notebook.stack = stack
            notebook = noteStore.createNotebook(authToken, notebook)
            return notebook

def inManifest(path, fileName):
    filePath=path+fileName
    #print filePath + ":filepath"
    #dateModified=os.path.getatime(filePath)
    #print dateModified
    try:
        manifestFile = open(infoPath +"manifest.txt", "r+")
    except IOError:
        logging.info("could not find manifest, creating a new one")
        manifestFile = open(infoPath + "manifest.txt", "w+")
    filesInManifest=manifestFile.read()
    filesInManifest = filesInManifest.split("|")
    for line in filesInManifest:
        line=line.strip()
        #print "comparing line "+line+" filname "+fileName
        if line == fileName:
            #print("found match")
            return useManifest
    manifestFile.write(fileName+"|")
    manifestFile.close()
    return False

#returns a list of tuples. tuples are filename, subfolder, filetype
def getFilesToUpload(path, manifestPath):
    files=os.listdir(path)
    #print str(files) + "uggggg"
    filesList=[]
    for fileName in files:
        filePath=path+fileName
        fileType = os.path.splitext(filePath)[-1].lower()
        #dateModifyed=os.path.getatime(filePath)
        logging.debug(fileType)
        logging.debug("file: " + fileName + " is a .txt or .pdf " + str(".pdf" == fileType or ".txt" == fileType))

        if fileType=="" and fileName not in badFiles:
            logging.debug("found subfolder")
            logging.debug(filesList)
            filesList = filesList+getFilesToUpload(filePath+"/", manifestPath)
        elif ".pdf" == fileType or ".txt" == fileType and fileName not in badFiles:
            if inManifest(manifestPath,fileName)==False:
                theNotebook = getNotebook(path.split("/")[-2], noteStore, dev_token)
                logging.info("found file: " + fileName + " in folder: " + path.split("/")[-2] + " with fileType: " + fileType)
                logging.debug(theNotebook)
                logging.info("Preparing: " + fileName + " for upload")
                filesList.append(TheFile(fileName,filePath,fileType,theNotebook))
            else:
                logging.info("skipping: " + fileName)
        else:
            logging.warning("Invalid Path or File type for file: " + fileName)
    return filesList


def readDirectory(path):
    filesToUpload = getFilesToUpload(path, path)
    for fileToUpload in filesToUpload:
        logging.info("found " + fileToUpload.fileType + " file: " + fileToUpload.fileName + " which was last modified: " + fileToUpload.dateModified)
        #data=readfile(filePath)
        #print(theNotebook)
        createNote(dev_token, noteStore, fileToUpload.getNoteName(), fileToUpload.getData(), fileToUpload.fileType, fileToUpload.filePath, notebook=fileToUpload.notebook)
        logging.info("uploading: " + fileToUpload.fileName)


args = sys.argv
if "-noManifest" in args:
    print "Not using the Manifest: THIS IS NOT NORMAL"
    useManifest = False

if "-generateManifestOnly" in args:
    print "Gennerating manifest only"
    getFilesToUpload(directoryPath,directoryPath)
#new feature not in final
if "-path:" in args:
    index=0
    for arg in args:
        if arg == "-path:":
            args[index+1] = directoryPath
        else:
            index+=1
    readDirectory(directoryPath,directoryPath)
else:
    readDirectory(directoryPath)
#getFilesToUpload(directoryPath, directoryPath)