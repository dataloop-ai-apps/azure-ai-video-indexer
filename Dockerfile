FROM hub.dataloop.ai/dtlpy-runner-images/cpu:python3.10_opencv

USER 1000
COPY requirements.txt /tmp/
RUN pip install --user -r /tmp/requirements.txt




# docker build --no-cache -t gcr.io/viewo-g/piper/agent/runner/cpu/azure-indexer:0.1.7 -f Dockerfile .
# docker push gcr.io/viewo-g/piper/agent/runner/cpu/azure-indexer:0.1.7
