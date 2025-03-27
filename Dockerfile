FROM python:3

ENV HOME_DIR=${HOME_DIR:-/opt/dods-match-stats}
ENV OUTPUT_DIR=${OUTPUT_DIR:-$HOME_DIR/reports}

WORKDIR $HOME_DIR

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 -m pip install PyMySQL
RUN python3 -m pip install cryptography

COPY . .

RUN mkdir -p $OUTPUT_DIR

RUN mkdir $HOME_DIR/logs

CMD ["python3", "__main__.py"]