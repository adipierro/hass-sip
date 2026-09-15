"""IVR lifecycle regression tests."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

from test_pure import _load_component_module


ivr = _load_component_module("ivr")


def _session(*, trigger_assist=None):
    return ivr.IvrSession(
        MagicMock(),
        {"timeout": 3600},
        play_message_fn=AsyncMock(),
        play_audio_file_fn=AsyncMock(),
        hangup_fn=MagicMock(),
        fire_event_fn=MagicMock(),
        trigger_assist_fn=trigger_assist or AsyncMock(),
    )


def test_close_cancels_timeout_without_rearming_it():
    async def run():
        session = _session()
        session._start_dtmf_collection()
        original = session.timeout_task
        assert original is not None
        session.close()
        await asyncio.sleep(0)
        return session.timeout_task, original.cancelled()

    timeout_task, cancelled = asyncio.run(run())
    assert timeout_task is None
    assert cancelled


def test_assist_handoff_does_not_leave_an_ivr_timeout():
    async def run():
        trigger = AsyncMock()
        session = _session(trigger_assist=trigger)
        session._start_dtmf_collection()
        await session._execute_choice({"assist": True})
        await asyncio.sleep(0)
        return session.timeout_task, trigger

    timeout_task, trigger = asyncio.run(run())
    assert timeout_task is None
    trigger.assert_awaited_once()
