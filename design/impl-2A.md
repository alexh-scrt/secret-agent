# PART 2: Gradio - MCP Integration

## Overview

Part 2 builds the Gradio application that provides a beautiful, user-friendly interface to interact with our enhanced MCP-SCRT server. This includes an AI agent orchestration layer, streaming chat interface, portfolio dashboard, and more.

---

## Phase 2A: Agent Orchestration Layer

### Task 2A.1: Intent Classifier

**Objective**: Create an LLM-powered intent classifier that determines what type of request the user is making.

**Files to Create**:
```
src/agent/__init__.py
src/agent/intent_classifier.py
src/agent/types.py
tests/test_intent_classifier.py
```

**Implementation Details**:

```python
# src/agent/types.py

"""
Type definitions for the agent system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class IntentType(Enum):
    """Types of user intents."""
    INFORMATION = "information"  # Question about Secret Network
    TRANSACTION = "transaction"  # Execute blockchain operation
    QUERY = "query"  # Query blockchain data
    ANALYSIS = "analysis"  # Analyze patterns/networks
    HYBRID = "hybrid"  # Multiple intent types
    CONVERSATION = "conversation"  # General chat
    UNKNOWN = "unknown"  # Unable to classify


@dataclass
class Entity:
    """Extracted entity from user message."""
    type: str  # address, amount, validator, proposal_id, etc.
    value: str
    confidence: float = 1.0


@dataclass
class Intent:
    """Classified user intent."""
    type: IntentType
    confidence: float
    topic: Optional[str] = None  # For information requests
    operation: Optional[str] = None  # For transactions
    entities: List[Entity] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class ConversationContext:
    """Context for multi-turn conversations."""
    history: List[Dict[str, str]] = field(default_factory=list)
    user_address: Optional[str] = None
    last_intent: Optional[Intent] = None
    
    def add_turn(self, user_message: str, assistant_response: str):
        """Add a conversation turn."""
        self.history.append({
            "role": "user",
            "content": user_message
        })
        self.history.append({
            "role": "assistant",
            "content": assistant_response
        })
    
    def get_recent_history(self, n: int = 5) -> List[Dict[str, str]]:
        """Get recent conversation history."""
        return self.history[-n*2:] if self.history else []


@dataclass
class AgentResponse:
    """Response from agent to user."""
    type: str  # knowledge, transaction, query, analysis, error
    content: str  # Main response text
    data: Optional[Dict[str, Any]] = None  # Structured data
    sources: Optional[List[Dict]] = None  # Source citations
    requires_confirmation: bool = False
    pending_action: Optional[Dict] = None  # Action awaiting confirmation


# Export
__all__ = [
    "IntentType",
    "Entity",
    "Intent",
    "ConversationContext",
    "AgentResponse"
]
```

