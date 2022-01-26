import os
import re


def createFileName(fileDir, fileName):
    num = 1
    while os.path.exists(fileDir):
        dir = os.path.split(fileDir)
        regex = re.compile(r"\-[0-9]+\.")

        matchobj = regex.search(dir[1])
        if matchobj is not None:
            fileName = dir[1].replace(matchobj.group(), "-" + str(num) + ".")
            fileDir = os.path.join(dir[0], fileName)
            num += 1
        else:
            fileName = (
                dir[1].split(".")[0] + "-" + str(num) + "." + dir[1].split(".")[1]
            )
            fileDir = os.path.join(dir[0], fileName)
            num += 1
    return fileName
