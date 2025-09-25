import pytest
from src.edal.signal_emitter import SignalEmitter

@pytest.mark.asyncio
async def test_emit_to_kinesis(monkeypatch):
    emitter = SignalEmitter()
    # Monkeypatch kinesis to avoid real calls
    async def fake_put_record(**kwargs): return {"ShardId":"1"}
    monkeypatch.setattr("aioboto3.Session.client", lambda *a,**k: FakeClient(fake_put_record))
    payload={"host":"h","metric":1}
    await emitter.emit(payload)

class FakeClient:
    def __init__(self, fn): self.fn=fn
    async def __aenter__(self): return self
    async def __aexit__(self,*a): return False
    async def put_record(self,**k): return await self.fn(**k)
