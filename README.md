# Perspectiva - CivicLab - Demo

### Structure of the project

The project is splitted into three repositories:
- **data**: repository of the data and metadata (include in .gitignore)
- **notebook**: containing the exploration and experimentation
- **src**: script and code to run the prototype.
- **log**: logs of the application when running. (include in .gitignore)
- **config**: repository where the config TOML files are stored.

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

### GUI application and webservice

#### GUI Application with NiceGUI

One application was build as demonstration.

It is based on NiceGUI, a framework based on FastAPI to develop web application.
As a demonstrator, many features are not implemented.
Also, if the application is working, it presents many error in server side during refreshing.
However, it was tested and validated as harmless by the designer.

Contact the provider if the errors disturb the usage experience.

To run the application, from the root of the project repository execute:
```
$ python src/app.py
```

Then open your browser and go to `localhost:8080`.
See the log to see errors.

*warning*: the application try to find automatically your browser by default. If not existing, e.g. you run it in WSL, a message of error appears: `Connection lost. Trying to reconnect`. Then, press `:q` to exit `w3m` and return on the application.

The application works with a LLM in background. If you want to use the local model. Run it with the following command:

```
$ sh run_server.sh
```

Adapt `run_server.sh` regarding your hardware.

### Contact
Cyril François  
mail: [cyril.francois.87@gmail.com](mailto:cyril.francois.87@gmail.com)

