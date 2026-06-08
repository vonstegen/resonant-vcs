"""Tests for AI module."""

import pytest
from resonant_vcs.ai.intent import IntentClassifier, VCSIntent


def test_intent_classifier_add():
    """Test classifying 'add' intent."""
    classifier = IntentClassifier()
    
    result = classifier.classify("add test.txt")
    assert result.intent == VCSIntent.ADD
    assert result.confidence > 0

def test_intent_classifier_commit():
    """Test classifying 'commit' intent."""
    classifier = IntentClassifier()
    
    result = classifier.classify("commit this")
    assert result.intent == VCSIntent.COMMIT
    assert result.confidence > 0

def test_intent_classifier_log():
    """Test classifying 'log' intent."""
    classifier = IntentClassifier()
    
    result = classifier.classify("show me the history")
    assert result.intent == VCSIntent.LOG
    assert result.confidence > 0

def test_intent_classifier_status():
    """Test classifying 'status' intent."""
    classifier = IntentClassifier()
    
    result = classifier.classify("what changed")
    assert result.intent == VCSIntent.STATUS
    assert result.confidence > 0

def test_intent_classifier_branch():
    """Test classifying branch intent."""
    classifier = IntentClassifier()
    
    result = classifier.classify("create a new branch")
    assert result.intent == VCSIntent.BRANCH_CREATE
    assert result.confidence > 0

def test_intent_classifier_unknown():
    """Test classifying unknown intent."""
    classifier = IntentClassifier()
    
    result = classifier.classify("make me a sandwich")
    assert result.intent == VCSIntent.UNKNOWN
    assert result.confidence == 0

def test_intent_classifier_entities():
    """Test entity extraction."""
    classifier = IntentClassifier()
    
    result = classifier.classify("add myfile.py")
    assert "myfile.py" in result.entities.get("file", "")

def test_intent_classifier_branch_name():
    """Test branch name extraction."""
    classifier = IntentClassifier()
    
    result = classifier.classify("create branch feature-login")
    assert "feature-login" in result.entities.get("branch_name", "")