```python
# src/agent/intent_classifier.py

"""
Intent classifier using LLM to understand user requests.
"""

import json
import re
from typing import List, Optional
import logging
from .types import Intent, IntentType, Entity

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Classifies user intents using LLM.
    
    Determines:
    - What type of request (information, transaction, query, etc.)
    - What topic or operation
    - Extracted entities (addresses, amounts, etc.)
    """
    
    # Entity extraction patterns
    PATTERNS = {
        "address": r"secret1[a-z0-9]{38}",
        "validator": r"secretvaloper1[a-z0-9]{38}",
        "amount": r"(\d+(?:\.\d+)?)\s*(SCRT|uscrt|scrt)?",
        "proposal_id": r"(?:proposal\s*)?#?(\d+)",
    }
    
    # Keywords for intent classification (fallback)
    KEYWORDS = {
        IntentType.INFORMATION: [
            "what", "how", "explain", "tell me", "describe",
            "definition", "meaning", "introduction", "learn"
        ],
        IntentType.TRANSACTION: [
            "send", "transfer", "delegate", "stake", "vote",
            "withdraw", "claim", "execute", "instantiate"
        ],
        IntentType.QUERY: [
            "show", "get", "check", "balance", "list",
            "display", "view", "my", "current"
        ],
        IntentType.ANALYSIS: [
            "analyze", "recommend", "compare", "best",
            "find", "suggest", "optimal", "pattern"
        ],
    }
    
    def __init__(self, ollama_client):
        """
        Initialize intent classifier.
        
        Args:
            ollama_client: Ollama client for LLM calls
        """
        self.ollama = ollama_client
        logger.info("Initialized IntentClassifier")
    
    async def classify(
        self,
        message: str,
        context: Optional[object] = None
    ) -> Intent:
        """
        Classify user intent.
        
        Args:
            message: User message
            context: Optional conversation context
            
        Returns:
            Intent object with classification
        """
        try:
            # Try LLM classification first
            intent = await self._classify_with_llm(message, context)
            
            # Extract entities
            intent.entities = self._extract_entities(message)
            
            return intent
        
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            
            # Fallback to keyword-based classification
            return self._classify_with_keywords(message)
    
    async def _classify_with_llm(
        self,
        message: str,
        context: Optional[object]
    ) -> Intent:
        """
        Classify intent using LLM.
        
        Args:
            message: User message
            context: Conversation context
            
        Returns:
            Intent object
        """
        # Build context string
        context_str = ""
        if context and hasattr(context, 'get_recent_history'):
            recent = context.get_recent_history(3)
            if recent:
                context_str = "Recent conversation:\n" + "\n".join(
                    f"{msg['role']}: {msg['content'][:100]}"
                    for msg in recent
                )
        
        # Create classification prompt
        prompt = f"""Analyze this user message and classify the intent.

{context_str}

User message: "{message}"

Classify the intent as one of:
- information: User wants to learn about Secret Network (concepts, features, how-to)
- transaction: User wants to execute a blockchain operation (send, delegate, vote, etc.)
- query: User wants to retrieve blockchain data (balance, validators, proposals, etc.)
- analysis: User wants analysis or recommendations (best validators, network patterns, etc.)
- hybrid: Multiple intents combined (e.g., "explain staking and show my delegations")
- conversation: General chat or greeting
- unknown: Cannot determine intent

Also identify:
- The specific topic (for information) or operation (for transaction)
- Confidence level (0.0-1.0)

Respond ONLY with valid JSON in this exact format:
{{
  "intent_type": "information|transaction|query|analysis|hybrid|conversation|unknown",
  "confidence": 0.95,
  "topic": "staking",
  "operation": "delegate",
  "reasoning": "Brief explanation"
}}

DO NOT include any text before or after the JSON. ONLY output valid JSON."""
        
        # Call LLM
        response = self.ollama.generate(
            prompt=prompt,
            options={
                "temperature": 0.1,  # Low temperature for consistent classification
                "top_p": 0.9
            }
        )
        
        # Parse response
        response_text = response.get("response", "").strip()
        
        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()
        
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response text: {response_text}")
            # Fallback to keyword classification
            return self._classify_with_keywords(message)
        
        # Create Intent object
        intent_type_str = data.get("intent_type", "unknown")
        try:
            intent_type = IntentType(intent_type_str)
        except ValueError:
            intent_type = IntentType.UNKNOWN
        
        return Intent(
            type=intent_type,
            confidence=float(data.get("confidence", 0.5)),
            topic=data.get("topic"),
            operation=data.get("operation"),
            reasoning=data.get("reasoning", "")
        )
    
    def _classify_with_keywords(self, message: str) -> Intent:
        """
        Fallback keyword-based classification.
        
        Args:
            message: User message
            
        Returns:
            Intent object
        """
        message_lower = message.lower()
        
        # Score each intent type
        scores = {}
        for intent_type, keywords in self.KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            if score > 0:
                scores[intent_type] = score
        
        if not scores:
            return Intent(
                type=IntentType.CONVERSATION,
                confidence=0.5,
                reasoning="No specific keywords matched"
            )
        
        # Get highest scoring intent
        intent_type = max(scores, key=scores.get)
        max_score = scores[intent_type]
        total_keywords = len(self.KEYWORDS[intent_type])
        confidence = min(max_score / total_keywords, 1.0)
        
        return Intent(
            type=intent_type,
            confidence=confidence,
            reasoning=f"Keyword match (score: {max_score})"
        )
    
    def _extract_entities(self, message: str) -> List[Entity]:
        """
        Extract entities from message using regex patterns.
        
        Args:
            message: User message
            
        Returns:
            List of extracted entities
        """
        entities = []
        
        # Extract addresses
        for match in re.finditer(self.PATTERNS["address"], message):
            entities.append(Entity(
                type="address",
                value=match.group(0),
                confidence=1.0
            ))
        
        # Extract validator addresses
        for match in re.finditer(self.PATTERNS["validator"], message):
            entities.append(Entity(
                type="validator",
                value=match.group(0),
                confidence=1.0
            ))
        
        # Extract amounts
        for match in re.finditer(self.PATTERNS["amount"], message):
            amount = match.group(1)
            denom = match.group(2) or "SCRT"
            entities.append(Entity(
                type="amount",
                value=f"{amount} {denom}",
                confidence=0.9
            ))
        
        # Extract proposal IDs
        for match in re.finditer(self.PATTERNS["proposal_id"], message):
            entities.append(Entity(
                type="proposal_id",
                value=match.group(1),
                confidence=0.95
            ))
        
        return entities


# Export
__all__ = ["IntentClassifier"]
```

