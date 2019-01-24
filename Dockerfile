FROM python:3
ADD langProcessing.py /
RUN pip install flask
RUN pip install requests
RUN pip install flask-restful
RUN pip install nltk
CMD [ "python", "./langProcessing.py" ]