import time
import gradio as gr
from gradio.themes.utils import colors, fonts

# -------------------------------------------------------------------
# Theme Configuration (from theme.md)
# -------------------------------------------------------------------

secretai_theme = gr.themes.Base(
    primary_hue=colors.teal,
    secondary_hue=colors.violet,
    font=fonts.GoogleFont("Inter"),
    font_mono=fonts.GoogleFont("JetBrains Mono"),
)

# Custom CSS for enhanced styling
CUSTOM_CSS = """
/* ========== GLOBAL STYLES ========== */
:root {
  --font-heading: "Space Grotesk", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-body: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;

  /* Colors from theme.md */
  --primary: #14F4C9;
  --primary-soft: #11C9A5;
  --secondary: #8A5DFF;
  --accent-cyan: #38BDF8;
  --bg-base: #050716;
  --bg-elevated: #0B1021;
  --bg-hover: #141A2C;
  --border-subtle: #252B3F;
  --text-primary: #F5F7FF;
  --text-secondary: #A7B1D2;
  --success: #22C55E;
  --warning: #FACC15;
  --error: #F97373;
}

/* Apply dark background globally */
body, .gradio-container {
  background: #050716 !important;
  color: #F5F7FF !important;
}

/* Block styling */
.gr-block, .gr-box, .gr-form, .gr-input {
  background: #0B1021 !important;
  border-color: #252B3F !important;
  border-radius: 12px !important;
}

/* Input fields */
textarea, input[type="text"], .gr-text-input {
  background: #0B1021 !important;
  border: 1px solid #333A52 !important;
  color: #F5F7FF !important;
  border-radius: 8px !important;
}

textarea:focus, input[type="text"]:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 2px rgba(20, 244, 201, 0.2) !important;
}

/* Headings */
h1, h2, h3, h4, .prose h1, .prose h2, .prose h3 {
  font-family: var(--font-heading);
  letter-spacing: 0.01em;
  font-weight: 600;
}

/* ========== CHAT STYLING ========== */
.gr-chatbot .message.user {
  background: #11172A !important;
  border-radius: 16px !important;
  border: 1px solid #252B3F !important;
  padding: 12px 16px !important;
}

.gr-chatbot .message.bot {
  background: #0B1021 !important;
  border-left: 3px solid #11C9A5 !important;
  border-radius: 16px !important;
  padding: 12px 16px !important;
}

/* ========== WIZARD STEP SIDEBAR ========== */
#wizard-steps-md {
  background: linear-gradient(135deg, #0B1021 0%, #050716 100%) !important;
  border-radius: 16px !important;
  border: 1px solid #252B3F !important;
  padding: 20px !important;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
}

#wizard-steps-md h3 {
  color: var(--primary);
  margin-bottom: 16px;
  font-size: 1.1em;
}

#wizard-steps-md ul {
  list-style: none;
  padding-left: 0;
}

#wizard-steps-md li {
  padding: 8px 0;
  color: var(--text-secondary);
  transition: color 0.2s;
}

#wizard-steps-md li strong {
  color: var(--primary);
  font-weight: 600;
}

/* ========== WIZARD STEP INDICATOR ========== */
#wizard-step-indicator {
  background: linear-gradient(90deg, rgba(20, 244, 201, 0.1) 0%, rgba(138, 93, 255, 0.1) 100%);
  border-left: 3px solid var(--primary);
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-family: var(--font-heading);
}

/* ========== DASHBOARD CARDS ========== */
#card-latest-block, #card-mcp-health, #card-index-status, #card-alerts {
  background: radial-gradient(circle at top left, #141A2C 0%, #0B1021 70%) !important;
  border-radius: 16px !important;
  border: 1px solid #252B3F !important;
  padding: 20px !important;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

#card-latest-block:hover, #card-mcp-health:hover, #card-index-status:hover, #card-alerts:hover {
  border-color: #333A52;
  box-shadow: 0 4px 12px rgba(20, 244, 201, 0.1);
  transform: translateY(-2px);
}

#card-latest-block h4, #card-mcp-health h4, #card-index-status h4, #card-alerts h4 {
  color: var(--primary);
  margin-bottom: 12px;
  font-family: var(--font-heading);
}

#card-mcp-health strong {
  color: var(--success);
}

/* ========== MODE TOGGLE AREA ========== */
.app-header {
  background: linear-gradient(135deg, #14F4C9 0%, #8A5DFF 50%, #38BDF8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 16px;
}

/* ========== CONTEXT PANEL TABS ========== */
.gr-tab-nav button[aria-selected="true"] {
  border-bottom: 2px solid #14F4C9 !important;
  color: #F5F7FF !important;
  font-weight: 600;
}

.gr-tab-nav button {
  color: #A7B1D2;
  transition: all 0.2s;
}

.gr-tab-nav button:hover {
  color: #F5F7FF;
}

/* ========== ACCORDION STYLING ========== */
.gr-accordion {
  background: #0B1021 !important;
  border: 1px solid #252B3F !important;
  border-radius: 12px !important;
}

.gr-accordion-header {
  background: #141A2C !important;
  border-radius: 12px 12px 0 0 !important;
  font-family: var(--font-heading);
  color: var(--primary) !important;
}

/* ========== BUTTONS ========== */
button {
  font-family: var(--font-body);
  font-weight: 500;
  transition: all 0.2s ease;
}

button.primary {
  box-shadow: 0 0 20px rgba(20, 244, 201, 0.3);
}

button.primary:hover {
  box-shadow: 0 0 25px rgba(20, 244, 201, 0.5);
}

button.secondary:hover {
  border-color: var(--primary);
}

/* ========== TEXTBOX & INPUT STYLING ========== */
textarea, input {
  font-family: var(--font-body);
  color: var(--text-primary) !important;
}

textarea::placeholder, input::placeholder {
  color: #6F7695;
}

/* ========== CHECKBOXES ========== */
.gr-checkbox-group label {
  color: var(--text-primary);
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.2s;
}

.gr-checkbox-group label:hover {
  background: var(--bg-hover);
}

/* ========== SPECIAL ELEMENTS ========== */
#read-md, #write-md {
  background: #0B1021;
  border-radius: 8px;
  padding: 12px;
  border-left: 3px solid var(--accent-cyan);
  min-height: 60px;
}

#context-summary {
  background: linear-gradient(135deg, rgba(20, 244, 201, 0.05) 0%, rgba(138, 93, 255, 0.05) 100%);
  border-radius: 8px;
  padding: 12px;
  margin-top: 12px;
  border: 1px solid #252B3F;
}

/* ========== WIZARD BOTTOM NAV ========== */
#wizard-status-md {
  text-align: center;
  color: var(--text-secondary);
  font-family: var(--font-heading);
  padding: 8px;
}

/* ========== CODE/MONOSPACE ELEMENTS ========== */
code, pre {
  font-family: var(--font-mono);
  background: #050716;
  border-radius: 4px;
  padding: 2px 6px;
  color: var(--primary);
}

/* ========== SCROLLBARS ========== */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #050716;
}

::-webkit-scrollbar-thumb {
  background: #252B3F;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #333A52;
}

/* ========== GRADIO OVERRIDES ========== */
.gradio-container {
  font-family: var(--font-body) !important;
}

.gr-button-primary {
  background: var(--primary) !important;
  border: none !important;
  color: #050716 !important;
  font-weight: 600 !important;
}

.gr-button-secondary {
  background: transparent !important;
  border: 1px solid #333A52 !important;
  color: var(--text-primary) !important;
}

.gr-button-secondary:hover {
  background: #141A2C !important;
  border-color: var(--primary) !important;
}

/* ========== RESPONSIVENESS ========== */
@media (max-width: 768px) {
  #wizard-steps-md {
    margin-bottom: 20px;
  }

  #card-latest-block, #card-mcp-health, #card-index-status, #card-alerts {
    margin-bottom: 12px;
  }
}
"""

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

