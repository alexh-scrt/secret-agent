"""Chat interface - implements the conversational UI."""

import gradio as gr


def create_chat_tab():
    """
    Create the chat interface tab.

    Returns:
        Gradio components for chat tab
    """
    with gr.Column():
        chatbot = gr.Chatbot(label="Secret Agent Chat")
        msg = gr.Textbox(
            label="Message",
            placeholder="Ask me anything about Secret Network...",
        )
        submit = gr.Button("Send")

        # TODO: Wire up chat functionality

    return chatbot, msg, submit
