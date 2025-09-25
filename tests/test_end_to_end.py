import pytest, asyncio
from src.edal.main import main

@pytest.mark.asyncio
async def test_main_runs():
    await main()  # Just checks no crash
