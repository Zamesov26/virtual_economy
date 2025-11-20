import pytest
from httpx import AsyncClient


@pytest.mark.anyio
class TestHealth:
    async def test_should_return_healthy_status_when_getting_health_endpoint(
        self, client: AsyncClient
    ):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert data == {"status": "healthy", "message": "FastAPI service is running"}
