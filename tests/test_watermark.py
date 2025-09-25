import pytest, asyncio
from src.edal.watermark import WatermarkStore
from src.edal.config import settings

@pytest.mark.asyncio
async def test_watermark_cycle():
    wm = WatermarkStore()
    await wm.update_object_watermark("bucket","key","md5")
    res = await wm.get_object_watermark("bucket","key")
    assert res["md5"]=="md5"
