FROM nexus-nid.stc/stc_facesdk_research/25floor/dataset_preparation:4b36d2809b766fab9b64ad96583bab8b4724d51c
USER root
RUN pip3 install flask
USER researcher
COPY toloka_processing_profile.xml /home/researcher/SDK_data/profiles/toloka_processing_profile.xml
COPY docker_code /code
WORKDIR /code
USER root
RUN mkdir -p /root/.local/lib/python3.6/site-packages \
    && cp /home/researcher/.local/lib/python3.6/site-packages/fsdk.pth /root/.local/lib/python3.6/site-packages/fsdk.pth
ENTRYPOINT ["python3", "main.py"]
