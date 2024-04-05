from .header import add_head_html
from nicegui import ui
from .style import link_target, section_heading, subtitle
import logging
from pandas import DataFrame, read_csv
from pathlib import Path
import numpy as np
import plotly.express as px


########
# LAYOUT
########
@ui.refreshable
def section_future():
    add_head_html()
    section_heading(
        "S'interfacer avec l'intelligence artificielle",
        "Les enjeux et les besoins de Perspectiva",
    )
    msg = """A l'heure actuel, *Perspectiva* est au stade du prototype. Les modèles n'ont pas été spécifiquement 
entrainé pour s'ajuster au corpus à traiter. Aussi, l'interfaçage est à peine une ébauche.
Or ces deux éléments sont indispensable pour constituer une plateforme fonctionnelle.

Les enjeux sont de quatre dimensions :

1. assurer l'interopérabilité avec les formats des solutions leaders de la consultation public comme Decidim ou Cap Collectif).

2. naviguer et visualiser simplement dans les données et permettre d'enrichir les données brutes via le traitement assisté par IA.

3. améliorer les modèles d'IA en mettant en place une méthodologie d'adaptation robuste de ces derniers au corpus de la consultation.

4. mettre en place un système de traitement des textes facilement configurable, soit pour utiliser un modèle local
ou un modèle en ligne (sur le cloud).
    """

    ui.markdown(msg).classes("gap-2 bold-links arrow-links text-lg")

    ## SECTION
    subtitle("Les idées des développements à venir")

    with ui.row().classes("flex-col flex-row"):
        with ui.column().classes():
            msg = """Au dela des fonctionnalités actuelles, l'équipe de développeur implémente de nouvelles
            fonctionnalités. En particulier, nous développons un outil pour hiérarchiser les regroupements d'idées.
            En particulier, certaines idées sont liées entre elles, que ce soit part le fait qu'une idée est plus spécifique
            qu'une idée, ou parce que les idées vont de paires dans la majorité des contributions.
            """
            ui.markdown(msg).classes("gap-2 bold-links arrow-links text-lg")

        ui.image("./image/lien_entre_idee.png").classes("w-80")

    ## SECTION
    subtitle("Nos besoins urgents : des développeurs d'interface")

    msg = """
    Actuellement nous sommes une équipe représentant un développeur actif. Si la Data science et la gestion des données sont son métier, la création d'application
    avec interface graphique ne l'est pas. Nous avons besoin de développeur !!
    
    Contactez nous vite : [cyril.francois.87@gmail.com](mailto:cyril.francois.87@gmail.com) 
    """
    ui.markdown(msg).classes("gap-2 bold-links arrow-links text-lg")
