# Analyzes text in a document stored in an S3 bucket. Display polygon box around text and angled text

import boto3
import io
import sys
from PIL import Image, ImageDraw
import numpy as np
from gensim import models

sys.path.append('.')

word2vec = models.KeyedVectors.load_word2vec_format(
    '/homes/zahara/PycharmProjects/text_button_detection/data/GoogleNews-vectors-negative300.bin.gz', binary=True,
    limit=500000)


def ShowBoundingBox(draw, box, width, height, boxColor):
    left = width * box['Left']
    top = height * box['Top']
    draw.rectangle([left, top, left + (width * box['Width']), top + (height * box['Height'])], outline=boxColor)

    t = [left, top, left + (width * box['Width']), top + (height * box['Height'])]
    # print(f'Real pixel size: {t}')
    return t[0], t[1], t[2], t[3]


def ShowSelectedElement(draw, box, width, height, boxColor):
    left = width * box['Left']
    top = height * box['Top']
    draw.rectangle([left, top, left + (width * box['Width']), top + (height * box['Height'])], fill=boxColor)


# Displays information about a block returned by text detection and text analysis
def DisplayBlockInformation(block):
    print('Id: {}'.format(block['Id']))
    if 'Text' in block:
        print('    Detected: ' + block['Text'])
    print('    Type: ' + block['BlockType'])

    if 'Confidence' in block:
        print('    Confidence: ' + "{:.2f}".format(block['Confidence']) + "%")

    if block['BlockType'] == 'CELL':
        print("    Cell information")
        print("        Column:" + str(block['ColumnIndex']))
        print("        Row:" + str(block['RowIndex']))
        print("        Column Span:" + str(block['ColumnSpan']))
        print("        RowSpan:" + str(block['ColumnSpan']))

    if 'Relationships' in block:
        print('    Relationships: {}'.format(block['Relationships']))
    print('    Geometry: ')
    print('        Bounding Box: {}'.format(block['Geometry']['BoundingBox']))
    print('        Polygon: {}'.format(block['Geometry']['Polygon']))

    if block['BlockType'] == "KEY_VALUE_SET":
        print('    Entity Type: ' + block['EntityTypes'][0])

    if block['BlockType'] == 'SELECTION_ELEMENT':
        print('    Selection element detected: ', end='')

        if block['SelectionStatus'] == 'SELECTED':
            print('Selected')
        else:
            print('Not selected')

    if 'Page' in block:
        print('Page: ' + block['Page'])
    print()


def process_text_analysis(bucket, document):
    # Get the document from S3
    s3_connection = boto3.resource('s3')

    s3_object = s3_connection.Object(bucket, document)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image = Image.open(stream)

    # resp = urllib.urlopen('https://buttunscreenshot.s3.eu-central-1.amazonaws.com/012.png')
    # img_disp = np.asarray(bytearray(resp.read()), dtype="uint8")
    # img_disp = cv.imdecode(img_disp, cv.IMREAD_COLOR)
    # squares = find_squares(img_disp)
    # cv.drawContours(img, squares, -1, (0, 0, 255), 2)

    # Analyze the document
    client = boto3.client('textract')

    image_binary = stream.getvalue()
    response = client.analyze_document(Document={'Bytes': image_binary},
                                       FeatureTypes=["TABLES", "FORMS"])

    # Alternatively, process using S3 object
    # response = client.analyze_document(
    #    Document={'S3Object': {'Bucket': bucket, 'Name': document}},
    #    FeatureTypes=["TABLES", "FORMS"])

    # Get the text blocks
    blocks = response['Blocks']
    width, height = image.size
    # print(f'image.size: {image.size}')
    draw = ImageDraw.Draw(image)
    # print('Detected Document Text')

    result_words = []
    # Create image showing bounding box/polygon the detected lines/text
    for block in blocks:

        draw = ImageDraw.Draw(image)

        if block['BlockType'] == 'WORD' and len(block['Text']) > 1:
            text = ''.join([i if i.isalpha() else '' for i in block['Text']])

            x1, y1, x2, y2 = ShowBoundingBox(draw, block['Geometry']['BoundingBox'], width, height, 'red')
            # DisplayBlockInformation(block)
            # print('location:')
            # print(x1, y1, x2, y2)
            # print('Text:')
            # print(text)

            result_words.append([text, [x1, y1, x2, y2]])
            # if text in word2vec:
            #     vec = word2vec[text]

                # print(f'Vector faund - length:{len(vec)}')
                # print(vec)
            # else:
            #     print('Vector not faund=================================')

    # Display the image
    # image.show()

    # cv.imshow('squares', img)
    # cv.imwrite(f'data/simple-squares/{i}', img)
    np_im = np.array(image)

    result = Image.fromarray(np_im.astype(np.uint8))
    # result.save('out.png')

    return result_words  # len(blocks)


def ocr():
    s3 = boto3.resource('s3')
    b_name = 'buttunscreenshot'

    # Load pretrained word2vec (since intermediate data is not included, the word2vec cannot be refined with additional data)

    my_bucket = s3.Bucket(b_name)
    for my_bucket_object in my_bucket.objects.all():
        print(my_bucket_object.key)
        document = my_bucket_object.key
        block_count = process_text_analysis(b_name, document)
        print("Blocks detected: " + str(block_count))
    # block_count = process_text_analysis( b_name, 'c46.png')

    #
    # dog = word2vec['dog']
    # print(dog.shape)
    # print(dog[:10])




if __name__ == "__main__":
    ocr()

