"""Portfolio dashboard - displays user's assets and positions."""

import gradio as gr


def create_portfolio_tab():
    """
    Create the portfolio dashboard tab.

    Returns:
        Gradio components for portfolio tab
    """
    with gr.Column():
        gr.Markdown("## Portfolio Overview")

        # TODO: Add portfolio components
        balance = gr.Textbox(label="Total Balance", value="0 SCRT")
        assets_table = gr.DataFrame(
            headers=["Asset", "Amount", "Value"],
            label="Assets",
        )

    return balance, assets_table
