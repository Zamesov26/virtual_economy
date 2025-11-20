import pytest


@pytest.mark.anyio
class TestAuthRegister:
    async def test_success(self, client):
        payload = {
            "username": "TestUser",
            "email": "TestUser@Example.Com",
            "password": "123456",
        }

        response = await client.post("api/v1/auth/register", json=payload)

        assert response.status_code == 201

        data = response.json()

        assert data["username"] == "testuser"
        assert data["email"] == "testuser@example.com"
        assert "id" in data

    @pytest.mark.parametrize(
        ("username", "email", "message"),
        (
            ("user", "email@example.com", "Email already registered"),
            ("other_name", "email@example.com", "Email already registered"),
            ("user", "other_mail@example.com", "Username already taken"),
        ),
    )
    async def test_conflict_when_user_already_exists(
        self, client, username, email, message
    ):
        await client.post(
            "api/v1/auth/register",
            json={
                "username": "User",
                "email": "email@example.com",
                "password": "123456",
            },
        )

        resp = await client.post(
            "api/v1/auth/register",
            json={"username": username, "email": email, "password": "123456"},
        )

        assert resp.status_code == 409
        assert resp.json()["detail"] == message

    @pytest.mark.parametrize(
        "invalid_data",
        (
            {"email": "invalid_email"},
            {"password": "123"},
            {"username": "FK"},
        ),
    )
    async def test_bad_request(self, client, invalid_data):
        data = {
            "username": "user123",
            "email": "email@example.com",
            "password": "123456",
        }
        data.update(invalid_data)
        resp = await client.post(
            "api/v1/auth/register",
            json=data,
        )

        assert resp.status_code == 422