**Test File**:

```python
# tests/test_intent_classifier.py

import pytest
from unittest.mock import Mock, AsyncMock
from src.agent.intent_classifier import IntentClassifier
from src.agent.types import IntentType, Intent


@pytest.fixture
def mock_ollama():
    """Mock Ollama client."""
    ollama = Mock()
    ollama.generate = Mock()
    return ollama


@pytest.fixture
def classifier(mock_ollama):
    """Create intent classifier."""
    return IntentClassifier(ollama_client=mock_ollama)


@pytest.mark.asyncio
async def test_classify_information_intent(classifier, mock_ollama):
    """Test classifying information request."""
    mock_ollama.generate.return_value = {
        "response": '{"intent_type": "information", "confidence": 0.95, "topic": "staking", "reasoning": "User asking to learn"}'
    }
    
    intent = await classifier.classify("What is staking on Secret Network?")
    
    assert intent.type == IntentType.INFORMATION
    assert intent.topic == "staking"
    assert intent.confidence > 0.9


@pytest.mark.asyncio
async def test_classify_transaction_intent(classifier, mock_ollama):
    """Test classifying transaction request."""
    mock_ollama.generate.return_value = {
        "response": '{"intent_type": "transaction", "confidence": 0.98, "operation": "delegate", "reasoning": "User wants to stake tokens"}'
    }
    
    intent = await classifier.classify("Stake 100 SCRT to validator X")
    
    assert intent.type == IntentType.TRANSACTION
    assert intent.operation == "delegate"


@pytest.mark.asyncio
async def test_classify_query_intent(classifier, mock_ollama):
    """Test classifying query request."""
    mock_ollama.generate.return_value = {
        "response": '{"intent_type": "query", "confidence": 0.92, "reasoning": "User requesting data"}'
    }
    
    intent = await classifier.classify("Show me my balance")
    
    assert intent.type == IntentType.QUERY


@pytest.mark.asyncio
async def test_extract_entities_address(classifier):
    """Test extracting wallet address."""
    message = "Send 100 SCRT to secret1abc123def456ghi789jkl012mno345pqr678stu"
    
    intent = await classifier.classify(message)
    
    # Should extract address
    addresses = [e for e in intent.entities if e.type == "address"]
    assert len(addresses) == 1


@pytest.mark.asyncio
async def test_extract_entities_amount(classifier):
    """Test extracting amount."""
    message = "Delegate 500 SCRT"
    
    intent = await classifier.classify(message)
    
    # Should extract amount
    amounts = [e for e in intent.entities if e.type == "amount"]
    assert len(amounts) == 1
    assert "500" in amounts[0].value


@pytest.mark.asyncio
async def test_fallback_keyword_classification(classifier, mock_ollama):
    """Test fallback to keyword classification on LLM failure."""
    # Make LLM fail
    mock_ollama.generate.side_effect = Exception("LLM error")
    
    intent = await classifier.classify("What is Secret Network?")
    
    # Should still classify (fallback)
    assert intent.type in [IntentType.INFORMATION, IntentType.CONVERSATION]


def test_keyword_classification_information(classifier):
    """Test keyword-based classification for information."""
    intent = classifier._classify_with_keywords("How does staking work?")
    
    assert intent.type == IntentType.INFORMATION


def test_keyword_classification_transaction(classifier):
    """Test keyword-based classification for transaction."""
    intent = classifier._classify_with_keywords("Send tokens to address")
    
    assert intent.type == IntentType.TRANSACTION


def test_keyword_classification_query(classifier):
    """Test keyword-based classification for query."""
    intent = classifier._classify_with_keywords("Show my balance")
    
    assert intent.type == IntentType.QUERY
```

