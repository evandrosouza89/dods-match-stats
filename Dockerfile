FROM python:3

ENV DMS_HOME=/opt/dods-match-stats
ENV DMS_HTML_OUTPUT=/var/www/dods-match-stats/html

WORKDIR $DMS_HOME

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 -m pip install PyMySQL
RUN python3 -m pip install cryptography

COPY . .

RUN mkdir -p $DMS_HTML_OUTPUT
COPY /assets/banner.jpg $DMS_HTML_OUTPUT

RUN mkdir $DMS_HOME/logs

#RUN apt-get update
#RUN apt-get -y install conntrack
#CMD conntrack -D -p UDP;/bin/bash $DMS_HOME/scripts/dods-match-stats.sh dms-instance-1

CMD /bin/bash $DMS_HOME/scripts/dods-match-stats.sh dms-instance-1