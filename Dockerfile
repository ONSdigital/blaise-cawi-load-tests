FROM locustio/locust
RUN pip3 install locust-plugins 
RUN pip3 install python-dotenv
