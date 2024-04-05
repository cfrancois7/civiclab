# Perspectiva - CivicLab - Demo

### Structure of the project

The project is splitted into three repositories:
- **data**: repository of the data and metadata (include in .gitignore)
- **notebook**: containing the exploration and experimentation
- **src**: script and code to run the prototype.
- **log**: logs of the application when running. (include in .gitignore)
- **config**: repository where the config TOML files are stored.
- **template**: repository where the template for the LLM model are stored.

```
.
├── configs
│   ├── llm.toml
│   └── my_model.yaml
├── data
│   ├── metadata.csv
│   └── nba_logreg.csv
├── log
├── notebook
│   └── 0_data_discovery.ipynb
├── requirement.txt
├── src
│   ├── app.py
│   ├── ...
│   └── ...
└── template
    └── template_chatml.jinja
```

### Clone the code

1. Install git and python in your environnement
2. Create a virtual environnement with your preferate tool.
3. Clone the repot with : `git clone https://github.com/cfrancois7/civiclab.git`.
4. Install the requirements with: `pip install -r requirements. txt`

Once it is done, copy your data and the correct file to use the plateform. If you do not know what it is about, contact the owner: [cyril.francois.87@gmail.com](mailto:cyril.francois.87@gmail.com).

### Run the application

#### The web server
To run the application, you can execute the command:
```
uvicorn src.main:app --reload --log-level debug --port 8000
```

If you are in linux, you can use the bash script:
```
$ sh startup.sh
```

#### The local model

This part is only for expert. It means you have already download and install a local LLM model.

If it is the case, you can run your local model with this kind of command:

```
python -m vllm.entrypoints.openai.api_server\
    --model TheBloke/NeuralBeagle14-7B-AWQ\
    --chat-template ./config/template_chatml.jinja\
    --quantization awq\
    --trust-remote-code\
    --max-model-len 2048
```

Or:
```
sh run_server.sh
```

Adapt the configs regarding your hardware.

### Contact
Cyril François  
mail: [cyril.francois.87@gmail.com](mailto:cyril.francois.87@gmail.com)