WIZARD_STEPS = [
    "Define Goal",
    "Select Scope",
    "Choose Operations",
    "Review & Execute",
    "Explanation & Export",
]


def render_step_list(active_idx: int) -> str:
    """Render the left-hand step list markdown with the active step highlighted."""
    lines = ["### Steps"]
    symbols = ["○", "○", "○", "○", "○"]

    for i in range(active_idx):
        symbols[i] = "✓"
    if active_idx < len(symbols):
        symbols[active_idx] = "●"

    for i, name in enumerate(WIZARD_STEPS):
        bullet = f"{symbols[i]} {i+1}. {name}"
        if i == active_idx:
            lines.append(f"- **{bullet}**")
        elif i < active_idx:
            lines.append(f"- ~~{name}~~ ✓")
        else:
            lines.append(f"- {bullet}")
    return "\n".join(lines)


def wizard_nav(step: int, direction: str):
    """Move wizard step forward/back and update which panel is visible."""
    if direction == "next":
        step = min(step + 1, len(WIZARD_STEPS) - 1)
    elif direction == "back":
        step = max(step - 1, 0)

    # Visibility flags for the 5 step panels
    visibilities = [False] * len(WIZARD_STEPS)
    visibilities[step] = True

    step_md = render_step_list(step)
    step_indicator = f"**Step {step+1} of {len(WIZARD_STEPS)} – {WIZARD_STEPS[step]}**"

    return (
        step,  # state
        step_md,
        step_indicator,
        *[gr.update(visible=v) for v in visibilities],
    )


