from nicegui import ui


def section_heading(subtitle_: str, title_: str) -> None:
    """Render a section heading with a subtitle."""
    ui.label(subtitle_).classes("md:text-lg font-bold")
    ui.markdown(title_).classes("text-3xl md:text-5xl font-medium mt-[-12px] fancy-em")


def link_target(name: str, offset: str = "0") -> ui.link_target:
    """Create a link target that can be linked to with a hash."""
    target = ui.link_target(name).style(f"position: absolute; top: {offset}; left: 0")
    assert target.parent_slot is not None
    target.parent_slot.parent.classes("relative")
    return target


def heading(title_: str) -> ui.markdown:
    """Render a heading."""
    return ui.markdown(title_).classes(
        "text-2xl md:text-3xl xl:text-4xl font-medium text-white"
    )


def title(content: str) -> ui.markdown:
    """Render a title."""
    return ui.markdown(content).classes(
        "text-4xl sm:text-5xl md:text-6xl font-medium fancy-em"
    )


def subtitle(content: str) -> ui.markdown:
    """Render a subtitle."""
    return ui.markdown(content).classes("text-xl sm:text-2xl md:text-3xl leading-7")
