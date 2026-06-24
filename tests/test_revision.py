from app.workflows.revision_graph import revision_graph


def test_revision_flow():

    result = revision_graph.invoke(
        {
            "db": None,
            "session_id": 1,
            "slack_user_id": "test",
            "channel_id": "test",
            "revision_request": "Make timeline more detailed",
        }
    )

    assert "proposal_sections" in result
    assert result["proposal_sections"] is not None