def expert_chat_stream(chat_history, user_msg):
    """Very simple streaming stub for Expert mode chat."""
    if not user_msg:
        yield chat_history, gr.update(value=""), "### Context View\nSelect a tab to view context details."
        return

    # Append user message
    chat_history = chat_history + [[user_msg, ""]]
    assistant_idx = len(chat_history) - 1

    # Fake "thinking"/streaming content
    full_reply = (
        "🔍 **Analysis initiated...**\n\n"
        "I'm analyzing your request using available tools:\n"
        "- 📊 **Graph Query**: Checking entity relationships in Neo4j\n"
        "- ⛓️ **Blockchain SDK**: Fetching on-chain data\n"
        "- 📚 **Knowledge Base**: Searching Chroma for relevant docs\n\n"
        "**Preliminary findings:**\n"
        "• Found 3 related entities in the graph\n"
        "• Transaction volume indicates normal activity\n"
        "• Contract metadata retrieved successfully\n\n"
        "_This is a placeholder response. In production, actual MCP tools would be called._"
    )

    streamed = ""
    for token in full_reply.split(" "):
        streamed += token + " "
        chat_history[assistant_idx][1] = streamed
        # Context panel summary (stub)
        context_md = (
            "### 📊 Live Context Update\n\n"
            "**Last Query Results:**\n"
            "- **Type**: Graph + Blockchain Analysis\n"
            "- **Entities Found**: 3 nodes, 5 relationships\n"
            "- **Status**: ✓ Complete\n\n"
            "**Quick Stats:**\n"
            "- Neo4j Query Time: ~45ms\n"
            "- SDK Calls: 2 successful\n"
            "- KB Chunks Retrieved: 7 relevant documents\n\n"
            "_Switch tabs above to view detailed visualizations._"
        )
        yield chat_history, gr.update(value=""), context_md
        time.sleep(0.05)


def guided_mini_chat(chat_history, user_msg):
    """Tiny helper for the mini chat in Guided mode (non-streaming)."""
    if not user_msg:
        return chat_history, ""
    # Echo-style helper
    reply = (
        f"💡 **Wizard Helper**: Great question about '{user_msg[:30]}...'!\n\n"
        "I'm here to help you navigate the wizard. "
        "In a full implementation, I'd provide contextual help based on your current step and question."
    )
    chat_history = chat_history + [[user_msg, reply]]
    return chat_history, ""


def toggle_mode(mode):
    """Switch between Guided Wizard and Expert Ops containers."""
    guided_visible = mode == "Guided Wizard"
    expert_visible = mode == "Expert Ops Mode"
    return (
        gr.update(visible=guided_visible),
        gr.update(visible=expert_visible),
    )


