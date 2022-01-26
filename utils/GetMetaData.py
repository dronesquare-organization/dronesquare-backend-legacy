import datetime


def getMetaData(tagLabel):
    metadata = {}
    if tagLabel["GPSInfo"] is not None:
        exifGPS = tagLabel["GPSInfo"]
        latData = list(exifGPS[2])
        lonData = list(exifGPS[4])
        Lat = latData[0] + float(latData[1] / 60) + float(latData[2] / 3600)
        Lon = lonData[0] + float(lonData[1] / 60) + float(lonData[2] / 3600)
        metadata["altitude"] = exifGPS[6]
        metadata["location"] = "POINT(" + str(Lon) + " " + str(Lat) + ")"
    if tagLabel["FocalLength"] is not None:
        metadata["focalLength"] = tagLabel["FocalLength"]
    if tagLabel["Make"] is not None:
        metadata["make"] = tagLabel["Make"].split("\x00")[0]
    if tagLabel["Model"] is not None:
        metadata["model"] = tagLabel["Model"].split("\x00")[0]
    if tagLabel["FNumber"] is not None:
        metadata["fNumber"] = tagLabel["FNumber"]
    if tagLabel["ExifImageWidth"] is not None:
        metadata["width"] = tagLabel["ExifImageWidth"]
    if tagLabel["ExifImageHeight"] is not None:
        metadata["height"] = tagLabel["ExifImageHeight"]
    if tagLabel["FocalLengthIn35mmFilm"] is not None:
        metadata["focalLengthIn35mmFilm"] = tagLabel["FocalLengthIn35mmFilm"]
    if tagLabel["DateTimeOriginal"] is not None:
        originalDate = (
            tagLabel["DateTimeOriginal"].split(" ")[0].replace(":", "-")
            + " "
            + tagLabel["DateTimeOriginal"].split(" ")[1]
        )
        metadata["created"] = datetime.datetime.strptime(
            originalDate, "%Y-%m-%d %H:%M:%S"
        )
    if tagLabel["DateTimeDigitized"] is not None:
        digitizedDate = (
            tagLabel["DateTimeDigitized"].split(" ")[0].replace(":", "-")
            + " "
            + tagLabel["DateTimeDigitized"].split(" ")[1]
        )
        metadata["modified"] = datetime.datetime.strptime(
            digitizedDate, "%Y-%m-%d %H:%M:%S"
        )
    if tagLabel["ISOSpeedRatings"] is not None:
        metadata["iSOSpeedRatings"] = tagLabel["ISOSpeedRatings"]

    return metadata
