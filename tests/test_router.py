"""Tests for src/router.py — Foundry Agent intent router."""

import pytest

from src.router import (
    ROUTING_RULES,
    FoundryRouter,
    IntentCategory,
    RoutingRule,
    route_intent,
)
from src.agents import AGENT_REGISTRY


@pytest.fixture
def router():
    return FoundryRouter()


class TestRoutingRules:
    """Verify routing rules structure."""

    def test_rules_cover_all_intents_except_unknown(self):
        covered = {r.intent for r in ROUTING_RULES}
        all_intents = set(IntentCategory) - {IntentCategory.UNKNOWN}
        assert covered == all_intents

    def test_every_rule_has_keywords(self):
        for rule in ROUTING_RULES:
            assert len(rule.keywords) >= 3, (
                f"Rule {rule.intent.value} has too few keywords"
            )

    def test_every_rule_agent_exists(self):
        agent_names = {a.name for a in AGENT_REGISTRY}
        for rule in ROUTING_RULES:
            assert rule.agent_name in agent_names, (
                f"Rule {rule.intent.value} references unknown agent '{rule.agent_name}'"
            )


class TestClassifyIntent:
    """Intent classification from user input."""

    @pytest.mark.parametrize("input_text, expected_intent", [
        # English keywords -- inventory
        ("check inventory status", IntentCategory.INVENTORY_QUERY),
        ("stock level for pineapple", IntentCategory.INVENTORY_QUERY),
        ("supplier inventory report", IntentCategory.INVENTORY_QUERY),
        # English keywords -- knowledge
        ("search knowledge base", IntentCategory.KNOWLEDGE_SEARCH),
        ("FAQ troubleshoot guide", IntentCategory.KNOWLEDGE_SEARCH),
        # English keywords -- bug fix
        ("fix the code bug", IntentCategory.BUG_FIX),
        ("error in API timeout", IntentCategory.BUG_FIX),
        # English keywords -- external search
        ("weather forecast today", IntentCategory.EXTERNAL_SEARCH),
        ("news search Bing", IntentCategory.EXTERNAL_SEARCH),
        # English keywords -- logistics
        ("logistics tracking ETA", IntentCategory.LOGISTICS_TRACK),
        ("shipping tracking status", IntentCategory.LOGISTICS_TRACK),
        # English keywords -- system health
        ("system health monitor check", IntentCategory.SYSTEM_HEALTH),
        ("Azure log metrics alert", IntentCategory.SYSTEM_HEALTH),
        # English keywords -- incident report
        ("generate incident report", IntentCategory.INCIDENT_REPORT),
        ("summary report incident", IntentCategory.INCIDENT_REPORT),
        # English keywords -- meeting booking
        ("book a meeting on calendar", IntentCategory.MEETING_BOOKING),
        ("schedule meeting Teams", IntentCategory.MEETING_BOOKING),
    ])
    def test_intent_classification(self, router, input_text, expected_intent):
        intent, confidence = router.classify_intent(input_text)
        assert intent == expected_intent, (
            f"Input '{input_text}' classified as {intent.value}, "
            f"expected {expected_intent.value}"
        )

    def test_unknown_input(self, router):
        intent, confidence = router.classify_intent("asdlkfjasldkf random gibberish")
        assert intent == IntentCategory.UNKNOWN
        assert confidence == 0.0

    def test_empty_input(self, router):
        intent, confidence = router.classify_intent("")
        assert intent == IntentCategory.UNKNOWN

    def test_confidence_in_range(self, router):
        for text in ["inventory", "knowledge", "weather", "logistics", "health monitor", "report", "meeting"]:
            _, confidence = router.classify_intent(text)
            assert 0.0 <= confidence <= 1.0

    def test_more_keywords_higher_confidence(self, router):
        _, conf_single = router.classify_intent("inventory")
        _, conf_multi = router.classify_intent("inventory stock pineapple supplier")
        assert conf_multi >= conf_single


