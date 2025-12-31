"""
Property-Based Tests for State Machine Documentation Accuracy

Feature: documentation-unification
Property 6: State Machine Documentation Accuracy
Validates: Requirements 6.1, 6.2, 6.3, 6.5

Tests that state machine documentation in states.md accurately reflects
the implementation in vince/state/.
"""

import re
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from vince.state.default_state import (
    VALID_TRANSITIONS as DEFAULT_VALID_TRANSITIONS,
    DefaultState,
)
from vince.state.offer_state import (
    VALID_TRANSITIONS as OFFER_VALID_TRANSITIONS,
    OfferState,
)


# =============================================================================
# Helper Functions for Extraction
# =============================================================================


def extract_documented_default_states(states_md_path: Path) -> set[str]:
    """
    Extract all documented DefaultState values from states.md.
    
    Parses the states.md file to find default state definitions in tables.
    """
    states = set()
    
    if not states_md_path.exists():
        return states
    
    content = states_md_path.read_text()
    
    # Known default states to look for
    default_state_names = {"none", "pending", "active", "removed"}
    
    # Look for states in Default States table section
    for state in default_state_names:
        # Pattern matches table rows like: | none | def-none | ...
        if re.search(rf"\|\s*{state}\s*\|", content, re.IGNORECASE):
            states.add(state)
    
    return states


def extract_documented_offer_states(states_md_path: Path) -> set[str]:
    """
    Extract all documented OfferState values from states.md.
    
    Parses the states.md file to find offer state definitions in tables.
    """
    states = set()
    
    if not states_md_path.exists():
        return states
    
    content = states_md_path.read_text()
    
    # Known offer states to look for
    offer_state_names = {"none", "created", "active", "rejected"}
    
    # Look for states in Offer States table section
    for state in offer_state_names:
        # Pattern matches table rows like: | created | off-crtd | ...
        if re.search(rf"\|\s*{state}\s*\|", content, re.IGNORECASE):
            states.add(state)
    
    return states


def extract_documented_default_transitions(states_md_path: Path) -> dict[str, set[str]]:
    """
    Extract documented default state transitions from states.md.
    
    Returns a dict mapping from_state to set of to_states.
    """
    transitions = {}
    
    if not states_md_path.exists():
        return transitions
    
    content = states_md_path.read_text()
    
    # Pattern to match transition table rows like:
    # | none | pending | `slap` | ... |
    # | none | active | `slap -set` / `set` | ... |
    transition_pattern = re.compile(
        r'\|\s*(none|pending|active|removed)\s*\|\s*(none|pending|active|removed)\s*\|'
    )
    
    for match in transition_pattern.finditer(content):
        from_state = match.group(1).lower()
        to_state = match.group(2).lower()
        
        if from_state not in transitions:
            transitions[from_state] = set()
        transitions[from_state].add(to_state)
    
    return transitions


def extract_documented_offer_transitions(states_md_path: Path) -> dict[str, set[str]]:
    """
    Extract documented offer state transitions from states.md.
    
    Returns a dict mapping from_state to set of to_states.
    """
    transitions = {}
    
    if not states_md_path.exists():
        return transitions
    
    content = states_md_path.read_text()
    
    # Pattern to match transition table rows like:
    # | none | created | `offer` / auto-create | ... |
    # | created | active | First use | ... |
    transition_pattern = re.compile(
        r'\|\s*(none|created|active|rejected)\s*\|\s*(none|created|active|rejected)\s*\|'
    )
    
    # Find the Offer State Transitions section
    offer_section_match = re.search(
        r'### Offer State Transitions.*?(?=###|\Z)',
        content,
        re.DOTALL
    )
    
    if offer_section_match:
        offer_section = offer_section_match.group()
        for match in transition_pattern.finditer(offer_section):
            from_state = match.group(1).lower()
            to_state = match.group(2).lower()
            
            if from_state not in transitions:
                transitions[from_state] = set()
            transitions[from_state].add(to_state)
    
    return transitions


