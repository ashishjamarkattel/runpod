FROM vllm/vllm-openai:latest

# RunPod serverless SDK + http client
RUN pip install --no-cache-dir runpod requests

# HF cache lives on the network volume so weights download once
ENV HF_HOME=/runpod-volume/hf

COPY handler.py /handler.py

# The vllm/vllm-openai base image sets an ENTRYPOINT (the api_server). Clear it
# so our CMD runs the RunPod handler directly instead of being passed as args.
ENTRYPOINT []
CMD ["python3", "-u", "/handler.py"]
