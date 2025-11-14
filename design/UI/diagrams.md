Mermaid diagrams for:

1. Overall **mode + flow**
2. **Wizard states**
3. **Expert mode states**
4. **Wireframe-style layout** for both modes

---

## 1. High-Level User Flow (Modes + Main Paths)

```mermaid
flowchart TD
    %% ENTRY
    A[Start App] --> B[Load MCP Capabilities KB, Neo4j, SDK, STT ]
    B --> C{Selected Mode?}

    %% MODES
    C -->|Guided Wizard| GW[GUIDED WIZARD MODE]
    C -->|Expert Ops Mode| EX[EXPERT OPS MODE]

    %% GUIDED WIZARD MAIN LOOP
    subgraph GUIDED[Guided Wizard Flow]
        direction LR
        GW --> GW1[Step 1: Define Goal]
        GW1 --> GW2[Step 2: Select Scope<KB / Graph / Chain]
        GW2 --> GW3[Step 3: AI Proposes Ops PlanMCP tool plan]
        GW3 --> GW4[Step 4: Review & Execute Plan]
        GW4 --> GW5[Step 5: Explanation & Report Export]

        %% Where tool calls actually happen
        GW4 --> T1[Execute MCP Operations Neo4j, Chroma, SDK]
        T1 --> GW5
        %% Optional: back to Step 1 for a new goal
        GW5 --> GW1
    end

    %% SWITCHING MODES
    GW --- SW1[User clicks 'Expert Ops Mode']
    EX --- SW2[User clicks 'Guided Wizard']

    SW1 --> EX
    SW2 --> GW1

    %% EXPERT MODE MAIN LOOP
    subgraph EXPERT[Expert Ops Flow]
        direction LR

        EX --> D1[Dashboard Loaded<br/>Latest block, MCP status, indexes]
        D1 --> E1[User sends Chat Prompt]
        E1 --> M1[Assistant Streams Reply may call MCP tools]

        %% Contextual panel reacts to latest result
        M1 --> CP{Result Type?}

        CP -->|Graph entities| P1[Update Graph View]
        CP -->|Transactions| P2[Update Tx View]
        CP -->|Docs / Text| P3[Update KB Snippets View]
        CP -->|Tool metadata| P4[Update Logs/Debug View]

        %% Blockchain Ops
        M1 --> OP[User opens Blockchain Ops Drawer]
        OP --> OP1{Read vs Write?}
        OP1 -->|Read| R1[Run Safe Read via SDK]
        OP1 -->|Write| W1[Show TX Summary & Confirm 2-step safety]
        R1 --> M2[Summarize result in chat]
        W1 --> W2[If Confirmed → Send TX<br/>Report status in chat]
        W2 --> M2
    end

    %% EXIT
    GW5 --> Z[End Session / New Session]
    M2 --> Z
```

---

## 2. Wizard as a State Machine

```mermaid
stateDiagram-v2
    [*] --> WizardMode
    [*] --> ExpertMode
    
    state WizardMode {
        [*] --> DefineGoal

        DefineGoal: Step 1 – Define Goal
        SelectScope: Step 2 – Select Data Scope
        ChooseOps: Step 3 – AI Suggests Operations
        ReviewExecute: Step 4 – Review & Execute
        ExplainExport: Step 5 – Explanation & Export

        %% Transitions
        DefineGoal --> SelectScope: Next
        SelectScope --> ChooseOps: Next
        ChooseOps --> ReviewExecute: Accept Plan
        ChooseOps --> DefineGoal: Change Goal
        ReviewExecute --> ExplainExport: Run Plan (MCP tools)
        ExplainExport --> DefineGoal: New Investigation

        %% Back buttons
        SelectScope --> DefineGoal: Back
        ChooseOps --> SelectScope: Back
        ReviewExecute --> ChooseOps: Back
        ExplainExport --> ReviewExecute: Back (view details)

    }

    state ExpertMode {
        [*] --> ExpertDashboard

        ExpertDashboard: Top dashboard loaded
        ChatActive: Chat streaming
        OpsDrawer: Blockchain operations panel
        ContextPanel: Context visualization panel

        ExpertDashboard --> ChatActive: User types prompt
        ChatActive --> ContextPanel: Result received
        ChatActive --> OpsDrawer: User opens "Ops"
        OpsDrawer --> ChatActive: Operation result → explain in chat

    }
```

