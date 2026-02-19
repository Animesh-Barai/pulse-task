import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    async def test_health_check_returns_200(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200

    async def test_health_check_returns_json(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.headers["content-type"] == "application/json"

    async def test_health_check_returns_status_healthy(self, client: AsyncClient):
        response = await client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

    async def test_root_endpoint_returns_200(self, client: AsyncClient):
        response = await client.get("/")
        assert response.status_code == 200

    async def test_root_endpoint_returns_welcome_message(self, client: AsyncClient):
        response = await client.get("/")
        data = response.json()
        assert "message" in data
        assert "PulseTasks" in data["message"]
        assert "version" in data
        assert data["version"] == "1.0.0"

    async def test_root_endpoint_includes_docs_link(self, client: AsyncClient):
        response = await client.get("/")
        data = response.json()
        assert "docs" in data
        assert data["docs"] == "/docs"

    async def test_cors_headers_present(self, client: AsyncClient):
        response = await client.get("/")
        assert response.status_code == 200