**Success Criteria**:
- ✅ LLM-powered intent classification works
- ✅ Fallback keyword classification available
- ✅ Entity extraction functional
- ✅ All tests pass

---

### Task 2A.2: Agent Orchestrator

**Objective**: Create the main orchestrator that routes requests to appropriate handlers and coordinates multi-step workflows.

**Files to Create**:
```
src/agent/orchestrator.py
src/agent/handlers/__init__.py
src/agent/handlers/knowledge_handler.py
src/agent/handlers/transaction_handler.py
src/agent/handlers/query_handler.py
tests/test_orchestrator.py
```

**Implementation Details**:

```python
# src/agent/orchestrator.py

"""
Main agent orchestrator for routing and coordinating operations.
"""

import asyncio
from typing import Optional, Dict, Any
import logging
from .intent_classifier import IntentClassifier
from .types import (
    Intent,
    IntentType,
    ConversationContext,
    AgentResponse
)
from .handlers.knowledge_handler import KnowledgeHandler
from .handlers.transaction_handler import TransactionHandler
from .handlers.query_handler import QueryHandler

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Main agent that routes requests and coordinates execution.
    
    Flow:
    1. Classify user intent
    2. Route to appropriate handler
    3. Execute operations (potentially multi-step)
    4. Format and return response
    """
    
    def __init__(
        self,
        mcp_server,
        ollama_client,
        knowledge_service,
        graph_service,
        cache_service
    ):
        """
        Initialize orchestrator.
        
        Args:
            mcp_server: MCP-SCRT server instance
            ollama_client: Ollama client for LLM
            knowledge_service: Knowledge service
            graph_service: Graph service
            cache_service: Cache service
        """
        self.mcp = mcp_server
        self.ollama = ollama_client
        self.knowledge_service = knowledge_service
        self.graph_service = graph_service
        self.cache_service = cache_service
        
        # Initialize intent classifier
        self.classifier = IntentClassifier(ollama_client=ollama_client)
        
        # Initialize handlers
        self.knowledge_handler = KnowledgeHandler(
            knowledge_service=knowledge_service,
            ollama_client=ollama_client
        )
        
        self.transaction_handler = TransactionHandler(
            mcp_server=mcp_server,
            graph_service=graph_service
        )
        
        self.query_handler = QueryHandler(
            mcp_server=mcp_server,
            cache_service=cache_service
        )
        
        logger.info("Initialized AgentOrchestrator")
    
    async def process_message(
        self,
        message: str,
        context: ConversationContext
    ) -> AgentResponse:
        """
        Process user message and generate response.
        
        Args:
            message: User message
            context: Conversation context
            
        Returns:
            Agent response
        """
        try:
            logger.info(f"Processing message: {message[:100]}...")
            
            # 1. Classify intent
            intent = await self.classifier.classify(message, context)
            context.last_intent = intent
            
            logger.info(f"Intent: {intent.type.value} (confidence: {intent.confidence:.2f})")
            
            # 2. Route to appropriate handler
            if intent.type == IntentType.INFORMATION:
                response = await self.knowledge_handler.handle(message, intent, context)
            
            elif intent.type == IntentType.TRANSACTION:
                response = await self.transaction_handler.handle(message, intent, context)
            
            elif intent.type == IntentType.QUERY:
                response = await self.query_handler.handle(message, intent, context)
            
            elif intent.type == IntentType.ANALYSIS:
                response = await self._handle_analysis(message, intent, context)
            
            elif intent.type == IntentType.HYBRID:
                response = await self._handle_hybrid(message, intent, context)
            
            elif intent.type == IntentType.CONVERSATION:
                response = await self._handle_conversation(message, context)
            
            else:
                response = AgentResponse(
                    type="error",
                    content="I'm not sure how to help with that. Could you rephrase?"
                )
            
            # 3. Update context
            context.add_turn(message, response.content)
            
            return response
        
        except Exception as e:
            logger.error(f"Message processing failed: {e}", exc_info=True)
            return AgentResponse(
                type="error",
                content=f"I encountered an error: {str(e)}. Please try again."
            )
    
    async def _handle_analysis(
        self,
        message: str,
        intent: Intent,
        context: ConversationContext
    ) -> AgentResponse:
        """
        Handle analysis requests (validator recommendations, network patterns, etc.).
        
        Args:
            message: User message
            intent: Classified intent
            context: Conversation context
            
        Returns:
            Agent response
        """
        # Determine analysis type from message
        message_lower = message.lower()
        
        # Validator recommendations
        if any(word in message_lower for word in ["validator", "recommend", "stake", "delegate"]):
            # Extract wallet address if present
            wallet_addresses = [e.value for e in intent.entities if e.type == "address"]
            wallet_address = wallet_addresses[0] if wallet_addresses else context.user_address
            
            if not wallet_address:
                return AgentResponse(
                    type="error",
                    content="I need a wallet address to provide validator recommendations. Please provide your address or set it in settings."
                )
            
            # Call graph service for recommendations
            try:
                recommendations = await self.graph_service.recommend_validators(
                    wallet_address=wallet_address,
                    count=5
                )
                
                # Format response
                content = "Here are my top validator recommendations:\n\n"
                for idx, rec in enumerate(recommendations, 1):
                    content += f"**{idx}. {rec.moniker}**\n"
                    content += f"   Score: {rec.score:.1f}/10\n"
                    content += f"   Reasons: {', '.join(rec.reasons)}\n"
                    content += f"   Metrics: {rec.metrics.get('voting_power', 0):.2f}% voting power, "
                    content += f"{rec.metrics.get('commission', 0):.2f}% commission, "
                    content += f"{rec.metrics.get('uptime', 0):.2f}% uptime\n\n"
                
                return AgentResponse(
                    type="analysis",
                    content=content,
                    data={"recommendations": [rec.__dict__ for rec in recommendations]}
                )
            
            except Exception as e:
                logger.error(f"Validator recommendation failed: {e}")
                return AgentResponse(
                    type="error",
                    content=f"I couldn't generate validator recommendations: {str(e)}"
                )
        
        # Network analysis
        elif any(word in message_lower for word in ["network", "pattern", "analyze"]):
            try:
                analysis = await self.graph_service.analyze_validator_network()
                
                content = f"**Network Analysis:**\n\n"
                content += f"- Total validators: {analysis.node_count}\n"
                content += f"- Total delegations: {analysis.relationship_count}\n"
                content += f"- Network density: {analysis.density:.2%}\n\n"
                
                if analysis.insights:
                    content += "**Insights:**\n"
                    for insight in analysis.insights:
                        content += f"- {insight}\n"
                
                return AgentResponse(
                    type="analysis",
                    content=content,
                    data={"analysis": analysis.__dict__}
                )
            
            except Exception as e:
                logger.error(f"Network analysis failed: {e}")
                return AgentResponse(
                    type="error",
                    content=f"I couldn't analyze the network: {str(e)}"
                )
        
        # Default: use LLM to handle
        return await self._handle_conversation(message, context)
    
    async def _handle_hybrid(
        self,
        message: str,
        intent: Intent,
        context: ConversationContext
    ) -> AgentResponse:
        """
        Handle hybrid requests (multiple intents).
        
        Args:
            message: User message
            intent: Classified intent
            context: Conversation context
            
        Returns:
            Agent response
        """
        # Split into sub-tasks (simple heuristic)
        # Example: "Explain staking and show my delegations"
        
        parts = []
        
        # Check for information request
        if any(word in message.lower() for word in ["what", "how", "explain"]):
            parts.append("information")
        
        # Check for query request
        if any(word in message.lower() for word in ["show", "my", "get", "check"]):
            parts.append("query")
        
        # Execute both parts
        responses = []
        
        if "information" in parts:
            info_response = await self.knowledge_handler.handle(message, intent, context)
            responses.append(info_response.content)
        
        if "query" in parts:
            query_response = await self.query_handler.handle(message, intent, context)
            responses.append(query_response.content)
        
        # Combine responses
        combined_content = "\n\n---\n\n".join(responses)
        
        return AgentResponse(
            type="hybrid",
            content=combined_content
        )
    
    async def _handle_conversation(
        self,
        message: str,
        context: ConversationContext
    ) -> AgentResponse:
        """
        Handle general conversation.
        
        Args:
            message: User message
            context: Conversation context
            
        Returns:
            Agent response
        """
        # Build conversation history
        history = context.get_recent_history(5)
        
        # System prompt
        system_prompt = """You are a helpful AI assistant for Secret Network.
You help users learn about and interact with Secret Network blockchain.
Be friendly, concise, and helpful."""
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})
        
        # Generate response
        try:
            response = self.ollama.chat(
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            )
            
            content = response["message"]["content"]
            
            return AgentResponse(
                type="conversation",
                content=content
            )
        
        except Exception as e:
            logger.error(f"Conversation handling failed: {e}")
            return AgentResponse(
                type="error",
                content="I'm having trouble responding right now. Please try again."
            )


# Export
__all__ = ["AgentOrchestrator"]
```

