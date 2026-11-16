import unittest
from unittest.mock import patch

from config import Router
from grafo import (
    EmailInput,
    EmailState,
    email_agent,
    human_in_the_loop_schedule,
    triage_router,
)
from tools import schedule_meeting


SAMPLE_EMAIL: EmailInput = {
    "from": "Alice Smith <alice.smith@company.com>",
    "to": "Sarah Chen <sarah.chen@company.com>",
    "subject": "Acompanhamento",
    "body": "Como está minha solicitação?",
}


class EmailGraphTests(unittest.TestCase):
    @patch("grafo.llm_router")
    def test_ignore_classification_ends_the_graph(self, mock_router):
        mock_router.invoke.return_value = Router(
            reasoning="Mensagem informativa sem ação.",
            classification="ignore",
        )

        state: EmailState = {"email_input": SAMPLE_EMAIL}
        result = email_agent.invoke(state)

        self.assertEqual(result["next_step"], "end")
        self.assertEqual(result.get("messages"), [])

    @patch("grafo.llm_router")
    def test_respond_classification_creates_an_agent_message(self, mock_router):
        mock_router.invoke.return_value = Router(
            reasoning="O remetente fez uma pergunta direta.",
            classification="respond",
        )

        state: EmailState = {"email_input": SAMPLE_EMAIL}
        result = triage_router(state)

        self.assertEqual(result.get("next_step"), "respond")
        messages = result.get("messages", [])
        self.assertIn("Alice Smith", str(getattr(messages[0], "content", "")))

    def test_schedule_tool_accepts_meeting_duration(self):
        result = schedule_meeting.invoke(
            {
                "attendees": ["Alice Smith", "Sarah Chen"],
                "subject": "Acompanhamento",
                "duration_minutes": 30,
                "preferred_day": "amanhã",
            }
        )

        self.assertIn("30 minutos", result)

    @patch("grafo.write_email")
    @patch("grafo.search_memory_tool")
    def test_existing_meeting_memory_skips_confirmation_prompt(
        self,
        mock_search,
        mock_email,
    ):
        mock_search.invoke.return_value = ([{"content": "Reunião agendada"}], [])
        mock_email.invoke.return_value = "e-mail preparado"

        with patch("builtins.input", side_effect=AssertionError("Prompt inesperado")):
            human_in_the_loop_schedule(
                SAMPLE_EMAIL["from"],
                SAMPLE_EMAIL["to"],
                SAMPLE_EMAIL["subject"],
            )

        mock_email.invoke.assert_called_once()


if __name__ == "__main__":
    unittest.main()
