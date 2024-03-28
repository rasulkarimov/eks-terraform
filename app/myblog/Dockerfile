FROM ubi8/ubi:8.9-1136
MAINTAINER rasulkarimov
RUN mkdir /pythonapp && \
    chgrp 0 /pythonapp && \
    chmod g=u /pythonapp && \
    yum install python3 -y && \
    python3 -m pip install -U pip && \
    yum clean all -y 
COPY . /pythonapp/
WORKDIR /pythonapp/
RUN pip install -r ./requirements.txt
EXPOSE 8080
CMD ["gunicorn", "-w", "4", "--bind", "0.0.0.0:8080", "wsgi", "--access-logfile", "-"]
