Theme that feels “Secret AI / Secret VMs”: dark, mysterious, neon-teal privacy vibes with a subtle violet accent, plus clean modern type.


1. **Visual direction**
2. **Color system (hex values + roles)**
3. **Typography stack**
4. **How to apply it in your Gradio app (code snippet)**

---

## 1. Visual Direction (SecretAI-style)

* **Overall**: Deep, almost-black background, with **teal + cyan glows** and a **violet accent**.
* **Mood**: Confidential, futuristic, but not “gamer RGB”; more “secure data center at 2 AM”.
* **Usage**:

  * Teal = your **brand / primary** (Secret AI, secure, encrypted).
  * Violet = your **secondary / accent** (AI, agents, “homunculus brain”).
  * Neutral blues/gray for surfaces; bright colors reserved for state (success/warn/error).

---

## 2. Color System

### Core Brand Colors

**Primary (Teal / Secret Glow)**

* `PRIMARY`: `#14F4C9` – bright neon teal
* `PRIMARY_SOFT`: `#11C9A5` – slightly muted teal for large fills
* `PRIMARY_DARK`: `#0C8F79`

Use for:

* Primary buttons (Send, Run Plan, Confirm)
* Active mode toggle
* Links and key highlights (e.g., address chips)

---

**Secondary (Violet / AI Aura)**

* `SECONDARY`: `#8A5DFF` – electric violet
* `SECONDARY_SOFT`: `#6B4AE0`
* `SECONDARY_DARK`: `#4F36B5`

Use for:

* Secondary buttons (e.g., “Customize Plan”)
* Wizard step highlights / progress
* AI-related decorative elements (gradients, borders)

---

**Accent / Gradient**

* `ACCENT_CYAN`: `#38BDF8` – cyan for data/graph nodes
* **Brand Gradient**:
  `BRAND_GRADIENT = linear-gradient(135deg, #14F4C9 0%, #8A5DFF 50%, #38BDF8 100%)`

Use for:

* Hero banners (top of app), status dashboard strip
* Graph highlights (selected node/edge)
* Active tab indicator underline

---

### Backgrounds & Surfaces

* `BG_BASE`: `#050716` – full app background
* `BG_ELEVATED`: `#0B1021` – cards, panels
* `BG_HOVER`: `#141A2C` – hover on cards/buttons
* `BG_CHIP`: `#1B2236` – small badges/chips

Use pattern:

* Body: `BG_BASE`
* Cards (wizard panel, dashboard cards, chat bubbles): `BG_ELEVATED`
* Press/hover: `BG_HOVER`

---

### Borders & Dividers

* `BORDER_SUBTLE`: `#252B3F`
* `BORDER_STRONG`: `#333A52`

Use:

* Card outlines, panel separators
* Wizard step separator line
* Context panel tab borders

---

### Text Colors

* `TEXT_PRIMARY`: `#F5F7FF` – main text
* `TEXT_SECONDARY`: `#A7B1D2` – labels, descriptions
* `TEXT_MUTED`: `#6F7695` – helper text
* `TEXT_INVERTED`: `#050716` – on primary buttons

Use:

* Chat text: `TEXT_PRIMARY`
* Wizard explanatory text: `TEXT_SECONDARY`
* Tiny hints / tooltips: `TEXT_MUTED`

---

### Status Colors (Semantic)

* `SUCCESS`: `#22C55E`
* `SUCCESS_BG`: `#082F1A`
* `WARNING`: `#FACC15`
* `WARNING_BG`: `#2E2808`
* `ERROR`: `#F97373`
* `ERROR_BG`: `#3B1010`
* `INFO`: `#38BDF8`
* `INFO_BG`: `#062638`

Use:

* MCP health pill: `SUCCESS` text on `SUCCESS_BG` chip
* “Write TX” warnings: `WARNING` with `WARNING_BG` and border
* Errors in logs / failed calls: `ERROR` with `ERROR_BG`
* Informational badges (“Read-only”, “Simulated”): `INFO`

---

### Component-Level Mapping

**Chat (Expert mode)**

* Chat background: `BG_ELEVATED`
* User bubble:

  * Background: `#11172A`
  * Text: `TEXT_PRIMARY`
* Assistant bubble:

  * Background: `#0B1021`
  * Left border: `PRIMARY_SOFT`
  * Text: `TEXT_PRIMARY`

**Wizard steps**

* Active step bullet / number: `PRIMARY`
* Completed steps: `SECONDARY_SOFT`
* Inactive steps: `TEXT_MUTED`
* Step connector line: `BORDER_SUBTLE`

**Dashboard cards**

* Card background: `BG_ELEVATED`
* Card border: `BORDER_SUBTLE`
* Card title: `TEXT_SECONDARY`
* Key metrics (block number, latency): `TEXT_PRIMARY` with small `ACCENT_CYAN` icon
* Danger/alert card: border left strip `WARNING` or `ERROR`

