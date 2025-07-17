from flask import Flask, request, render_template, redirect
import boto3 
import json
import csv
import PyPDF2, io


textractclient = boto3.client("textract", aws_access_key_id="AKIAQKPILVD6VV5X7O46",
                              aws_secret_access_key="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", region_name="us-east-1")

app = Flask(__name__)


@app.route("/", methods=["GET"])
def main():
    return render_template("index.html", jsonData=json.dumps({}))


@app.route("/<string:page_name>")
def html_page(page_name):
    return render_template(page_name)


@app.route("/extractImg", methods=["POST"])
def extractImage():
    file = request.files.get("filename")
    binaryFile = file.read()
    response = textractclient.detect_document_text(
        Document={
            'Bytes': binaryFile
        }
    )

    extractedText = ""

    for block in response["Blocks"]:
        if block["BlockType"] == "LINE":
           #print('\033[94m' + item["Text"] + '\033[0m')
            extractedText = extractedText+block["Text"]+" "

    responseJson = {

        "text": extractedText
    }


# Print or return the extracted text
    print(responseJson)
    return render_template("works.html", jsonData=json.dumps(responseJson))


@app.route("/extractPdf", methods=["POST"])
def extractpdf():
    file = request.files.get("pdffilename")
    page_text = ""
    if file:
        pdf_data = file.read()

        # Open the PDF using PyMuPDF
        pdf_reader = PyPDF2.PdfFileReader(io.BytesIO(pdf_data))

        # Extract text from all pages
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            page_text += page.extractText() + "\n"


    responseJson = {
        "text": page_text
    }

    # Print or return the extracted text
    print(responseJson)
    return render_template("works.html", jsonData=json.dumps(responseJson))


def write_to_csv(data):
    with open('database12.csv', newline='', mode='a') as database:
        email = data["email"]
        subject = data["subject"]
        message = data["feedback"]
        csv_writer = csv.writer(database, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([email, subject, message])


@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        data = request.form.to_dict()
        write_to_csv(data)
        print(data)
        return redirect('/thankyou.html')


if __name__ == '__main__':
    app.run()
