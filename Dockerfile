FROM vllm/vllm-openai:latest

# RunPod serverless SDK + http client
RUN pip install --no-cache-dir runpod requests

# HF cache lives on the network volume so weights download once
ENV HF_HOME=/runpod-volume/hf

COPY handler.py /handler.py
CMD ["python", "-u", "/handler.py"]
