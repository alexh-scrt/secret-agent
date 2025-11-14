"""Validator table - displays validator information and staking options."""

import gradio as gr


def create_validators_tab():
    """
    Create the validators table tab.

    Returns:
        Gradio components for validators tab
    """
    with gr.Column():
        gr.Markdown("## Validators")

        # TODO: Add validator components
        validators_table = gr.DataFrame(
            headers=["Name", "Commission", "Voting Power", "Status"],
            label="Active Validators",
        )
        refresh_btn = gr.Button("Refresh")

    return validators_table, refresh_btn
