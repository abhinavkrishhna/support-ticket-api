from app.models import TicketPriority
from app.triage import TicketClassifier


def test_classifier_routes_login_failure_to_identity_operations() -> None:
    classifier = TicketClassifier()

    recommendation = classifier.suggest("My password reset link expired and I cannot sign in")

    assert recommendation.category == "access"
    assert recommendation.team == "identity-operations"
    assert recommendation.priority is TicketPriority.HIGH
    assert "password" in recommendation.matched_terms
    assert 0 < recommendation.match_score <= 1


def test_urgent_ticket_gets_urgent_priority() -> None:
    recommendation = TicketClassifier().suggest("The ETL data export did not arrive", urgent=True)

    assert recommendation.category == "data_pipeline"
    assert recommendation.priority is TicketPriority.URGENT


def test_ticket_with_no_matching_words_goes_to_general_support() -> None:
    recommendation = TicketClassifier().suggest("Need help with something", urgent=False)

    assert recommendation.category == "general"
    assert recommendation.team == "support-desk"
    assert recommendation.match_score == 0.0