def dummy_read_op(network, wallet):
    """Placeholder for a read operation in the ops drawer."""
    return (
        f"✅ **READ Operation Complete**\n\n"
        f"**Network**: {network}\n"
        f"**Wallet**: {wallet}\n\n"
        f"**Results** (simulated):\n"
        f"- Balance: 1.2345 ETH\n"
        f"- Nonce: 42\n"
        f"- Last Activity: 2 hours ago\n\n"
        f"_In production, this would call the actual blockchain SDK._"
    )


def dummy_write_op(network, wallet):
    """Placeholder for a write operation (with confirmation) in the ops drawer."""
    return (
        f"⚠️ **WRITE Operation Preview**\n\n"
        f"**Network**: {network}\n"
        f"**From Wallet**: {wallet}\n\n"
        f"**Transaction Details** (example):\n"
        f"- To: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb\n"
        f"- Value: 0.1 ETH\n"
        f"- Gas Estimate: ~21,000 gas\n"
        f"- Estimated Cost: ~0.0005 ETH\n\n"
        f"🔐 **In production, you would see a confirmation dialog before signing.**"
    )


# -------------------------------------------------------------------
# Gradio UI
# -------------------------------------------------------------------

with gr.Blocks(
    title="SecretChain Studio",
    fill_height=True,
    theme=secretai_theme,
    css=CUSTOM_CSS
) as demo:

    # Global mode toggle
    with gr.Row():
        gr.Markdown(
            "## ▣ SecretChain Studio — AI + Blockchain Guided Agent",
            elem_classes="app-header"
        )
    with gr.Row():
        mode_radio = gr.Radio(
            ["Guided Wizard", "Expert Ops Mode"],
            value="Guided Wizard",
            label="🎯 Select Mode",
            interactive=True,
            info="Choose how you want to interact with the platform"
        )

    # ------------------------- GUIDED WIZARD -------------------------
    with gr.Group(visible=True) as guided_group:
        wizard_step_state = gr.State(0)

        with gr.Row():
            with gr.Column(scale=1, min_width=220):
                steps_md = gr.Markdown(render_step_list(0), elem_id="wizard-steps-md")

            with gr.Column(scale=3):
                # Step indicator header
                step_indicator_md = gr.Markdown(
                    f"**Step 1 of {len(WIZARD_STEPS)} – {WIZARD_STEPS[0]}**",
                    elem_id="wizard-step-indicator",
                )

                # Per-step content panels
                with gr.Column(visible=True) as step1_panel:
                    gr.Markdown("### 🎯 Step 1 – Define Your Goal")
                    wizard_goal_input = gr.Textbox(
                        label="What would you like to explore today?",
                        lines=4,
                        placeholder="Examples:\n• Investigate address 0x1234...\n• Trace transaction 0xabcd...\n• Analyze contract interactions for UniswapV3\n• Find suspicious patterns in recent transfers",
                        info="You can paste addresses, tx hashes, contract names, or describe your investigation in natural language"
                    )
                    gr.Markdown(
                        "> 💡 **Tip**: The more specific your goal, the better I can plan the investigation. "
                        "In production, this goal drives the entire MCP tool selection process."
                    )

                with gr.Column(visible=False) as step2_panel:
                    gr.Markdown("### 🔍 Step 2 – Select Data Scope")
                    gr.Markdown(
                        "Enable the data sources you want the AI to use for this investigation. "
                        "Each source provides different capabilities:"
                    )
                    wizard_scope = gr.CheckboxGroup(
                        choices=[
                            "⛓️ On-chain Data (Blockchain SDK) - Real-time blockchain queries",
                            "🕸️ Entity Graph (Neo4j) - Relationship mapping and pattern detection",
                            "📚 Knowledge Base (Chroma) - Contract metadata and documentation",
                            "📡 Live Node Monitoring - Real-time network activity",
                            "🧪 AI Simulation Tools - Transaction simulation and testing",
                        ],
                        value=[
                            "⛓️ On-chain Data (Blockchain SDK) - Real-time blockchain queries",
                            "🕸️ Entity Graph (Neo4j) - Relationship mapping and pattern detection",
                            "📚 Knowledge Base (Chroma) - Contract metadata and documentation",
                        ],
                        label="Data Sources",
                        info="Selected sources will be used to build your investigation plan"
                    )
                    gr.Markdown(
                        "> 🔧 **Under the hood**: These selections map to specific MCP server capabilities "
                        "and determine which tools the AI agent can use."
                    )

                with gr.Column(visible=False) as step3_panel:
                    gr.Markdown("### 🤖 Step 3 – AI-Proposed Operations Plan")
                    gr.Markdown(
                        "Based on your goal and selected data sources, here's the recommended investigation plan:"
                    )
                    gr.Markdown(
                        """
**Proposed Operations:**

1. **➤ Graph Query**: Find path between entities A ↔ B
   - Tool: `neo4j.cypher_query`
   - Estimated time: ~2-5 seconds

2. **➤ Transaction Lookup**: Pull ERC-20 transfers for target address
   - Tool: `blockchain_sdk.get_transfers`
   - Estimated time: ~1-3 seconds

3. **➤ Knowledge Base Search**: Retrieve contract metadata and documentation
   - Tool: `chroma.semantic_search`
   - Query: "contract verification and metadata"
   - Estimated time: ~500ms

4. **➤ Risk Scoring**: Evaluate entity behavior patterns
   - Tool: `risk_analyzer.score_entity`
   - Includes: transaction volume, frequency, known flags
   - Estimated time: ~1 second

**Total Estimated Time**: 5-10 seconds

**Safety Check**: ✅ All operations are read-only, no write transactions involved.
                        """
                    )
                    with gr.Row():
                        gr.Button("🔧 Customize Plan", variant="secondary", scale=1)
                        gr.Button("✅ Accept Plan", variant="primary", scale=1)

                with gr.Column(visible=False) as step4_panel:
                    gr.Markdown("### ⚡ Step 4 – Review & Execute")
                    gr.Markdown(
                        "**Ready to run your investigation plan**. Here's what will happen:"
                    )
                    gr.Markdown(
                        """
**Execution Plan Summary:**

```python
# Step 1: Graph Query
neo4j.cypher_query(
    query="MATCH (a)-[*..3]->(b) WHERE a.address='0x...' RETURN path"
)

# Step 2: Blockchain Query
blockchain_sdk.get_transfers(
    address="0x...",
    token_type="ERC20",
    limit=100
)

# Step 3: Knowledge Base Lookup
chroma.semantic_search(
    query="contract metadata verification",
    n_results=5
)

# Step 4: Risk Analysis
risk_analyzer.score_entity(
    address="0x...",
    include_history=True
)
```

**Security & Safety:**
- ✅ No private keys required
- ✅ Read-only operations
- ✅ No transactions will be signed
- ✅ All data requests are logged

**Resource Usage:**
- Estimated API calls: ~4-6 requests
- Estimated tokens: ~2,000 tokens
- Estimated cost: ~$0.02
                        """
                    )
                    gr.Button("🚀 Run Plan", variant="primary", size="lg")

                with gr.Column(visible=False) as step5_panel:
                    gr.Markdown("### 📊 Step 5 – Explanation & Export")
                    gr.Markdown(
                        "**Investigation Complete!** Here's what we found:"
                    )
                    gr.Markdown(
                        """
#### 🔍 Analysis Results

**Graph Analysis:**
- ✓ Found 3-hop path between addresses A and B
- ✓ Intermediate entities: 0x1234..., 0x5678...
- ⚠️ Entity 0x5678... flagged in 2 previous investigations

**Transaction Analysis:**
- ✓ Retrieved 87 ERC-20 transfers in last 30 days
- ✓ Total volume: ~$125,000 USD equivalent
- ⚠️ Transaction volume spike detected on 2025-11-10 (+340% above average)
- ✓ Gas usage patterns: Normal

**Contract Metadata:**
- ✓ Contract verified on Etherscan
- ✓ Contract type: Proxy (EIP-1967)
- ✓ Implementation: 0x9abc...
- ℹ️ Proxy pattern suggests upgradability - review implementation changes

**Risk Assessment:**
- **Overall Risk Score**: 6.2/10 (Medium)
- **Flags**: Volume spike, connection to flagged entity
- **Recommendations**:
  - Monitor for continued unusual volume
  - Review proxy implementation updates
  - Cross-reference flagged intermediary entity

---

#### 📁 Export Options

Export this analysis in your preferred format:
                        """
                    )
                    with gr.Row():
                        gr.Button("📄 Export as PDF", variant="secondary")
                        gr.Button("💾 Export as JSON", variant="secondary")
                        gr.Button("📋 Copy to Clipboard", variant="secondary")

                    gr.Markdown(
                        """
---

> 🔄 **Start New Investigation**: Click "Next" to begin a new investigation with your learnings from this one.
                        """
                    )

                # Mini-chat on the right side of wizard main block
                with gr.Accordion("💬 Mini Chat (Wizard Sidekick)", open=False):
                    gr.Markdown(
                        "_Ask quick questions while going through the wizard. "
                        "I can clarify terms, explain options, or help you refine your investigation._"
                    )
                    mini_chatbot = gr.Chatbot(
                        label="Wizard Helper",
                        height=200,
                        type="tuples",
                    )
                    mini_input = gr.Textbox(
                        label="Ask a question",
                        placeholder="e.g., What does 'entity graph' mean? How do I investigate a contract?",
                    )
                    mini_send = gr.Button("Send", variant="primary", size="sm")

        # Wizard bottom navigation
        gr.Markdown("---")
        with gr.Row():
            back_btn = gr.Button("◀ Back", variant="secondary", scale=1)
            with gr.Column(scale=2):
                step_status_md = gr.Markdown(
                    "Step 1 of 5 – Define Goal", elem_id="wizard-status-md"
                )
            next_btn = gr.Button("Next ▶", variant="primary", scale=1)

        # ---------- Guided wizard callbacks ----------
        back_btn.click(
            fn=lambda step: wizard_nav(step, "back"),
            inputs=wizard_step_state,
            outputs=[
                wizard_step_state,
                steps_md,
                step_status_md,
                step1_panel,
                step2_panel,
                step3_panel,
                step4_panel,
                step5_panel,
            ],
        )

        next_btn.click(
            fn=lambda step: wizard_nav(step, "next"),
            inputs=wizard_step_state,
            outputs=[
                wizard_step_state,
                steps_md,
                step_status_md,
                step1_panel,
                step2_panel,
                step3_panel,
                step4_panel,
                step5_panel,
            ],
        )

        mini_send.click(
            fn=guided_mini_chat,
            inputs=[mini_chatbot, mini_input],
            outputs=[mini_chatbot, mini_input],
        )

    # ------------------------- EXPERT OPS MODE -------------------------
    with gr.Group(visible=False) as expert_group:
        gr.Markdown("### 📊 System Status Dashboard")

        # Dashboard
        with gr.Row():
            latest_block_card = gr.Markdown(
                """#### ⛓️ Latest Block

**Block Number**: `#19,223,491`
**Gas Price**: `22 gwei`
**Block Time**: `14s ago`
**Status**: ✅ Synced
                """,
                elem_id="card-latest-block",
            )
            mcp_health_card = gr.Markdown(
                """#### 🏥 MCP Server Health

**Status**: **● Healthy**
**Latency**: `~120 ms`
**Tools Available**: `18/18`
**Last Check**: `5s ago`
                """,
                elem_id="card-mcp-health",
            )
            index_status_card = gr.Markdown(
                """#### 🗂️ Index Status

**Graph DB**: ✓ Synced
**Entities**: `1.2M nodes`
**Relationships**: `3.4M edges`
**KB Embeddings**: `452k docs`
                """,
                elem_id="card-index-status",
            )
            alerts_card = gr.Markdown(
                """#### 🔔 Alerts

✅ No critical alerts
ℹ️ 2 info-level notices:
- Index refresh in 2h
- API rate limit: 85%
                """,
                elem_id="card-alerts",
            )

        gr.Markdown("---")

        # Main split area: Chat + Context panel
        with gr.Row():
            # Chat area
            with gr.Column(scale=3):
                gr.Markdown("### 💬 Expert Chat")
                expert_chatbot = gr.Chatbot(
                    label="Expert Agent",
                    height=400,
                    show_label=False,
                    avatar_images=(None, "🤖"),
                    type="tuples",
                )
                expert_input = gr.Textbox(
                    label="Ask anything",
                    placeholder="e.g., Investigate address 0x1234... across graph + KB, or trace suspicious transactions",
                    lines=2,
                )
                with gr.Row():
                    expert_mic_btn = gr.Button("🎙️ Voice Input (STT)", variant="secondary", scale=1)
                    expert_send_btn = gr.Button("Send", variant="primary", scale=2)

            # Context panel
            with gr.Column(scale=3):
                gr.Markdown("### 📊 Context Visualization Panel")
                gr.Markdown("_This panel automatically updates based on the latest query results_")

                context_tabs = gr.Tabs()

                with context_tabs:
                    with gr.Tab("🕸️ Graph"):
                        context_graph_md = gr.Markdown(
                            """
#### Graph View

```
     ┌─────────┐
     │ Node A  │
     │ 0x1234..│
     └────┬────┘
          │ transfers
          ▼
     ┌─────────┐
     │ Node X  │──────► [ Node Y ] ──────► ┌─────────┐
     │ 0x5678..│  swap              call    │ Node B  │
     └─────────┘                            │ 0x9abc..│
                                            └─────────┘
```

**Graph Statistics:**
- Nodes visible: 4
- Relationships: 3
- Shortest path length: 3 hops
- Risk nodes: 1 (Node X)

_In production, this would be an interactive D3.js or Cytoscape visualization._
                            """,
                            elem_id="context-graph-md",
                        )

                    with gr.Tab("⛓️ Transaction"):
                        context_tx_md = gr.Markdown(
                            """
#### Transaction Details

**Latest Analyzed TX**: `0xabcd1234...`

| Field | Value |
|-------|-------|
| **Block** | #19,223,445 |
| **From** | `0x1234...5678` |
| **To** | `0x9abc...def0` |
| **Value** | 1.5 ETH |
| **Gas Used** | 21,000 / 50,000 |
| **Status** | ✅ Success |

**Decoded Logs:**
```
Transfer(
  from: 0x1234...5678,
  to: 0x9abc...def0,
  value: 1500000000000000000
)
```

**Internal Traces:** 2 internal calls detected
**ERC-20 Transfers:** 3 token movements

_Full transaction decoder and trace viewer would appear here._
                            """,
                            elem_id="context-tx-md",
                        )

                    with gr.Tab("📚 KB"):
                        context_kb_md = gr.Markdown(
                            """
#### Knowledge Base Results

**Query**: "contract proxy pattern verification"
**Retrieved**: 5 relevant documents

---

**1. EIP-1967: Proxy Storage Slots** (relevance: 0.94)
> Standard proxy contract pattern that uses specific storage slots for upgradability...

**2. Proxy Contract Security Best Practices** (relevance: 0.89)
> When implementing upgradeable contracts, ensure proper access controls on upgrade functions...

**3. OpenZeppelin TransparentUpgradeableProxy** (relevance: 0.87)
> Implementation details and security considerations for transparent proxy pattern...

**4. Proxy Pattern Vulnerabilities** (relevance: 0.82)
> Common vulnerabilities in proxy contracts include storage collisions, function selector clashes...

**5. Contract Verification Guide** (relevance: 0.78)
> Steps to verify proxy contracts on block explorers and ensure implementation matches...

---

_Semantic search powered by Chroma vector database._
                            """,
                            elem_id="context-kb-md",
                        )

                    with gr.Tab("📜 Logs"):
                        context_logs_md = gr.Markdown(
                            """
#### MCP Tool Execution Logs

```log
[2025-11-14 10:23:45] INFO: Query initiated
[2025-11-14 10:23:45] DEBUG: Parsing user intent...
[2025-11-14 10:23:46] INFO: Selected tools: neo4j_query, blockchain_sdk, chroma_search
[2025-11-14 10:23:46] DEBUG: Executing neo4j.cypher_query
[2025-11-14 10:23:47] SUCCESS: Neo4j query completed (1.2s, 4 nodes returned)
[2025-11-14 10:23:47] DEBUG: Executing blockchain_sdk.get_transfers
[2025-11-14 10:23:49] SUCCESS: Retrieved 87 transfers (2.1s)
[2025-11-14 10:23:49] DEBUG: Executing chroma.semantic_search
[2025-11-14 10:23:50] SUCCESS: Found 5 relevant docs (0.8s)
[2025-11-14 10:23:50] INFO: Generating response...
[2025-11-14 10:23:52] COMPLETE: Total execution time: 6.4s
```

**Performance Metrics:**
- Total MCP calls: 3
- Avg latency: 1.37s per call
- Success rate: 100%
- Tokens used: ~2,100

_Real-time tool execution monitoring and debugging._
                            """,
                            elem_id="context-logs-md",
                        )

                # Simple context summary that we update from the chat function
                context_summary_md = gr.Markdown(
                    "### 📊 Live Context Update\n\nAwaiting first query...",
                    elem_id="context-summary"
                )

        # Blockchain ops drawer (use Accordion as a drawer-like element)
        with gr.Accordion("🔧 Blockchain Operations Panel", open=False):
            gr.Markdown(
                "**Direct blockchain operations** - Interact directly with the blockchain "
                "for advanced read/write operations."
            )

            with gr.Row():
                network_dd = gr.Dropdown(
                    ["Mainnet", "Testnet (Sepolia)", "Devnet (Local)"],
                    value="Testnet (Sepolia)",
                    label="Network",
                )
                wallet_tb = gr.Textbox(
                    label="Wallet Address",
                    placeholder="0xABCD... (connected wallet in production)",
                    value="0xABCD1234...demo",
                )
                gas_dd = gr.Dropdown(
                    ["Auto", "Low (10 gwei)", "Medium (25 gwei)", "High (50 gwei)"],
                    value="Auto",
                    label="Gas Setting"
                )

            gr.Markdown("#### 📖 Read Operations (Safe)")
            gr.Markdown("_These operations don't modify blockchain state_")
            with gr.Row():
                read_balance_btn = gr.Button("💰 Get Balance", variant="secondary")
                read_contract_btn = gr.Button("📄 Inspect Contract ABI", variant="secondary")
                read_simulate_btn = gr.Button("🧪 Simulate Call", variant="secondary")
            read_result_md = gr.Markdown("", elem_id="read-md")

            gr.Markdown("---")
            gr.Markdown("#### ✍️ Write Operations (Require Confirmation)")
            gr.Markdown("_⚠️ These operations will modify blockchain state and require gas_")
            with gr.Row():
                write_tx_btn = gr.Button("💸 Send Transaction", variant="secondary")
                write_contract_btn = gr.Button("⚙️ Interact With Contract", variant="secondary")
            write_result_md = gr.Markdown("", elem_id="write-md")

        # ---------- Expert mode callbacks ----------
        expert_send_btn.click(
            fn=expert_chat_stream,
            inputs=[expert_chatbot, expert_input],
            outputs=[expert_chatbot, expert_input, context_summary_md],
        )

        read_balance_btn.click(
            fn=dummy_read_op,
            inputs=[network_dd, wallet_tb],
            outputs=read_result_md,
        )
        read_contract_btn.click(
            fn=dummy_read_op,
            inputs=[network_dd, wallet_tb],
            outputs=read_result_md,
        )
        read_simulate_btn.click(
            fn=dummy_read_op,
            inputs=[network_dd, wallet_tb],
            outputs=read_result_md,
        )
        write_tx_btn.click(
            fn=dummy_write_op,
            inputs=[network_dd, wallet_tb],
            outputs=write_result_md,
        )
        write_contract_btn.click(
            fn=dummy_write_op,
            inputs=[network_dd, wallet_tb],
            outputs=write_result_md,
        )

    # ------------------------- MODE TOGGLE -------------------------
    mode_radio.change(
        fn=toggle_mode,
        inputs=mode_radio,
        outputs=[guided_group, expert_group],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