def extract_source_default_transitions() -> dict[str, set[str]]:
    """
    Extract default state transitions from source code.
    
    Returns a dict mapping from_state to set of to_states.
    """
    transitions = {}
    
    for from_state, to_states in DEFAULT_VALID_TRANSITIONS.items():
        transitions[from_state.value] = {s.value for s in to_states}
    
    return transitions


def extract_source_offer_transitions() -> dict[str, set[str]]:
    """
    Extract offer state transitions from source code.
    
    Returns a dict mapping from_state to set of to_states.
    """
    transitions = {}
    
    for from_state, to_states in OFFER_VALID_TRANSITIONS.items():
        transitions[from_state.value] = {s.value for s in to_states}
    
    return transitions


# =============================================================================
# Property 6: State Machine Documentation Accuracy
# Validates: Requirements 6.1, 6.2, 6.3, 6.5
# Feature: documentation-unification
# =============================================================================


class TestStateMachineDocumentationAccuracy:
    """
    Feature: documentation-unification, Property 6: State Machine Documentation Accuracy
    
    For any state in DefaultState or OfferState enums, and for any valid transition
    in VALID_TRANSITIONS, the states.md documentation SHALL contain matching state
    definitions and transition diagrams.
    
    **Validates: Requirements 6.1, 6.2, 6.3, 6.5**
    """
    
    @pytest.fixture
    def states_md_path(self) -> Path:
        """Get the states.md path."""
        return Path(__file__).parent.parent / "docs" / "states.md"
    
    # =========================================================================
    # Requirement 6.1: DefaultState Documentation
    # =========================================================================
    
    def test_all_default_states_documented(self, states_md_path: Path):
        """
        Property 6: All DefaultState enum values should be documented.
        
        For any state in DefaultState enum, there SHALL exist a corresponding
        entry in docs/states.md.
        
        **Validates: Requirements 6.1**
        """
        if not states_md_path.exists():
            pytest.skip("states.md not found")
        
        # Get source states
        source_states = {s.value for s in DefaultState}
        
        # Get documented states
        doc_states = extract_documented_default_states(states_md_path)
        
        # Check all source states are documented
        missing_in_docs = source_states - doc_states
        
        assert len(missing_in_docs) == 0, (
            f"DefaultState values not documented in states.md: {sorted(missing_in_docs)}"
        )
    
    def test_no_extra_default_states_documented(self, states_md_path: Path):
        """
        Property 6: No extra default states should be documented.
        
        All documented default states SHALL exist in the DefaultState enum.
        
        **Validates: Requirements 6.1**
        """
        if not states_md_path.exists():
            pytest.skip("states.md not found")
        
        # Get source states
        source_states = {s.value for s in DefaultState}
        
        # Get documented states
        doc_states = extract_documented_default_states(states_md_path)
        
        # Check no extra states in docs
        extra_in_docs = doc_states - source_states
        
        assert len(extra_in_docs) == 0, (
            f"Extra default states documented but not in source: {sorted(extra_in_docs)}"
        )
    
    # =========================================================================
    # Requirement 6.2: OfferState Documentation
    # =========================================================================
    
    def test_all_offer_states_documented(self, states_md_path: Path):
        """
        Property 6: All OfferState enum values should be documented.
        
        For any state in OfferState enum, there SHALL exist a corresponding
        entry in docs/states.md.
        
        **Validates: Requirements 6.2**
        """
        if not states_md_path.exists():
            pytest.skip("states.md not found")
        
        # Get source states
        source_states = {s.value for s in OfferState}
        
        # Get documented states
        doc_states = extract_documented_offer_states(states_md_path)
        
        # Check all source states are documented
        missing_in_docs = source_states - doc_states
        
        assert len(missing_in_docs) == 0, (
            f"OfferState values not documented in states.md: {sorted(missing_in_docs)}"
        )
    
    def test_no_extra_offer_states_documented(self, states_md_path: Path):
        """
        Property 6: No extra offer states should be documented.
        
        All documented offer states SHALL exist in the OfferState enum.
        
        **Validates: Requirements 6.2**
        """
        if not states_md_path.exists():
            pytest.skip("states.md not found")
        
        # Get source states
        source_states = {s.value for s in OfferState}
        
        # Get documented states
        doc_states = extract_documented_offer_states(states_md_path)
        
        # Check no extra states in docs
        extra_in_docs = doc_states - source_states
        
        assert len(extra_in_docs) == 0, (
            f"Extra offer states documented but not in source: {sorted(extra_in_docs)}"
        )
    
    # =========================================================================
    # Requirement 6.3: Transition Documentation
    # =========================================================================
    
    def test_all_default_transitions_documented(self, states_md_path: Path):
        """
        Property 6: All valid default transitions should be documented.
        
        For any valid transition in DEFAULT_VALID_TRANSITIONS, there SHALL exist
        a corresponding entry in docs/states.md.
        
        **Validates: Requirements 6.3**
        """
        if not states_md_path.exists():
            pytest.skip("states.md not found")
        
        # Get source transitions
        source_transitions = extract_source_default_transitions()
        
        # Get documented transitions
        doc_transitions = extract_documented_default_transitions(states_md_path)
        
        # Check all source transitions are documented
        for from_state, to_states in source_transitions.items():
            doc_to_states = doc_transitions.get(from_state, set())
            missing = to_states - doc_to_states
            
            assert len(missing) == 0, (
                f"Default transitions from '{from_state}' not documented: "
                f"{sorted(missing)}"
            )
    
    def test_all_offer_transitions_documented(self, states_md_path: Path):
        """
        Property 6: All valid offer transitions should be documented.
        
        For any valid transition in OFFER_VALID_TRANSITIONS, there SHALL exist
        a corresponding entry in docs/states.md.
        
        **Validates: Requirements 6.3**
        """
        if not states_md_path.exists():
            pytest.skip("states.md not found")
        
        # Get source transitions
        source_transitions = extract_source_offer_transitions()
        
        # Get documented transitions
        doc_transitions = extract_documented_offer_transitions(states_md_path)
        
        # Check all source transitions are documented (except terminal state)
        for from_state, to_states in source_transitions.items():
            if len(to_states) == 0:  # Terminal state (rejected)
                continue
            
            doc_to_states = doc_transitions.get(from_state, set())
            missing = to_states - doc_to_states
            
            assert len(missing) == 0, (
                f"Offer transitions from '{from_state}' not documented: "
                f"{sorted(missing)}"
            )
    
    # =========================================================================
    # Requirement 6.5: State Diagram Accuracy
    # =========================================================================
    
    def test_default_state_diagram_exists(self, states_md_path: Path):
        """
        Property 6: Default state diagram should exist in documentation.
        
        The states.md documentation SHALL contain a Mermaid state diagram
        for the default state machine.
        
        **Validates: Requirements 6.5**
        """
        if not states_md_path.exists():
            pytest.skip("states.md not found")
        
        content = states_md_path.read_text()
        
        # Check for Mermaid state diagram
        assert "```mermaid" in content, "No Mermaid diagrams found in states.md"
        assert "stateDiagram-v2" in content, "No state diagram found in states.md"
        
        # Check for default state diagram section
        assert "Default State Diagram" in content, (
            "Default State Diagram section not found in states.md"
        )
    
    def test_offer_state_diagram_exists(self, states_md_path: Path):
        """
        Property 6: Offer state diagram should exist in documentation.
        
        The states.md documentation SHALL contain a Mermaid state diagram
        for the offer state machine.
        
        **Validates: Requirements 6.5**
        """
        if not states_md_path.exists():
            pytest.skip("states.md not found")
        
        content = states_md_path.read_text()
        
        # Check for offer state diagram section
        assert "Offer State Diagram" in content, (
            "Offer State Diagram section not found in states.md"
        )
    
    def test_default_diagram_contains_all_states(self, states_md_path: Path):
        """
        Property 6: Default state diagram should contain all states.
        
        The default state diagram SHALL reference all DefaultState values.
        
        **Validates: Requirements 6.5**
        """
        if not states_md_path.exists():
            pytest.skip("states.md not found")
        
        content = states_md_path.read_text()
        
        # Find the default state diagram section
        default_diagram_match = re.search(
            r'### Default State Diagram.*?```mermaid(.*?)```',
            content,
            re.DOTALL
        )
        
        assert default_diagram_match, "Default state diagram not found"
        
        diagram_content = default_diagram_match.group(1)
        
        # Check all states are referenced in the diagram
        for state in DefaultState:
            assert state.value in diagram_content.lower(), (
                f"State '{state.value}' not found in default state diagram"
            )
    
    def test_offer_diagram_contains_all_states(self, states_md_path: Path):
        """
        Property 6: Offer state diagram should contain all states.
        
        The offer state diagram SHALL reference all OfferState values.
        
        **Validates: Requirements 6.5**
        """
        if not states_md_path.exists():
            pytest.skip("states.md not found")
        
        content = states_md_path.read_text()
        
        # Find the offer state diagram section
        offer_diagram_match = re.search(
            r'### Offer State Diagram.*?```mermaid(.*?)```',
            content,
            re.DOTALL
        )
        
        assert offer_diagram_match, "Offer state diagram not found"
        
        diagram_content = offer_diagram_match.group(1)
        
        # Check all states are referenced in the diagram
        for state in OfferState:
            assert state.value in diagram_content.lower(), (
                f"State '{state.value}' not found in offer state diagram"
            )


