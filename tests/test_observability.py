"""Homework 2: authentication and the spans the endpoint records.

Everything here runs offline. No Langfuse, no Docker, no model provider key:
the spans go to an in-memory exporter and the agent run is stubbed. Reading
the real traces is Part E's job, in Langfuse.

Two groups of tests:

  - Authentication (Part D, required by the handout). The two places where a
    wrong answer lets a caller act as someone they are not.
  - Instrumentation (Parts A and C, kept as regression tests). The span
    attributes and the root-span nesting are invisible in the HTTP response,
    so without these they are only ever checked by eye in the Langfuse UI.
"""

from __future__ import annotations

import asyncio
import json

import pytest
from fastapi import HTTPException
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from agent.auth import AuthContext, permission_denied
from observability import instrument
from server import app as server_app

SHOPPER_1 = AuthContext(user_id=1, role="shopper")
MERCHANT_STORE_2 = AuthContext(user_id=9002, role="merchant", store_id=2)


@pytest.fixture
def sessions(tmp_path, monkeypatch):
    """Hand each test an empty session registry and its own .sessions.db.

    Both are module-level names that create_session and _authorize resolve at
    call time, so monkeypatch swaps them without touching production code and
    restores them afterwards. Without this, tests would share the process-wide
    registry and write api-* tables into the repo's real .sessions.db.
    """
    monkeypatch.setattr(server_app, "SESSIONS_DB", tmp_path / "sessions.db")
    monkeypatch.setattr(server_app, "_SESSIONS", {})
    return server_app._SESSIONS


@pytest.fixture
def spans():
    """A real tracer provider that records finished spans into memory."""
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    try:
        yield provider, exporter
    finally:
        provider.shutdown()


# ---------------------------------------------------------------------------
# Part D: authentication
# ---------------------------------------------------------------------------


def test_create_session_rejects_role_the_database_disagrees_with(world, sessions) -> None:
    """A claimed role never overrides the stored one.

    User 9002 is a merchant. Asking for a shopper session must fail, because
    identity comes from the database row and not from the request body.
    """
    with pytest.raises(HTTPException) as exc:
        server_app.create_session(
            server_app.SessionCreate(user_id=9002, role="shopper")
        )

    assert exc.value.status_code == 403
    # A rejected request must not leave a usable session behind.
    assert sessions == {}


def test_token_does_not_authorize_another_session(world, sessions) -> None:
    """A token is scoped to the session it was issued for.

    The allowed case is asserted first on purpose: a broken _authorize that
    rejected everything would satisfy the rejection half all by itself.
    """
    shopper = server_app.create_session(
        server_app.SessionCreate(user_id=1, role="shopper")
    )
    merchant = server_app.create_session(
        server_app.SessionCreate(user_id=9002, role="merchant")
    )

    ctx = server_app._authorize(
        merchant["session_id"], f"Bearer {merchant['token']}"
    )
    assert ctx.user_id == 9002 and ctx.role == "merchant"

    with pytest.raises(HTTPException) as exc:
        server_app._authorize(
            merchant["session_id"], f"Bearer {shopper['token']}"
        )
    assert exc.value.status_code == 403


# ---------------------------------------------------------------------------
# Part A: application attributes on tool spans
# ---------------------------------------------------------------------------


def test_tool_span_records_allowed_caller(spans) -> None:
    provider, exporter = spans
    with provider.get_tracer("test").start_as_current_span("get_order"):
        instrument.record_tool_result(SHOPPER_1, {"ok": True, "order_id": 4127})

    attrs = exporter.get_finished_spans()[0].attributes
    assert attrs["cartwheel.user_role"] == "shopper"
    # The decimal id lives in a string, so it is never truncated by a
    # consumer that reads span attributes as numbers.
    assert attrs["cartwheel.user_id"] == "1"
    assert attrs["cartwheel.permission_denied"] is False
    # Absent, not empty: a shopper has no store, and no denial has a reason.
    assert "cartwheel.store_id" not in attrs
    assert "cartwheel.permission_denied.reason" not in attrs


