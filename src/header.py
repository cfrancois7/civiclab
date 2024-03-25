from nicegui import ui
from typing import Optional


def add_header(menu: Optional[ui.left_drawer] = None) -> None:
    """Create the page header."""
    menu_items = {"Why?": "/#why", "Load data": "/#load_data", "llm": "/llm"}

    with ui.header().classes("items-center duration-200 p-0 px-4 no-wrap").style(
        "box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1)"
    ):
        if menu:
            ui.button(on_click=menu.toggle, icon="menu").props(
                "flat color=white round"
            ).classes("lg:hidden")

        with ui.row().classes("max-[1050px]:hidden"):
            for title_, target in menu_items.items():
                ui.link(title_, target).classes(replace="text-lg text-white")