# =============================================================================
# Property-Based Tests for State Machine Documentation
# =============================================================================


@st.composite
def default_state_strategy(draw):
    """Generate valid DefaultState values."""
    return draw(st.sampled_from(list(DefaultState)))


@st.composite
def offer_state_strategy(draw):
    """Generate valid OfferState values."""
    return draw(st.sampled_from(list(OfferState)))


@st.composite
def valid_default_transition_strategy(draw):
    """Generate valid default state transitions."""
    valid_pairs = []
    for from_state, to_states in DEFAULT_VALID_TRANSITIONS.items():
        for to_state in to_states:
            valid_pairs.append((from_state, to_state))
    return draw(st.sampled_from(valid_pairs))


@st.composite
def valid_offer_transition_strategy(draw):
    """Generate valid offer state transitions."""
    valid_pairs = []
    for from_state, to_states in OFFER_VALID_TRANSITIONS.items():
        for to_state in to_states:
            valid_pairs.append((from_state, to_state))
    if not valid_pairs:
        # Handle case where no valid transitions exist
        return (OfferState.NONE, OfferState.CREATED)
    return draw(st.sampled_from(valid_pairs))


class TestStateMachineDocAccuracyProperties:
    """
    Property-based tests for state machine documentation accuracy.
    
    Feature: documentation-unification, Property 6: State Machine Documentation Accuracy
    **Validates: Requirements 6.1, 6.2, 6.3, 6.5**
    """
    
    @given(state=default_state_strategy())
    @settings(max_examples=100)
    def test_default_state_is_documented(self, state: DefaultState):
        """
        Property 6: For any DefaultState, documentation should exist.
        
        For any state from the DefaultState enum, it SHALL be documented
        in docs/states.md.
        
        **Validates: Requirements 6.1**
        """
        states_md_path = Path(__file__).parent.parent / "docs" / "states.md"
        
        if not states_md_path.exists():
            return  # Skip if file doesn't exist
        
        doc_states = extract_documented_default_states(states_md_path)
        
        assert state.value in doc_states, (
            f"DefaultState '{state.value}' is not documented in states.md"
        )
    
    @given(state=offer_state_strategy())
    @settings(max_examples=100)
    def test_offer_state_is_documented(self, state: OfferState):
        """
        Property 6: For any OfferState, documentation should exist.
        
        For any state from the OfferState enum, it SHALL be documented
        in docs/states.md.
        
        **Validates: Requirements 6.2**
        """
        states_md_path = Path(__file__).parent.parent / "docs" / "states.md"
        
        if not states_md_path.exists():
            return  # Skip if file doesn't exist
        
        doc_states = extract_documented_offer_states(states_md_path)
        
        assert state.value in doc_states, (
            f"OfferState '{state.value}' is not documented in states.md"
        )
    
    @given(transition=valid_default_transition_strategy())
    @settings(max_examples=100)
    def test_default_transition_is_documented(
        self,
        transition: tuple[DefaultState, DefaultState],
    ):
        """
        Property 6: For any valid default transition, documentation should exist.
        
        For any valid transition from DEFAULT_VALID_TRANSITIONS, it SHALL be
        documented in docs/states.md.
        
        **Validates: Requirements 6.3**
        """
        states_md_path = Path(__file__).parent.parent / "docs" / "states.md"
        
        if not states_md_path.exists():
            return  # Skip if file doesn't exist
        
        from_state, to_state = transition
        doc_transitions = extract_documented_default_transitions(states_md_path)
        
        doc_to_states = doc_transitions.get(from_state.value, set())
        
        assert to_state.value in doc_to_states, (
            f"Default transition '{from_state.value}' -> '{to_state.value}' "
            f"is not documented in states.md"
        )
    
    @given(transition=valid_offer_transition_strategy())
    @settings(max_examples=100)
    def test_offer_transition_is_documented(
        self,
        transition: tuple[OfferState, OfferState],
    ):
        """
        Property 6: For any valid offer transition, documentation should exist.
        
        For any valid transition from OFFER_VALID_TRANSITIONS, it SHALL be
        documented in docs/states.md.
        
        **Validates: Requirements 6.3**
        """
        states_md_path = Path(__file__).parent.parent / "docs" / "states.md"
        
        if not states_md_path.exists():
            return  # Skip if file doesn't exist
        
        from_state, to_state = transition
        doc_transitions = extract_documented_offer_transitions(states_md_path)
        
        doc_to_states = doc_transitions.get(from_state.value, set())
        
        assert to_state.value in doc_to_states, (
            f"Offer transition '{from_state.value}' -> '{to_state.value}' "
            f"is not documented in states.md"
        )


