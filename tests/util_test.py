import pytest

from streetlevel import util


@pytest.mark.asyncio
async def test_download_files_async_closes_created_session_after_error(monkeypatch):
    class FakeSession:
        closed = False

        def get(self, url, headers=None):
            raise RuntimeError("request failed")

        async def close(self):
            self.closed = True

    session = FakeSession()
    monkeypatch.setattr(util, "ClientSession", lambda: session)

    with pytest.raises(RuntimeError, match="request failed"):
        await util.download_files_async(["https://example.com/file"])

    assert session.closed
