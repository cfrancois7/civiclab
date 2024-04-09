from nicegui import ui, events, app
from io import StringIO
import logging
from pandas import read_csv
from openai import OpenAI, AsyncOpenAI
from pathlib import Path
import tomllib
from .state import State
from .header import add_head_html
from .style import link_target, section_heading
import numpy as np
from pandas import DataFrame, MultiIndex
import plotly.graph_objects as go
import plotly.express as px
import time

COLUMNS = [
    "QUXVlc3Rpb246MTYz - Que faudrait-il faire pour rendre la fiscalité plus juste et plus efficace ?",
    "title",
]

LLM_STATE = State(on_going=False)
LOAD_STATE = State(on_going=False)


##########
# FUNCTION
##########
def load_data(data_state):
    global dropdown_extract_select
    LOAD_STATE.on_going = True

    ui.notify("Data loading")
    path_data = Path("./data/LA_FISCALITE_ET_LES_DEPENSES_PUBLIQUES.csv")
    data_state.validated_data = read_csv(path_data, low_memory=False)
    cols = data_state.validated_data.columns.tolist()
    select_col = cols[0]

    dropdown_extract_select.set_options(["Select a column"] + cols)
    dropdown_stats.set_options(["Select a column"] + cols)

    dropdown_extract_select.update()
    dropdown_stats.update()

    columns = [
        {"name": select_col, "label": select_col, "field": select_col, "align": "left"}
    ]
    table_extract.columns = columns
    table_extract.rows = (
        data_state.validated_data[[select_col]].iloc[:200].dropna().to_dict("records")
    )
    table_extract.update()

    button_contrib.validated = True
    LOAD_STATE.on_going = False


def select_row(state, row):
    selected_row = row.args[1]
    col = dropdown_extract_select.value
    content = selected_row[col]
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


def update_table(data_state):
    global dropdown_extract_select
    select_col = dropdown_extract_select.value
    columns = [
        {
            "name": select_col,
            "label": select_col,
            "field": select_col,
            "align": "left",
        }
    ]
    table_extract.columns = columns
    table_extract.rows = (
        data_state.validated_data.loc[:200, [select_col]].dropna().to_dict("records")
    )
    table_extract.update()

    with table_extract.add_slot("top-left"):

        def toggle() -> None:
            table_extract.toggle_fullscreen()
            button.props(
                "icon=fullscreen_exit"
                if table_extract.is_fullscreen
                else "icon=fullscreen"
            )

        button = ui.button(
            "Toggle fullscreen", icon="fullscreen", on_click=toggle
        ).props("flat")
    logging.info(columns)
    # data_state.refresh_all = True


def update_stats_plot(data_state):
    global fig_stats, plot_stats, fig_price, plot_price
    # STATISTICS
    ## parse data
    data = data_state.validated_data
    col = dropdown_stats.value
    contributions = data.loc[:, col].dropna().values
    words_contribution = [len(c.split(" ")) for c in contributions]
    length_character = [len(c) for c in contributions]
    data_state.stat_text = text_stats_template.format(
        input=str(np.sum(words_contribution))
    )

    # ## reset plot trace
    fig_stats.data = []
    traces = list(
        px.histogram(
            x=np.log10(words_contribution),
            log_y=True,
        ).select_traces()
    )[0]
    fig_stats.add_trace(traces)
    plot_stats.update()

    # PRICE
    model = ["GPT 3.5", "GPT 4"]
    type_price = ["context", "generation"]
    price_context = np.array([0.5, 30]) / 1e6
    price_generation = np.array([1.5, 60]) / 1e6
    length_token = np.sum(np.array(length_character) / 3)
    prices_context = (length_token + 536) * price_context
    prices_generation = length_token * 2 * price_generation

    df_price = (
        DataFrame(
            data=np.concatenate([prices_context, prices_generation]),
            index=MultiIndex.from_product(
                [model, type_price], names=["model", "token type"]
            ),
        )
        .reset_index()
        .melt(id_vars=["model", "token type"])
    )

    ## reset plot trace
    fig_price.data = []
    traces = list(
        px.bar(
            df_price,
            x="model",
            y="value",
            color="token type",
        ).select_traces()
    )
    for trace in traces:
        fig_price.add_trace(trace)

    plot_price.update()


