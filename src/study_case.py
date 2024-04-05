from .header import add_head_html
from nicegui import ui
from .style import link_target, section_heading, subtitle
import logging
from pandas import DataFrame, read_csv
from pathlib import Path
import numpy as np
import plotly.express as px


def str_to_np_array(s):
    s = s.strip("[]")
    return np.array([float(x) for x in s.split()])


def transform_df(df):
    return np.vstack(df.apply(str_to_np_array).to_numpy())


########
# LAYOUT
########
@ui.refreshable
def section_study_case():
    add_head_html()
    section_heading("Un retour d'expérience", "L'analyse du Grande Débat National 2019")
    msg = """Un des plus grands exercices de consultation à l'échelle nationale a eu lieu en 2019.
Le Grand Débat National 2019 a représenté au moins 1,5 millions de contributeurs, tant sur internet
que dans des réunions animés localement. L'exercice a coûté environ 12 millions d'euros.

Dans l'étude de cas ci-dessous, nous analyserons les contributions numériques de ce Grand Débat, et parmi elles,
une question en particulier concernant la fiscalité. Ces contributions sont celles disponibles
via la plateforme
[Data.Gouv.fr](https://www.data.gouv.fr/fr/datasets/grand-debat-national-debats/).
Celles-ci ne représentent que les contributions réalisées via internet au travers du site
dédié. Les contributions traités ne contiennent pas les contributions manuscriptes et les cahiers de doléances.
Ces derniers ne sont pas accessibles car non encore numérisés.

L'exercice de l'étude de cas se porte sur la question n°163 du Grand Débat National :

"Que faudrait-il faire pour rendre la fiscalité plus juste et plus efficace"
    """
    ui.markdown(msg).classes("gap-2 bold-links arrow-links text-lg")

    ## SECTION
    subtitle("Les catégories principales d'idées")

    msg = """Le traitement de base que la plateforme se veut de proposer est le regroupement
des idées principales des contributions. Ce traitement s'opère en trois étapes : 

1. A l'aide des *Large Language Model (LLM)* de type *ChatGPT*, les idées principales des
contributions sont extraites.

2. Ces idées extraites sont ensuites traitées par d'autres modèles que l'on
appelle des générateurs d'*embeddings*. Ces derniers sont entraintés à évaluer la similarité entre
des textes écrits. Ainsi, en lui fournissant l'ensemble des contributions, ils rapprochent celles qui
sont les plus similaires.

3. Ensuite, à l'aide d'un dernier modèle, dit de regroupement, l'on forme des groupes. Sur l'image ci-dessous,
environ 200 groupes ont été formés.

La qualité de ces trois étapes dépendent de la qualité des modèles et de leur apprentissage.
Par exemple, les modèles actuels présentent quelques faiblesses. Certains acronymes ne sont pas
bien identifié. Aussi les phrases qui représentent la négation d'un fait sont évaluées comme similaires
avec les phrases qui affirment ce fait. Par exemple: "il faut plus d'impôts" est considérée proche de
"il ne faut plus d'impôt".
L'équipe du projet est train de réaliser un jeux de données de qualité afin d'entrainer les modèles
à mieux formuler les idées principales, sous forme de proposition ou de faits, et de discriminer
les phrases négatives des positives."""

    with ui.column():
        ui.markdown(msg).classes("gap-2 bold-links arrow-links text-lg")
        path_data = Path("./data/data_grand_debat_163.csv")
        df = read_csv(path_data)
        embeddings_2d = transform_df(df.umap_2d)
        color = df.cluster
        hover_data = df.text
        mask = df.cluster != -1
        fig_clusters = px.scatter(
            x=embeddings_2d[mask, 0],
            y=embeddings_2d[mask, 1],
            color=color[mask].astype(str),
            hover_data=hover_data.values[mask].reshape(1, -1),
            color_discrete_sequence=px.colors.qualitative.Alphabet,
        )
        fig_clusters.update_layout(
            title_text="""Représentation 2D des contributions.
            <br>Les idées principales similaires sont proches entre elles. """,
            title_font_size=15,
        )

        plot_stats = ui.plotly(fig_clusters).classes("w-2/3 h-96")
        ui.space()
        ## SECTION
        subtitle("Le point des contributions")

        msg = """
        Le second traitement de base de la plateforme est de définir un nom pour chacun de ces regroupements
        et de déterminer leur poids de représentativité.
        """

        ui.markdown(msg).classes("gap-2 bold-links arrow-links text-lg")

        ui.image("./image/image.png").classes("w-2/3 h-96")
