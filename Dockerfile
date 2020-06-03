FROM nvidia/cuda
USER root
RUN apt update && \
    apt -y install python3-pip cython3 libsm6 libxext6 libxrender-dev && \
	pip3 install --default-timeout=100 flask numpy opencv-python torch python-config
COPY docker_code /code
WORKDIR /code
RUN cython3 iou.pyx && \
	gcc -c -fPIC $(python3-config --includes) -o iou.o iou.c && \
	gcc -shared -L/usr/lib/x86_64-linux-gnu $(python3-config --libs) iou.o -o iou.so
ENTRYPOINT ["python3", "main.py"]
