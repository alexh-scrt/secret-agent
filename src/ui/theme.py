"""Custom Gradio theme for Secret Agent."""

import gradio as gr


def create_theme():
    """
    Create custom Gradio theme.

    Returns:
        Gradio theme
    """
    # TODO: Customize theme colors and styling
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="gray",
    )

    return theme
