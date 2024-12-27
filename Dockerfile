FROM python:3.12

ENV RUNTIME_ENV container
ENV PYTHONUNBUFFERED true

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

EXPOSE 5000
CMD ["gunicorn", "app:app"]
