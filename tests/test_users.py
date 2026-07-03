from httpx import AsyncClient
from sqlalchemy import select

from app.api.dependencies import get_current_superuser, get_current_user
from app.core.security import verify_password
from app.main import app
from app.models.user import User


async def test_get_current_logged_user(async_client: AsyncClient, create_test_user):
    user = await create_test_user(email="me@test.com")
    app.dependency_overrides[get_current_user] = lambda: user

    response = await async_client.get("/users/me")

    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"
    app.dependency_overrides.pop(get_current_user)


async def test_change_password_success(
    async_client: AsyncClient, create_test_user, db_session
):
    user = await create_test_user(email="pass1@test.com")
    app.dependency_overrides[get_current_user] = lambda: user

    payload = {"old_password": "secret123", "new_password": "new_secure_password"}

    response = await async_client.patch("/users/me/password", json=payload)

    assert response.status_code == 200
    assert response.json()["msg"] == "Password updated successfully"

    await db_session.refresh(user)
    assert verify_password("new_secure_password", user.hashed_password) is True

    app.dependency_overrides.pop(get_current_user)


async def test_change_password_wrong_old(async_client: AsyncClient, create_test_user):
    user = await create_test_user(email="pass2@test.com")
    app.dependency_overrides[get_current_user] = lambda: user

    payload = {"old_password": "wrongpassword", "new_password": "new_secure_password"}

    response = await async_client.patch("/users/me/password", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid old password"
    app.dependency_overrides.pop(get_current_user)


async def test_delete_my_account(
    async_client: AsyncClient, create_test_user, db_session
):
    user = await create_test_user(email="delete_me@test.com")
    app.dependency_overrides[get_current_user] = lambda: user

    response = await async_client.delete("/users/me/")

    assert response.status_code == 200
    await db_session.refresh(user)
    assert user.is_active is False
    app.dependency_overrides.pop(get_current_user)


async def test_get_all_users_as_superuser(async_client: AsyncClient, create_test_user):
    admin = await create_test_user(email="admin_all@test.com", is_superuser=True)
    await create_test_user(email="user_all@test.com")
    app.dependency_overrides[get_current_superuser] = lambda: admin

    response = await async_client.get("/users/")

    assert response.status_code == 200
    assert len(response.json()) >= 2
    app.dependency_overrides.pop(get_current_superuser)


async def test_get_user_by_id(async_client: AsyncClient, create_test_user):
    admin = await create_test_user(email="admin_id@test.com", is_superuser=True)
    target_user = await create_test_user(email="target_id@test.com")
    app.dependency_overrides[get_current_superuser] = lambda: admin

    response = await async_client.get(f"/users/{target_user.id}")

    assert response.status_code == 200
    assert response.json()["email"] == "target_id@test.com"
    app.dependency_overrides.pop(get_current_superuser)


async def test_update_user_status_by_admin(
    async_client: AsyncClient, create_test_user, db_session
):
    admin = await create_test_user(email="admin_status@test.com", is_superuser=True)
    target_user = await create_test_user(email="ban_me@test.com")
    app.dependency_overrides[get_current_superuser] = lambda: admin

    response = await async_client.patch(f"/users/{target_user.id}/status")

    assert response.status_code == 200
    await db_session.refresh(target_user)
    assert target_user.is_active is False
    app.dependency_overrides.pop(get_current_superuser)


async def test_admin_cannot_disable_another_admin(
    async_client: AsyncClient, create_test_user
):
    admin1 = await create_test_user(email="admin1_dis@test.com", is_superuser=True)
    admin2 = await create_test_user(email="admin2_dis@test.com", is_superuser=True)
    app.dependency_overrides[get_current_superuser] = lambda: admin1

    response = await async_client.patch(f"/users/{admin2.id}/status")

    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot change status of a superuser"
    app.dependency_overrides.pop(get_current_superuser)


async def test_hard_delete_user_by_admin(
    async_client: AsyncClient, create_test_user, db_session
):
    admin = await create_test_user(email="admin_hard@test.com", is_superuser=True)
    target_user = await create_test_user(email="hard_delete@test.com")
    app.dependency_overrides[get_current_superuser] = lambda: admin

    response = await async_client.delete(f"/users/{target_user.id}")

    assert response.status_code == 200

    query = await db_session.execute(select(User).where(User.id == target_user.id))
    deleted_user = query.scalar_one_or_none()
    assert deleted_user is None

    app.dependency_overrides.pop(get_current_superuser)


async def test_get_user_by_id_not_found(async_client: AsyncClient, create_test_user):
    admin = await create_test_user(email="admin_get_404@test.com", is_superuser=True)
    app.dependency_overrides[get_current_superuser] = lambda: admin

    response = await async_client.get("/users/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

    app.dependency_overrides.pop(get_current_superuser)


async def test_update_user_status_not_found(
    async_client: AsyncClient, create_test_user
):
    admin = await create_test_user(email="admin_status_404@test.com", is_superuser=True)
    app.dependency_overrides[get_current_superuser] = lambda: admin

    response = await async_client.patch("/users/99999/status")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

    app.dependency_overrides.pop(get_current_superuser)


async def test_hard_delete_user_not_found(async_client: AsyncClient, create_test_user):
    admin = await create_test_user(email="admin_delete_404@test.com", is_superuser=True)
    app.dependency_overrides[get_current_superuser] = lambda: admin

    response = await async_client.delete("/users/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

    app.dependency_overrides.pop(get_current_superuser)
