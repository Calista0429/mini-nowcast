"""Agent behaviour with a scripted fake LLM: no network, deterministic."""
import pandas as pd

from assistant.agent import Assistant
from assistant.llm import JSONReply, Usage


class FakeLLM:
    model = "fake"

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def complete_json(self, system, messages):
        self.calls.append(messages)
        return JSONReply(self.replies.pop(0), Usage(10, 5))


def fake_db(sql):
    return pd.DataFrame({"month": ["2011-10-01", "2011-11-01"], "revenue_gbp": [1000.0, 1250.0]})


def plan(sql):
    return {"sql": sql, "chart": {"type": "bar", "x": "month", "y": "revenue_gbp"}, "assumptions": []}


GOOD_SQL = "select month, revenue_gbp from marts.mart_sales_daily"


def test_rejected_sql_is_fed_back_and_corrected():
    llm = FakeLLM([
        plan("select * from raw.online_retail"),
        plan(GOOD_SQL),
        {"answer": "Revenue was 1250.", "cited_numbers": [{"text": "1250", "value": 1250, "derived": False}]},
    ])
    res = Assistant(llm=llm, run_sql=fake_db, log_path=None).ask("revenue?")
    assert res.ok and len(res.attempts) == 2
    assert "not allowed" in res.attempts[0].error
    assert "not allowed" in llm.calls[1][-1]["content"]  # error message went back to the model


def test_gives_up_after_max_attempts():
    llm = FakeLLM([plan("drop table x")] * 3)
    res = Assistant(llm=llm, run_sql=fake_db, log_path=None).ask("break it")
    assert not res.ok and "No valid query" in res.error


def test_declines_unanswerable_question():
    llm = FakeLLM([{"sql": None, "cannot_answer_reason": "no weather data"}])
    res = Assistant(llm=llm, run_sql=fake_db, log_path=None).ask("weather?")
    assert res.declined_reason == "no weather data" and res.rows is None


def test_flags_numbers_not_in_the_result():
    llm = FakeLLM([
        plan(GOOD_SQL),
        {
            "answer": "Revenue rose 25% to 1250, beating the 900 target.",
            "cited_numbers": [
                {"text": "25%", "value": 0.25, "derived": True},    # 1250/1000 - 1
                {"text": "1250", "value": 1250, "derived": False},  # a cell
                {"text": "900", "value": 900, "derived": False},    # invented
            ],
        },
    ])
    res = Assistant(llm=llm, run_sql=fake_db, log_path=None).ask("growth?")
    assert [n.text for n in res.cited_numbers if n.verified] == ["25%", "1250"]
    assert [n.text for n in res.unverified_numbers] == ["900"]
