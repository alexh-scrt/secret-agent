# SecretChain Studio UI

A Gradio-based user interface for the SecretChain AI + Blockchain agent platform.

## Overview

SecretChain Studio provides two interaction modes:

1. **Guided Wizard Mode** - A step-by-step wizard for blockchain investigations
2. **Expert Ops Mode** - A powerful dashboard with chat interface and live context visualization

## Features

### Guided Wizard Mode

A 5-step guided workflow for blockchain investigations:

1. **Define Goal** - Specify your investigation objective
2. **Select Scope** - Choose data sources (On-chain, Graph DB, Knowledge Base, etc.)
3. **Choose Operations** - Review AI-generated investigation plan
4. **Review & Execute** - Execute the plan with safety checks
5. **Explanation & Export** - View results and export reports

### Expert Ops Mode

Advanced interface with:

- **Status Dashboard** - Real-time blockchain, MCP server, and index status
- **Expert Chat** - AI-powered chat with streaming responses
- **Context Panel** - Multi-tab visualization (Graph, Transaction, KB, Logs)
- **Blockchain Operations** - Direct read/write blockchain interactions

## Design System

### Theme

- **Primary Color**: Teal (#14F4C9) - Brand color for Secret AI
- **Secondary Color**: Violet (#8A5DFF) - AI/Agent accent
- **Background**: Deep dark (#050716) - "Secure data center at 2 AM" vibe
- **Typography**:
  - Headings: Space Grotesk
  - Body: Inter
  - Code: JetBrains Mono

### Visual Style

The UI follows a dark, futuristic theme inspired by Secret Network's privacy-focused approach, with:
- Dark backgrounds with subtle gradients
- Teal and violet accent colors
- Clean, modern typography
- Card-based layouts with hover effects

## Running the UI

### Prerequisites

```bash
pip install gradio
```

### Launch

```bash
python src/ui/app.py
```

The app will be available at: **http://localhost:7860**

### Configuration

The app runs with the following default settings:

- **Host**: 0.0.0.0 (accessible from network)
- **Port**: 7860
- **Share**: False (set to True for public link)

To change these, modify the `demo.launch()` call in `app.py`:

```python
demo.launch(
    server_name="0.0.0.0",  # Change host
    server_port=7860,        # Change port
    share=True               # Create public link
)
```

## Current Status

**This is a UI mockup** - it demonstrates the design and user flow but does not yet integrate with the MCP server or actual blockchain tools.

### What Works

- ✅ Full UI layout and theming
- ✅ Mode switching (Wizard ↔ Expert)
- ✅ Wizard step navigation
- ✅ Chat interface with streaming
- ✅ Context panel tabs
- ✅ Blockchain operations panel
- ✅ Placeholder data and responses

### What's Next

- [ ] Integrate with MCP server
- [ ] Connect to Neo4j graph database
- [ ] Connect to Chroma knowledge base
- [ ] Connect to blockchain SDK
- [ ] Implement actual tool calls
- [ ] Add real-time data updates
- [ ] Add graph visualization (D3.js/Cytoscape)
- [ ] Add transaction decoder
- [ ] Add export functionality (PDF/JSON)
- [ ] Add voice input (STT)

## File Structure

```
src/ui/
├── app.py          # Main Gradio application
└── README.md       # This file
```

## Design Documentation

See the `design/UI/` folder for complete design specifications:

- **design.md** - ASCII mockups and layout specifications
- **diagrams.md** - Mermaid flow diagrams and state machines
- **theme.md** - Complete color system and typography guide

## Development

### Adding New Features

1. Follow the existing component structure
2. Use the defined color variables in CSS
3. Match the visual style (dark theme, rounded corners, subtle shadows)
4. Test both Guided Wizard and Expert Ops modes

### Styling Guidelines

- Use CSS variables defined in `CUSTOM_CSS`
- Apply `elem_id` for specific component styling
- Use `!important` sparingly (only for Gradio overrides)
- Keep borders subtle (#252B3F)
- Use teal (#14F4C9) for primary actions
- Use violet (#8A5DFF) for secondary/AI features

### Best Practices

- Keep functions focused and well-documented
- Use descriptive variable names
- Add comments for complex logic
- Test both modes when making changes
- Maintain consistent spacing and formatting

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Change port in app.py or kill existing process
lsof -ti:7860 | xargs kill -9
```

**Import errors:**
```bash
# Ensure Gradio is installed
pip install --upgrade gradio
```

**Theme not applying:**
- Check browser console for CSS errors
- Clear browser cache
- Verify custom CSS is loaded in `gr.Blocks(css=CUSTOM_CSS)`

## Credits

- Design inspired by Secret Network's privacy-first approach
- UI framework: Gradio
- Fonts: Google Fonts (Inter, Space Grotesk, JetBrains Mono)

## License

Part of the secret-agent project.
