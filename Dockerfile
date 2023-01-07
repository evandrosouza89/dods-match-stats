FROM python:3

ARG DMS_HOME=/opt/dods-match-stats
ARG DMS_HTML_OUTPUT=/var/www/dods-match-stats/html

WORKDIR $DMS_HOME

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 -m pip install PyMySQL
RUN python3 -m pip install cryptography

COPY . .

RUN mkdir -p $DMS_HTML_OUTPUT
COPY /assets/paper.jpg $DMS_HTML_OUTPUT

RUN mkdir $DMS_HOME/logs

RUN chmod u=rwx $DMS_HOME/scripts/dods-match-stats.sh

CMD /bin/bash $DMS_HOME/scripts/dods-match-stats.sh dms-instance-1