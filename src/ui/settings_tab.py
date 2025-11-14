"""Settings panel - manages app configuration and preferences."""

import gradio as gr


def create_settings_tab():
    """
    Create the settings panel tab.

    Returns:
        Gradio components for settings tab
    """
    with gr.Column():
        gr.Markdown("## Settings")

        # TODO: Add settings components
        rpc_url = gr.Textbox(
            label="RPC URL",
            value="https://lcd.mainnet.secretsaturn.net",
        )
        chain_id = gr.Textbox(label="Chain ID", value="secret-4")
        wallet_address = gr.Textbox(label="Wallet Address", placeholder="secret1...")

        save_btn = gr.Button("Save Settings")

    return rpc_url, chain_id, wallet_address, save_btn