```python
# src/agent/handlers/__init__.py

"""
Request handlers for different intent types.
"""

from .knowledge_handler import KnowledgeHandler
from .transaction_handler import TransactionHandler
from .query_handler import QueryHandler

__all__ = [
    "KnowledgeHandler",
    "TransactionHandler",
    "QueryHandler"
]
```

```python
# src/agent/handlers/knowledge_handler.py

"""
Handler for information/knowledge requests.
"""

import logging
from ..types import Intent, ConversationContext, AgentResponse

logger = logging.getLogger(__name__)


class KnowledgeHandler:
    """
    Handles information requests using knowledge base.
    """
    
    def __init__(self, knowledge_service, ollama_client):
        """
        Initialize knowledge handler.
        
        Args:
            knowledge_service: Knowledge service instance
            ollama_client: Ollama client
        """
        self.knowledge = knowledge_service
        self.ollama = ollama_client
        logger.info("Initialized KnowledgeHandler")
    
    async def handle(
        self,
        message: str,
        intent: Intent,
        context: ConversationContext
    ) -> AgentResponse:
        """
        Handle knowledge request.
        
        Args:
            message: User message
            intent: Classified intent
            context: Conversation context
            
        Returns:
            Agent response with knowledge
        """
        try:
            # Use knowledge service to search and synthesize
            result = await self.knowledge.search_and_synthesize(
                query=message,
                collection=intent.topic,  # May be None for general search
                top_k=5
            )
            
            # Format sources for display
            sources = None
            if result.sources:
                sources = [
                    {
                        "title": s.document.title,
                        "collection": s.document.collection,
                        "similarity": f"{s.similarity:.1%}"
                    }
                    for s in result.sources
                ]
            
            return AgentResponse(
                type="knowledge",
                content=result.response,
                sources=sources,
                data={
                    "confidence": result.confidence,
                    "cached": result.cached
                }
            )
        
        except Exception as e:
            logger.error(f"Knowledge handling failed: {e}")
            return AgentResponse(
                type="error",
                content=f"I couldn't find information about that: {str(e)}"
            )
```

