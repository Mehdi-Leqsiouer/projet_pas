#!/usr/bin/env python
# coding: utf-8

# In[1]:


#get_ipython().system('pip install opencv-python')


# In[7]:


import cv2
import os
import csv
import boto3
import io
import re
import sys
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont


# In[3]:


def extractFramesFromVideo(videoFile,framesOutputDirectory):
    vidcap = cv2.VideoCapture(videoFile)
    success,image = vidcap.read()
    count = 0
    nb_of_frames=0
    while success:
        if count%12 == 0 :
            cv2.imwrite(framesOutputDirectory + "frame%d.jpg" % count, image)     # save frame as JPEG file
            nb_of_frames+=1
        success,image = vidcap.read()      
        print('Read a new frame: ', success)
        count += 1
    return nb_of_frames

def createVideoFromFrames(framesDirectory, videoName):
    images = [img for img in os.listdir(framesDirectory) if img.endswith(".jpg")]
    frame = cv2.imread(os.path.join(framesDirectory, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(videoName, 0, 2, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(framesDirectory, image)))

    cv2.destroyAllWindows()
    video.release()


# In[4]:


def getAWSRekognitionCredentials(csvFile):
    with open(csvFile,'r') as input:
        next(input)
        reader = csv.reader(input)
        for line in reader:
            access_key_id = line[2]
            secret_access_key = line[3]
            
    aws_region = 'us-east-2'
    return access_key_id, secret_access_key, aws_region


# In[5]:


def show_faces_and_emotions(imagesDirectory, annotatedImagesDirectory):
 
 rekognition = boto3.client('rekognition',aws_access_key_id=access_key_id,
             aws_secret_access_key=secret_access_key,
             region_name=aws_region)
    
 for imageFilename in os.listdir(imagesDirectory):
    imageFilePath = os.path.join(imagesDirectory, imageFilename)
    if os.path.isfile(imageFilePath):
        image=Image.open(imageFilePath)

        with open(imageFilePath, 'rb') as image_data:
         response_content = image_data.read()

        #Call DetectFaces 
        response = rekognition.detect_faces(Image={'Bytes':response_content}, Attributes=['ALL'])
        imgWidth, imgHeight = image.size 
        draw = ImageDraw.Draw(image) 
        ageFont = ImageFont.truetype("C:\Windows\Fonts\micross.ttf", 30)
        font = ImageFont.truetype("C:\Windows\Fonts\micross.ttf", 50)

        # calculate and display bounding boxes for each detected face 
        print('Annotating faces in ' + imageFilePath + ' file.') 
        for faceDetail in response['FaceDetails']:

            box = faceDetail['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']

            #print('Left: ' + '{0:.0f}'.format(left))
            #print('Top: ' + '{0:.0f}'.format(top))
            #print('Face Width: ' + "{0:.0f}".format(width))
            #print('Face Height: ' + "{0:.0f}".format(height))

            points = (
            (left,top),
            (left + width, top),
            (left + width, top + height),
            (left , top + height),
            (left, top)
            )

            draw.line(points, fill='#00d400', width=2)
            # Alternatively can draw rectangle. However you can't set line width.
            #draw.rectangle([left,top, left + width, top + height], outline='#00d400')

            #Write emotion of each person in image file
            face_emotion_confidence = 0
            face_emotion = None
            for emotion in faceDetail.get('Emotions'):
             if emotion.get('Confidence') >= face_emotion_confidence:
                 face_emotion_confidence = emotion['Confidence']
                 face_emotion = emotion.get('Type')
            draw.text((left, top + height),face_emotion.capitalize(),(0,0,0),font=font)
            
            #Write age ranges to image file
            ageRange = str(faceDetail['AgeRange']['Low']) + '-' + str(faceDetail['AgeRange']['High']) + ' years old'
            draw.text((left, top + height + 50),ageRange,(0,0,0),font=ageFont)

        image.save(os.path.join(annotatedImagesDirectory, 'annotated_' + imageFilename))
    else:
        print(imageFilePath + " is not a file.")

 return len([name for name in os.listdir(annotatedImagesDirectory) if os.path.isfile(os.path.join(annotatedImagesDirectory, name))])


# In[6]:


videoFile = sys.argv[1]
print(videoFile)
#videoFile=r"CT028.mov"
framesDirectory=r"./video_frames/"
credentialsFile=r"new_user_credentials.csv"
annotatedImagesDir=r"./annotated_images/"
access_key_id, secret_access_key, aws_region = getAWSRekognitionCredentials(credentialsFile)
annotatedVideo=r"annotated_video.avi"

nb_frames=extractFramesFromVideo(videoFile,framesDirectory)
#print("\n" + str(nb_frames) + " frames has been extracted from " + videoFile + " file.")

nb_annotated_images=show_faces_and_emotions(framesDirectory, annotatedImagesDir)
#print("\n" + str(nb_annotated_images) + " images has been annotated.")

createVideoFromFrames(annotatedImagesDir, annotatedVideo)

