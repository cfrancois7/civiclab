from nicegui import ui, events, app
from io import StringIO
import logging
from pandas import read_csv
from openai import OpenAI, AsyncOpenAI
import tomllib
from state import State

COLUMNS = [
    "QUXVlc3Rpb246MTYz - Que faudrait-il faire pour rendre la fiscalité plus juste et plus efficace ?",
    "title",
]

LLM_STATE = State(on_going=False)


##########
# FUNCTION
##########
def load_valid_data(data_state):

    data = read_csv("./data/LA_FISCALITE_ET_LES_DEPENSES_PUBLIQUES_2.csv")
    data_state.validated_data = data[COLUMNS].dropna()
    data_state.validated = True
    ui.notify("Data successfully loader!")

    columns = [
        {"name": col, "label": col, "field": col, "align": "left"} for col in COLUMNS
    ]
    table_extract.columns = columns
    table_extract.rows = data_state.validated_data.to_dict("records")
    table_extract.update()


def select_row(state, row):
    selected_row = row.args[1]
    content = selected_row[COLUMNS[0]]
    msg = "**Contenu original :**  \n\n" + f"*{content}*"
    content_orig.set_content(msg)


async def query_llm():
    model = radio_llm.value

    LLM_STATE.on_going = True
    ui.notify("Run LLM on going ...")
    input = content_orig.content.split("**Contenu original :**  \n\n")[-1][1:-1]
    logging.info(input)

    if model == "local":
        output = await run_local_llm(input)
    elif model == "GPT-3.5 Turbo":
        output = await run_openai_llm(input, "gpt-3.5-turbo")
    elif model == "GPT-4 Turbo":
        output = await run_openai_llm(input, "gpt-4-turbo-preview")

    msg = f"""**Extrait des idées principales :**
    ```python
    {output}
    ```
    """
    LLM_STATE.on_going = False
    content_extract.set_content(msg)


async def run_local_llm(input):
    with open("./config/local_llm.toml", "rb") as file:
        configs = tomllib.load(file)

    client = AsyncOpenAI(
        base_url=configs["server"]["base_url"],
        api_key=configs["server"]["api_key"],
    )

    system_message = configs["template"]["system"]
    user_message = configs["template"]["user"].format(input=input)

    completion = await client.chat.completions.create(
        model=configs["model"]["name"],
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        stop=configs["model"]["stop"],
        top_p=configs["model"]["top_p"],
        temperature=configs["model"]["temperature"],
    )

    content = completion.choices[0].message.content
    logging.info(content)

    return content.split("```")[1]


async def run_openai_llm(input, model_name):
    with open("./config/openai.toml", "rb") as file:
        configs = tomllib.load(file)

    client = AsyncOpenAI(
        api_key=configs["server"]["api_key"],
    )

    system_message = configs["template"]["system"]
    user_message = configs["template"]["user"].format(input=input)

    completion = await client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        top_p=configs["model"]["top_p"],
        temperature=configs["model"]["temperature"],
        response_format=configs["model"]["response_format"],
    )

    content = completion.choices[0].message.content
    logging.info(content)

    return content


##########
# LAYOUT
##########
@ui.refreshable
def section_extract(data_state):
    global table_extract, content_orig, content_extract, spinner, radio_llm
    # to remove after bug test
    ui.button("load valid data", on_click=lambda e: load_valid_data(data_state))
    with ui.column().bind_visibility(data_state, "validated"):
        table_extract = ui.table(
            columns=[], rows=[], pagination={"rowsPerPage": 5}
        ).classes("max-w-screen-lg  overflow-x-auto")
        table_extract.on("rowClick", lambda row: select_row(data_state, row))

        with ui.row().classes("flex flex-row w-full"):
            with ui.scroll_area().classes("flex-1 overflow-x-auto border"):
                content_orig = ui.markdown("**Contenu original :**")
            with ui.scroll_area().classes("flex-1 overflow-x-auto border"):
                content_extract = ui.markdown("**Extrait des idées principales :**")
        with ui.row():
            ui.button("Extraction", on_click=query_llm)
            spinner = ui.spinner(size="lg").bind_visibility(LLM_STATE, "on_going")
            ui.markdown("LLM model:")
            radio_llm = ui.radio(
                ["local", "GPT-3.5 Turbo", "GPT-4 Turbo"], value="local"
            ).props("inline")