# =============================================================================
# Integration Tests: Source Code Reference Validation
# =============================================================================


class TestSourceCodeReferences:
    """
    Tests that states.md contains accurate source code references.
    
    Feature: documentation-unification, Property 6: State Machine Documentation Accuracy
    **Validates: Requirements 6.5**
    """
    
    @pytest.fixture
    def states_md_path(self) -> Path:
        """Get the states.md path."""
        return Path(__file__).parent.parent / "docs" / "states.md"
    
    def test_default_source_code_reference_exists(self, states_md_path: Path):
        """
        Test that default state source code reference exists.
        
        The states.md documentation SHALL contain a reference to
        vince/state/default_state.py.
        """
        if not states_md_path.exists():
            pytest.skip("states.md not found")
        
        content = states_md_path.read_text()
        
        assert "vince/state/default_state.py" in content, (
            "Reference to vince/state/default_state.py not found in states.md"
        )
    
    def test_offer_source_code_reference_exists(self, states_md_path: Path):
        """
        Test that offer state source code reference exists.
        
        The states.md documentation SHALL contain a reference to
        vince/state/offer_state.py.
        """
        if not states_md_path.exists():
            pytest.skip("states.md not found")
        
        content = states_md_path.read_text()
        
        assert "vince/state/offer_state.py" in content, (
            "Reference to vince/state/offer_state.py not found in states.md"
        )
    
    def test_valid_transitions_code_block_exists(self, states_md_path: Path):
        """
        Test that VALID_TRANSITIONS code block exists.
        
        The states.md documentation SHALL contain code blocks showing
        the VALID_TRANSITIONS dictionaries.
        """
        if not states_md_path.exists():
            pytest.skip("states.md not found")
        
        content = states_md_path.read_text()
        
        assert "VALID_TRANSITIONS" in content, (
            "VALID_TRANSITIONS reference not found in states.md"
        )
