FROM python:3.12

ENV RUNTIME_ENV container
ENV PYTHONUNBUFFERED true
ENV APP_HOST 0.0.0.0

RUN useradd -u 3000 recv

RUN mkdir -p \
    /home/recv \
    /workplace

WORKDIR /workplace
ADD . /workplace

RUN chown -R \
    3000:3000 \
    /home/recv \
    /workplace

USER 3000
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["sh", "/workplace/startup.sh"]