def test_tool_span_records_denial_and_store(spans) -> None:
    provider, exporter = spans
    reason = "order belongs to another store"
    with provider.get_tracer("test").start_as_current_span("get_order"):
        instrument.record_tool_result(MERCHANT_STORE_2, permission_denied(reason))

    attrs = exporter.get_finished_spans()[0].attributes
    assert attrs["cartwheel.store_id"] == 2
    assert isinstance(attrs["cartwheel.store_id"], int)
    assert attrs["cartwheel.permission_denied.reason"] == reason

    # `is True`, not `== True`: an accidental 1 or "true" would pass equality.
    # It has to survive as a real boolean, because reports/smoke.sql (HW3)
    # counts denials with JSONExtractString(...) = 'true' against the
    # serialized attributes.
    assert attrs["cartwheel.permission_denied"] is True
    assert '"cartwheel.permission_denied": true' in json.dumps(dict(attrs))


# ---------------------------------------------------------------------------
# Part C: the root span wraps the agent run
# ---------------------------------------------------------------------------


def _ancestor_ids(span, finished):
    """Yield span ids from `span`'s parent up to the root of its trace.

    A ReadableSpan knows only its immediate parent, so climbing the tree means
    rebuilding it from the exported spans. Stops when a parent is missing from
    `finished`, which keeps a partially exported trace from looping forever.
    """
    by_id = {s.context.span_id: s for s in finished}
    cursor = span.parent
    while cursor is not None:
        yield cursor.span_id
        parent = by_id.get(cursor.span_id)
        cursor = parent.parent if parent is not None else None


def _stub_runner(provider):
    """Stand in for the SDK runner, emitting the child span OpenLLMetry would.

    The real Runner.run needs a model provider key. What matters for Part C is
    only that whatever spans are created during the run land under the root
    span, so a stub that creates one child is enough to catch the regression:
    move Runner.run outside the `with` block and the nesting check below is
    the only assertion in this file that notices.
    """

    class StubResult:
        final_output = "Here are your recent orders."

    class StubRunner:
        @staticmethod
        async def run(agent, message, **kwargs):
            tracer = provider.get_tracer("stub.openllmetry")
            with tracer.start_as_current_span("openai.response") as child:
                child.set_attribute("gen_ai.operation.name", "chat")
            return StubResult()

    return StubRunner


def test_root_span_parents_the_agent_spans(world, sessions, spans, monkeypatch) -> None:
    provider, exporter = spans
    monkeypatch.setattr(server_app, "_tracer", provider.get_tracer("cartwheel.server"))
    monkeypatch.setattr(server_app, "Runner", _stub_runner(provider))
    # Part C records the message attributes only when content capture is on.
    monkeypatch.setenv("TRACELOOP_TRACE_CONTENT", "true")

    created = server_app.create_session(
        server_app.SessionCreate(user_id=1, role="shopper")
    )
    response = asyncio.run(
        server_app.post_message(
            created["session_id"],
            server_app.MessageIn(message="Show my recent orders."),
            authorization=f"Bearer {created['token']}",
        )
    )

    finished = {span.name: span for span in exporter.get_finished_spans()}
    root = finished["cartwheel.session_message"]
    child = finished["openai.response"]

    assert response["reply"] == "Here are your recent orders."
    assert root.attributes["cartwheel.user_role"] == "shopper"
    assert root.attributes["cartwheel.user_id"] == "1"
    assert root.attributes["cartwheel.prompt_version"] == response["prompt_version"]
    # Not supplied by this request, so it must be absent rather than null.
    assert "cartwheel.scenario_id" not in root.attributes

    messages = json.loads(root.attributes["gen_ai.input.messages"])
    assert messages == [
        {"role": "user", "parts": [{"type": "text", "content": "Show my recent orders."}]}
    ]
    replies = json.loads(root.attributes["gen_ai.output.messages"])
    assert replies[0]["role"] == "assistant"
    assert replies[0]["parts"][0]["content"] == "Here are your recent orders."
    # The agent's spans must sit underneath the request span, so Langfuse draws
    # one tree per request. Assert descent rather than a direct parent link:
    # against real OpenLLMetry an "Agent Workflow" span sits between the two,
    # and a direct-parent check would fail on a correctly nested tree.
    assert child.context.trace_id == root.context.trace_id
    assert root.context.span_id in set(_ancestor_ids(child, exporter.get_finished_spans()))
    # And the request span is itself the top of that trace.
    assert root.parent is None
