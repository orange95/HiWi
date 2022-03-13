FROM alpine:3.5 as buildgit
RUN apk update && apk add git
RUN mkdir -p /filip
WORKDIR /filip
RUN git clone "https://github.com/RWTH-EBC/FiLiP.git"

FROM python:3-slim
COPY --from=buildgit /filip/FiLiP /filip

RUN pip install /filip

ADD .env /
ADD app.py /
ADD index.py /
ADD helper_function /helper_function/
ADD assets /assets/

COPY ./requirements.txt /requirements.txt

RUN pip install -r requirements.txt

CMD [ "python", "-u","./index.py" ]