**Buttons**

* Primary:

  * BG: `PRIMARY`
  * Text: `TEXT_INVERTED`
  * Hover: `PRIMARY_SOFT`
* Secondary:

  * BG: transparent
  * Border: `BORDER_STRONG`
  * Text: `TEXT_PRIMARY`
  * Hover BG: `BG_HOVER`
* Destructive:

  * BG: `ERROR`
  * Text: `TEXT_INVERTED`
  * Hover: slightly darker `#E14F54`

---

## 3. Typography Theme

Let’s go with a **modern, slightly “techy” but highly readable setup**:

### Font Families

* **Headings**: `Space Grotesk` (or `Outfit` as a backup)
* **Body / UI**: `Inter`
* **Monospace (code / hashes)**: `JetBrains Mono` or `Fira Code`

CSS stack:

```css
:root {
  --font-heading: "Space Grotesk", system-ui, -apple-system, BlinkMacSystemFont,
                  "Segoe UI", sans-serif;
  --font-body: "Inter", system-ui, -apple-system, BlinkMacSystemFont,
               "Segoe UI", sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", ui-monospace, SFMono-Regular,
               Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}
```

Use:

* App title, section headers (Wizard step titles, “Expert Chat”, “Context Panel”) → `--font-heading`, semi-bold (600).
* Paragraphs, labels, buttons → `--font-body`, weights 400–500.
* Addresses, tx hashes, short code snippets → `--font-mono`, 0.95em size.

---

## 4. Applying This in Gradio

Gradio’s theme API lets you layer these on. Here’s a **skeleton** to plug into your existing `Blocks` app:

```python
import gradio as gr
from gradio.themes.utils import colors, fonts, sizes

secretai_theme = gr.themes.Base(
    primary_hue=colors.teal,
    secondary_hue=colors.violet,
).set(
    # Backgrounds
    body_background_fill="#050716",
    body_background_fill_dark="#050716",
    block_background_fill="#0B1021",
    block_background_fill_dark="#0B1021",
    block_border_color="#252B3F",
    border_color_primary="#333A52",

    # Text
    body_text_color="#F5F7FF",
    body_text_color_subdued="#A7B1D2",
    link_text_color="#14F4C9",

    # Buttons
    button_primary_background_fill="#14F4C9",
    button_primary_background_fill_hover="#11C9A5",
    button_primary_text_color="#050716",

    button_secondary_background_fill="transparent",
    button_secondary_background_fill_hover="#141A2C",
    button_secondary_border_color="#333A52",
    button_secondary_text_color="#F5F7FF",

    # Inputs
    input_background_fill="#050716",
    input_border_color="#333A52",
    input_shadow="0px 0px 0px 1px #252B3F",

    # Fonts
    font=fonts.GoogleFont("Inter"),
    font_mono=fonts.GoogleFont("JetBrains Mono"),
    heading_font=fonts.GoogleFont("Space Grotesk"),

    # Radii / sizing
    radius_xs="6px",
    radius_sm="10px",
    radius_md="14px",
    radius_lg="18px",
    radius_xl="22px",
)

with gr.Blocks(theme=secretai_theme, css="""
  /* Headings */
  h1, h2, h3, h4, .prose h1, .prose h2, .prose h3 {
    font-family: var(--font-heading, "Space Grotesk", system-ui);
    letter-spacing: 0.01em;
  }

  /* Chat bubbles */
  .gr-chatbot .message.user {
    background: #11172A;
    border-radius: 16px;
    border: 1px solid #252B3F;
  }
  .gr-chatbot .message.bot {
    background: #0B1021;
    border-left: 3px solid #11C9A5;
    border-radius: 16px;
  }

  /* Wizard step sidebar */
  #wizard-steps-md {
    background: #0B1021;
    border-radius: 16px;
    border: 1px solid #252B3F;
    padding: 12px 16px;
  }

  /* Context panel tabs underline */
  .gr-tab-nav button[aria-selected="true"] {
    border-bottom: 2px solid #14F4C9 !important;
    color: #F5F7FF !important;
  }

  /* Dashboard cards */
  #card-latest-block, #card-mcp-health, #card-index-status, #card-alerts {
    background: radial-gradient(circle at top left, #141A2C 0%, #050716 70%);
    border-radius: 16px;
    border: 1px solid #252B3F;
  }
""") as demo:
    # … your existing layout goes here …
    pass

if __name__ == "__main__":
    demo.launch()
```

Plug this directly into the skeleton:

* Replacing `with gr.Blocks(title="SecretChain Studio", fill_height=True) as demo:`
* With `with gr.Blocks(title="SecretChain Studio", fill_height=True, theme=secretai_theme, css=...) as demo:`

