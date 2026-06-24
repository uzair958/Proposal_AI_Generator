from app.agents.writer_agent import writer_agent


def test_writer_agent_outputs_structure():

    result = writer_agent(
        {
            "client_profile": {
                "industry": "healthcare",
                "problem": "inventory delays"
            },
            "retrieved_context": ["sample context"]
        }
    )

    assert "proposal_sections" in result
    assert result["proposal_sections"] is not None