---

## 3. Expert Mode Interaction Flow (State / Events)

This one zooms into Expert mode behavior.

```mermaid
stateDiagram-v2
    [*] --> LoadDashboard

    LoadDashboard: Load Status Widgets<br/>(block, MCP, indexes)
    LoadDashboard --> Idle

    Idle: Waiting for user input

    Idle --> ChatInput: User enters text / STT completes
    ChatInput --> StreamingResponse: Send prompt to MCP agent
    StreamingResponse --> ToolPlanning: Agent decides tools (internal)
    ToolPlanning --> ToolExec: Call Neo4j / Chroma / SDK via MCP
    ToolExec --> StreamingResponse: Stream intermediate / final answer

    StreamingResponse --> UpdateContextPanel: Inspect result type
    UpdateContextPanel --> Idle

    %% Blockchain Ops branch
    Idle --> OpenOpsDrawer: User clicks "Blockchain Ops"
    OpenOpsDrawer --> OpsForm: User configures operation
    OpsForm --> OpsPreview: Show generated call / summary
    OpsPreview --> OpsConfirm: User confirms
    OpsConfirm --> OpsSendTx: Send transaction via SDK
    OpsSendTx --> StreamingResponse: Report TX hash / status
    OpsSendTx --> UpdateContextPanel

    %% User can manually switch back to Guided
    Idle --> SwitchToWizard: User toggles mode
```

---

## 4. Wireframe-Level Layout — Guided Wizard

Mermaid isn’t a full wireframing tool, but we can use `subgraph` + layout hints as a structural wireframe.

```mermaid
flowchart LR
    subgraph App[SecretChain Studio]
      direction TB

      subgraph TopBar
        M1[MODE TOGGLE Guided Wizard Expert Ops]
      end

      subgraph GuidedLayout[Guided Wizard Layout]
        direction LR

        subgraph StepsSidebar[Steps Sidebar]
          S1[1. Define Goal]
          S2[2. Select Scope]
          S3[3. Choose Ops]
          S4[4. Review & Execute]
          S5[5. Explain & Export]
        end

        subgraph MainWizardPanel[Main Wizard Panel]
          WContent[Step-specific content - forms, AI plan, review]
        end

        subgraph MiniChat[Corner Mini Chat]
          MCInput[Small chat bubble<br/>ask side questions]
        end
      end

      subgraph BottomNav[Bottom Navigation]
        BBack[Back button]
        BStep[Step indicator]
        BNext[Next button]
      end
    end

    TopBar --> GuidedLayout
    GuidedLayout --> BottomNav
```

---

## 5. Wireframe-Level Layout — Expert Mode (Ops Dashboard + Chat Hybrid)

```mermaid
flowchart TB
    subgraph App[SecretChain Studio – Expert Mode]
      direction TB

      subgraph TopBar
        M2[MODE TOGGLE - Guided WizardExpert Ops active]
      end

      subgraph Dashboard[Status Dashboard]
        DBlock[Latest Block Card]
        DMCP[MCP Health Card]
        DIndex[Graph/KB Index Card]
        DAlert[Alerts / Small Chart]
      end

      subgraph MainArea[Main Split Area]
        direction LR

        subgraph ChatArea[Chat Area]
          ChatHeader[Chat Header<br/>Status: ● Streaming / ○ Idle]
          ChatHistory[Chat Transcript<br/>with tool badges]
          ChatInput[Mic + Input box + Send]
        end

        subgraph ContextPanel[Context Visualization Panel]
          Tabs[Tabs: Graph : Tx : KB : Logs]
          ContextView[ Active view graph, tx details, snippets, logs ]
        end
      end

      subgraph OpsDrawer[Blockchain Ops Drawer overlay/popup]
        OpsHeader[Network / Wallet / Gas]
        OpsRead[Read Ops List]
        OpsWrite[Write Ops List<br/>with confirmation]
      end
    end

    TopBar --> Dashboard
    Dashboard --> MainArea
    ChatArea --> ContextPanel
    MainArea --> OpsDrawer
```


