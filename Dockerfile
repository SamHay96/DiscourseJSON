FROM python:3
ADD langProcessing.py /
RUN pip install flask
RUN pip install requests
RUN pip install flask-restful
RUN pip install nltk
RUN python -m nltk.downloader punkt
RUN python -m nltk.downloader vader_lexicon
RUN python -m nltk.downloader averaged_perceptron_tagger

CMD [ "python", "./langProcessing.py" ]