class TestRoute:
    """Full routing: input → agent."""

    def test_route_inventory(self, router):
        agent, intent, conf = router.route("check inventory stock")
        assert agent is not None
        assert agent.name == "inventory-agent"
        assert intent == IntentCategory.INVENTORY_QUERY

    def test_route_knowledge(self, router):
        agent, intent, _ = router.route("search knowledge base FAQ")
        assert agent is not None
        assert agent.name == "knowledge-agent"

    def test_route_bugfix(self, router):
        agent, intent, _ = router.route("fix the bug in code")
        assert agent is not None
        assert agent.name == "coding-agent"

    def test_route_weather(self, router):
        agent, intent, _ = router.route("weather forecast search")
        assert agent is not None
        assert agent.name == "search-agent"

    def test_route_logistics(self, router):
        agent, intent, _ = router.route("logistics tracking ETA")
        assert agent is not None
        assert agent.name == "logistics-agent"

    def test_route_health(self, router):
        agent, intent, _ = router.route("system health monitor Azure")
        assert agent is not None
        assert agent.name == "sre-agent"

    def test_route_report(self, router):
        agent, intent, _ = router.route("generate incident report summary")
        assert agent is not None
        assert agent.name == "copilot-agent"

    def test_route_meeting(self, router):
        agent, intent, _ = router.route("schedule a meeting Teams")
        assert agent is not None
        assert agent.name == "copilot-agent"

    def test_route_unknown_returns_none(self, router):
        agent, intent, conf = router.route("lorem ipsum dolor sit amet")
        assert agent is None
        assert intent == IntentCategory.UNKNOWN

    def test_route_with_explanation_found(self, router):
        text = router.route_with_explanation("check inventory stock")
        assert "Routing Result" in text or "\u0001f500" in text or "inventory" in text.lower()

    def test_route_with_explanation_unknown(self, router):
        text = router.route_with_explanation("random gibberish")
        assert "Unable to classify" in text or "\u26a0" in text or "unable" in text.lower()


class TestChineseKeywords:
    """Verify Chinese keywords are correctly classified."""

    @pytest.mark.parametrize("input_text, expected_intent", [
        ("查詢庫存狀態", IntentCategory.INVENTORY_QUERY),
        ("鳳梨酥存貨多少", IntentCategory.INVENTORY_QUERY),
        ("缺貨補貨供應商", IntentCategory.INVENTORY_QUERY),
        ("知識庫搜尋FAQ", IntentCategory.KNOWLEDGE_SEARCH),
        ("文件怎麼辦", IntentCategory.KNOWLEDGE_SEARCH),
        ("修復程式碼bug", IntentCategory.BUG_FIX),
        ("天氣颱風航班", IntentCategory.EXTERNAL_SEARCH),
        ("物流貨運追蹤", IntentCategory.LOGISTICS_TRACK),
        ("系統健康監控", IntentCategory.SYSTEM_HEALTH),
        ("產生事件報告", IntentCategory.INCIDENT_REPORT),
        ("排會議行事曆", IntentCategory.MEETING_BOOKING),
    ])
    def test_chinese_keyword_classification(self, router, input_text, expected_intent):
        intent, confidence = router.classify_intent(input_text)
        assert intent == expected_intent, (
            f"Chinese input '{input_text}' classified as {intent.value}, "
            f"expected {expected_intent.value}"
        )


class TestMixedLanguageInput:
    """Verify mixed Chinese + English input is handled."""

    @pytest.mark.parametrize("input_text, expected_intent", [
        ("查一下 inventory stock", IntentCategory.INVENTORY_QUERY),
        ("FAQ 知識庫 troubleshoot", IntentCategory.KNOWLEDGE_SEARCH),
        ("fix 程式碼 error", IntentCategory.BUG_FIX),
        ("天氣 weather forecast", IntentCategory.EXTERNAL_SEARCH),
        ("物流 logistics tracking", IntentCategory.LOGISTICS_TRACK),
        ("system 系統 health monitor", IntentCategory.SYSTEM_HEALTH),
        ("incident 事件 report 報告", IntentCategory.INCIDENT_REPORT),
        ("meeting 會議 schedule", IntentCategory.MEETING_BOOKING),
    ])
    def test_mixed_language_routing(self, router, input_text, expected_intent):
        intent, confidence = router.classify_intent(input_text)
        assert intent == expected_intent, (
            f"Mixed input '{input_text}' classified as {intent.value}, "
            f"expected {expected_intent.value}"
        )


class TestModuleLevelRouter:
    """Test the module-level route_intent function."""

    def test_route_intent_function(self):
        agent, intent, conf = route_intent("check inventory stock")
        assert agent is not None
        assert intent == IntentCategory.INVENTORY_QUERY