```python
# src/agent/handlers/transaction_handler.py

"""
Handler for transaction requests.
"""

import logging
from ..types import Intent, ConversationContext, AgentResponse

logger = logging.getLogger(__name__)


class TransactionHandler:
    """
    Handles transaction requests with risk assessment and confirmation.
    """
    
    def __init__(self, mcp_server, graph_service):
        """
        Initialize transaction handler.
        
        Args:
            mcp_server: MCP server instance
            graph_service: Graph service for analysis
        """
        self.mcp = mcp_server
        self.graph = graph_service
        logger.info("Initialized TransactionHandler")
    
    async def handle(
        self,
        message: str,
        intent: Intent,
        context: ConversationContext
    ) -> AgentResponse:
        """
        Handle transaction request.
        
        Args:
            message: User message
            intent: Classified intent
            context: Conversation context
            
        Returns:
            Agent response with transaction details or confirmation request
        """
        # Extract parameters from entities
        params = self._extract_parameters(intent)
        
        # Determine operation
        operation = intent.operation or self._infer_operation(message)
        
        if not operation:
            return AgentResponse(
                type="error",
                content="I couldn't determine what transaction you want to execute. Please be more specific."
            )
        
        # Build confirmation message
        confirmation_msg = self._build_confirmation(operation, params)
        
        return AgentResponse(
            type="transaction",
            content=confirmation_msg,
            requires_confirmation=True,
            pending_action={
                "operation": operation,
                "params": params
            }
        )
    
    def _extract_parameters(self, intent: Intent) -> dict:
        """Extract parameters from entities."""
        params = {}
        
        for entity in intent.entities:
            if entity.type == "address":
                params["recipient"] = entity.value
            elif entity.type == "validator":
                params["validator_address"] = entity.value
            elif entity.type == "amount":
                # Parse amount and denom
                parts = entity.value.split()
                if len(parts) >= 2:
                    params["amount"] = parts[0]
                    params["denom"] = parts[1].lower()
            elif entity.type == "proposal_id":
                params["proposal_id"] = int(entity.value)
        
        return params
    
    def _infer_operation(self, message: str) -> str:
        """Infer operation from message."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["send", "transfer"]):
            return "secret_send_tokens"
        elif any(word in message_lower for word in ["delegate", "stake"]):
            return "secret_delegate"
        elif any(word in message_lower for word in ["undelegate", "unstake"]):
            return "secret_undelegate"
        elif any(word in message_lower for word in ["vote"]):
            return "secret_vote_proposal"
        elif any(word in message_lower for word in ["withdraw", "claim"]):
            return "secret_withdraw_rewards"
        
        return None
    
    def _build_confirmation(self, operation: str, params: dict) -> str:
        """Build confirmation message."""
        if operation == "secret_delegate":
            return f"""I'll delegate {params.get('amount', '?')} {params.get('denom', 'SCRT')} to validator {params.get('validator_address', '?')}.

Please confirm:
- Amount: {params.get('amount', '?')} {params.get('denom', 'SCRT')}
- Validator: {params.get('validator_address', '?')}

Reply 'confirm' to proceed or 'cancel' to abort."""
        
        # Add more operation-specific confirmations
        return f"Please confirm this transaction: {operation}"


# Export
__all__ = ["TransactionHandler"]
```

