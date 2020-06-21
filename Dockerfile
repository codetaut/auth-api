FROM python:3.8.3
EXPOSE 8000
COPY . /application
WORKDIR /application
RUN pip install -r requirements/dev.txt
ENTRYPOINT ["python"]
CMD ["server.py"]