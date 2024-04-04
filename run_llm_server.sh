python -m vllm.entrypoints.openai.api_server\
    --model TheBloke/NeuralBeagle14-7B-AWQ\
    --chat-template ./config/template_chatml.jinja\
    --quantization awq\
    --trust-remote-code\
    --max-model-len 2048