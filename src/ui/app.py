"""Main Gradio app - creates and configures the web interface."""

import gradio as gr


def create_app():
    """
    Create and configure the Gradio application.

    Returns:
        Gradio Blocks app
    """
    with gr.Blocks() as app:
        gr.Markdown("# Secret Agent")
        gr.Markdown("AI Assistant for Secret Network")

        # TODO: Add tabs and components
        with gr.Tabs():
            with gr.Tab("Chat"):
                gr.Markdown("Chat interface coming soon...")

            with gr.Tab("Portfolio"):
                gr.Markdown("Portfolio dashboard coming soon...")

            with gr.Tab("Validators"):
                gr.Markdown("Validator table coming soon...")

            with gr.Tab("Settings"):
                gr.Markdown("Settings panel coming soon...")

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch()
