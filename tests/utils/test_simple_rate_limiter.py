import pytest


@pytest.mark.anyio
async def test_rate_limit(client, redis_mock):
    url = "/api/v1/test-rate"

    assert (await client.get(url)).status_code == 200
    assert (await client.get(url)).status_code == 200
    assert (await client.get(url)).status_code == 200
    assert (await client.get(url)).status_code == 429
