FROM ubuntu:20.04

EXPOSE 5000
ENV TZ=Asia/Shanghai
ENV DEBIAN_FRONTEND=noninteractive

# Create upload directory
RUN mkdir -p /temp_uploads && chmod 777 /temp_uploads

COPY ocr-api.py /
COPY requirements.txt /tmp

# Install system dependencies
RUN apt-get update \
    && apt-get install -y \
    python3 \
    python3-pip \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    # Dependencies for PyMuPDF
    build-essential \
    libmupdf-dev \
    python3-dev \
    && pip install -r /tmp/requirements.txt \
    && apt-get -y remove python3-pip \
    && apt-get -y autoremove \
    && apt-get -y install --no-install-recommends python3-setuptools \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/ /root/.cache /tmp/*

VOLUME ["/temp_uploads"]
CMD ["python3", "/ocr-api.py"]