##########
# LAYOUT
##########
@ui.refreshable
def section_extract(data_state):
    add_head_html()
    msg = """Le traitement des contributions d'une consultation publique est chronophage.
    Il est nécessaire d'extraire les idées principales de l'ensemble des
    contributions avant de les regrouper et de leur donner du sens.
    Dans les faits, au fil de l'analyse, les praticiens déterminent une taxonomie
    des idées, c'est à dire détermine les catégories principales auxquelles font référence les contributions. La qualité de 
    cette taxonomie dépend de nombreux facteurs : objectif final de l'analyse,
    temps d'analyse, expérience et compétence du praticien. Si la réalisation d'un taxonomie permet de traiter plus efficacement les
    contributions, elle peut aussi contribuer à effacer une partie de
    l'information en réalisant de trop grandes catégories.
    
L'intelligence artificielle peut contribuer à aider le praticien dans cette tâche.
Infatigable, elle peut extraire les idées principales de 10 ou 10 000 contributions,
puis générer les catégories à partir de l'extraction fidèle de ces idées. L'intelligence
    artificielle en question sont les `Large Language Models` (LLM), tel que `ChatGPT`.
    
Voici ci-dessous un exemple d'application de l'extraction des idées principales.
    Le modèle pour une contribution donné extrait les idées principales, si elles sont
    synthaxiquement négative, et si ce sont des propositions. La sortie du traitement est
    au format JSON afin de faciliter la manipulation à posteriori par d'autres modules à venir.
    """
    ui.markdown(msg).classes("gap-2 bold-links arrow-links text-lg")

    msg = """Attention: Il faut noter que
    la qualité de l'extraction dépend de l'entrainement du modèle. Les modèles testés
    ici n'ont pas été entrainés spécifiquement à la tâche de l'extraction.
    Un jeu de données de référence corrigé est actuellement en cours de création
    pour entrainer les modèles à réaliser les meilleurs extractions."""
    ui.markdown(msg).classes("italic gap-2 bold-links arrow-links text-lg")

    msg = """Attention: Le fichier a charger est relativement lourd (env. 500 Mo). Soyez patient.
    En cas de bug, rafraichir la page."""
    ui.markdown(msg).classes("italic gap-2 bold-links arrow-links text-lg")

    global table_extract, content_orig, content_extract, spinner, radio_llm, button_contrib
    global spinner_load
    # to remove after bug test

    with ui.row():
        button_contrib = ui.button(
            "Load contributions", on_click=lambda e: load_data(data_state)
        )
        button_contrib.validated = False
        spinner_load = ui.spinner(size="lg").bind_visibility(LOAD_STATE, "on_going")

    with ui.column().classes("w-full").bind_visibility(button_contrib, "validated"):
        global dropdown_extract_select
        dropdown_extract_select = ui.select(
            options=["Select a column"],
            value="Select a column",
            on_change=lambda e: update_table(data_state),
        ).classes("text-lg")
        table_extract = ui.table(
            columns=[], rows=[], pagination={"rowsPerPage": 5}
        ).classes("max-w-screen-lg  overflow-x-auto w-full")
        table_extract.on("rowClick", lambda row: select_row(data_state, row))

        with ui.row().classes("flex flex-row w-full"):
            with ui.scroll_area().classes("flex-1 overflow-x-auto border"):
                content_orig = ui.markdown("**Contenu original :**")
            with ui.scroll_area().classes("flex-1 overflow-x-auto border"):
                content_extract = ui.markdown("**Extrait des idées principales :**")
        ## BUTTON EXCTRACTION
        with ui.row():
            ui.button("Extraction", on_click=query_llm)
            spinner = ui.spinner(size="lg").bind_visibility(LLM_STATE, "on_going")
            ui.markdown("LLM model:")
            radio_llm = ui.radio(
                ["GPT-3.5 Turbo", "GPT-4 Turbo"], value="GPT-3.5 Turbo"
            ).props("inline")

        ui.link(target="#prix").classes("center scroll-indicator")

        ## PLOTS AND STATISTICS

        with ui.row().classes(
            """
            py-20 px-8 lg:px-16
            gap-8 sm:gap-16 md:gap-8 lg:gap-16"""
        ).bind_visibility(button_contrib, "validated"):
            link_target("prix")
            with ui.column():
                section_heading("Le prix de l'automatisation", "Des coûts accessibles")

                msg = """
                Les LLM tels que ChatGPT sont aujourd'hui accessible via internet.
                Les coûts ont drastiquement baissés depuis 1 an.
                1 millions de token coûte 0.5 $ pour la lecture, et 1.50 $ pour la génération.
                Et il faut environ 3 tokens pour écrire un mot. Cette baisse de prix et les services associés
                toujours plus facile d'accès permet de démocratiser ce type de solution.
                """
                ui.markdown(msg).classes("gap-2 bold-links arrow-links text-lg")
                global dropdown_stats, text_stats_template
                dropdown_stats = ui.select(
                    options=["Select a column"],
                    value="Select a column",
                    on_change=lambda e: update_stats_plot(data_state),
                ).classes("text-lg max-w-screen-lg")

                text_stats_template = """
                *La figure représente la distribution de la taille des contributions en mot.
                La taille est représentée en logarithme, c'est à dire que 2 vaut 100, 3 vaut 1000, etc...
                
                
                La quantité totale de mot est de : {input}
                """
                data_state.stat_text = text_stats_template.format(input="")
                ui.markdown().bind_content(data_state, "stat_text").classes(
                    "gap-2 bold-links arrow-links text-lg"
                )
                global fig_stats, plot_stats, fig_price, plot_price
                # TODO: TRANSFOR PLOT INTO BAR PLOT WITH PRICE GPT 3.5 and GPT4
                with ui.column():
                    fig_stats = go.Figure()
                    fig_stats.update_layout(
                        # margin=dict(l=0, r=0, t=0, b=0),
                        title_text="""Distribution des taille des contributions en nombre de mot
                        <br>(échelle logarithmique)""",
                        title_font_size=18,
                        xaxis_title="Logarithme 10 (Taille des contributions)",
                        yaxis_title="Occurence",
                    )
                    plot_stats = ui.plotly(fig_stats)

                    fig_price = go.Figure()
                    fig_price.update_layout(
                        # margin=dict(l=0, r=0, t=0, b=0),
                        title_text="""Prix du traitement de la question en $ US""",
                        title_font_size=18,
                        yaxis_title="Total price ($ US)",
                    )
                    plot_price = ui.plotly(fig_price).classes("dark-box")