```python
# src/agent/handlers/query_handler.py

"""
Handler for blockchain query requests.
"""

import logging
from ..types import Intent, ConversationContext, AgentResponse

logger = logging.getLogger(__name__)


class QueryHandler:
    """
    Handles blockchain query requests.
    """
    
    def __init__(self, mcp_server, cache_service):
        """
        Initialize query handler.
        
        Args:
            mcp_server: MCP server instance
            cache_service: Cache service for optimization
        """
        self.mcp = mcp_server
        self.cache = cache_service
        logger.info("Initialized QueryHandler")
    
    async def handle(
        self,
        message: str,
        intent: Intent,
        context: ConversationContext
    ) -> AgentResponse:
        """
        Handle query request.
        
        Args:
            message: User message
            intent: Classified intent
            context: Conversation context
            
        Returns:
            Agent response with query results
        """
        # Determine what to query
        query_type = self._determine_query_type(message)
        
        if not query_type:
            return AgentResponse(
                type="error",
                content="I'm not sure what you want to query. Please be more specific."
            )
        
        # Extract address if needed
        addresses = [e.value for e in intent.entities if e.type == "address"]
        address = addresses[0] if addresses else context.user_address
        
        try:
            # Execute query
            if query_type == "balance":
                result = await self._query_balance(address)
            elif query_type == "delegations":
                result = await self._query_delegations(address)
            elif query_type == "rewards":
                result = await self._query_rewards(address)
            elif query_type == "validators":
                result = await self._query_validators()
            else:
                result = "Query type not implemented yet."
            
            return AgentResponse(
                type="query",
                content=result
            )
        
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return AgentResponse(
                type="error",
                content=f"Query failed: {str(e)}"
            )
    
    def _determine_query_type(self, message: str) -> str:
        """Determine query type from message."""
        message_lower = message.lower()
        
        if "balance" in message_lower:
            return "balance"
        elif any(word in message_lower for word in ["delegation", "stake", "staked"]):
            return "delegations"
        elif any(word in message_lower for word in ["reward", "earning"]):
            return "rewards"
        elif "validator" in message_lower:
            return "validators"
        
        return None
    
    async def _query_balance(self, address: str) -> str:
        """Query balance."""
        if not address:
            return "Please provide a wallet address or set your address in settings."
        
        result = await self.mcp.execute_tool(
            "secret_get_balance",
            {"address": address}
        )
        
        if not result.get("ok"):
            return f"Error: {result.get('error')}"
        
        data = result.get("data", {})
        balances = data.get("balances", [])
        
        if not balances:
            return f"No balances found for {address}"
        
        response = f"**Balance for {address}:**\n\n"
        for balance in balances:
            amount = float(balance.get("amount", 0)) / 1_000_000  # Convert uscrt to SCRT
            denom = balance.get("denom", "").upper()
            response += f"- {amount:.6f} {denom}\n"
        
        return response
    
    async def _query_delegations(self, address: str) -> str:
        """Query delegations."""
        if not address:
            return "Please provide a wallet address or set your address in settings."
        
        result = await self.mcp.execute_tool(
            "secret_get_delegations",
            {"address": address}
        )
        
        if not result.get("ok"):
            return f"Error: {result.get('error')}"
        
        data = result.get("data", {})
        delegations = data.get("delegations", [])
        
        if not delegations:
            return f"No delegations found for {address}"
        
        response = f"**Delegations for {address}:**\n\n"
        for delegation in delegations:
            validator = delegation.get("validator_address", "Unknown")
            amount = float(delegation.get("amount", 0)) / 1_000_000
            response += f"- {amount:.6f} SCRT to {validator}\n"
        
        return response
    
    async def _query_rewards(self, address: str) -> str:
        """Query rewards."""
        if not address:
            return "Please provide a wallet address or set your address in settings."
        
        result = await self.mcp.execute_tool(
            "secret_get_rewards",
            {"address": address}
        )
        
        if not result.get("ok"):
            return f"Error: {result.get('error')}"
        
        data = result.get("data", {})
        rewards = data.get("rewards", [])
        
        if not rewards:
            return f"No rewards found for {address}"
        
        total = sum(float(r.get("amount", 0)) for r in rewards) / 1_000_000
        
        response = f"**Rewards for {address}:**\n\n"
        response += f"Total: {total:.6f} SCRT\n\n"
        
        for reward in rewards[:5]:  # Show top 5
            validator = reward.get("validator_address", "Unknown")
            amount = float(reward.get("amount", 0)) / 1_000_000
            response += f"- {amount:.6f} SCRT from {validator}\n"
        
        return response
    
    async def _query_validators(self) -> str:
        """Query validators."""
        result = await self.mcp.execute_tool(
            "secret_get_validators",
            {}
        )
        
        if not result.get("ok"):
            return f"Error: {result.get('error')}"
        
        data = result.get("data", {})
        validators = data.get("validators", [])
        
        if not validators:
            return "No validators found"
        
        response = f"**Top 10 Validators:**\n\n"
        for validator in validators[:10]:
            moniker = validator.get("description", {}).get("moniker", "Unknown")
            voting_power = validator.get("voting_power", 0)
            response += f"- {moniker} (Voting Power: {voting_power})\n"
        
        return response


# Export
__all__ = ["QueryHandler"]
```

**Success Criteria**:
- ✅ Orchestrator routes requests correctly
- ✅ Knowledge handler uses knowledge service
- ✅ Transaction handler requires confirmation
- ✅ Query handler executes blockchain queries
- ✅ Multi-turn conversations work

---

## Summary of Phase 2A

You've completed the **Agent Orchestration Layer** with:

✅ **Intent Classifier**:
- LLM-powered classification
- Entity extraction
- Keyword fallback

✅ **Agent Orchestrator**:
- Request routing
- Multi-intent handling
- Context management

✅ **Request Handlers**:
- Knowledge handler (semantic search + LLM)
- Transaction handler (with confirmations)
- Query handler (blockchain data)

