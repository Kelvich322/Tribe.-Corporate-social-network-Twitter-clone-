from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


@pytest.mark.asyncio
async def test_get_user_by_api_key(client: AsyncClient, test_user: User):
    """Тестирует получение страницы текущего юзера с ключом, который есть в БД и которого нет."""
    resp = await client.get("/api/users/me", headers={"Api-Key": test_user.api_key})
    assert resp.status_code == status.HTTP_200_OK

    resp = await client.get("/api/users/me", headers={"Api-Key": "Another APIKey"})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient, test_user: User):
    resp = await client.get("/api/users/1", headers={"Api-Key": test_user.api_key})
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_follow_and_unfollow_user(
    client: AsyncClient,
    test_user: User,
    test_another_user: User,
):
    """Тестирует подписку и отписку пользователей"""
    resp = await client.post(
        f"/api/users/{test_another_user.id}/follow",
        headers={"Api-Key": test_user.api_key},
    )
    assert resp.status_code == status.HTTP_201_CREATED

    resp = await client.delete(
        f"/api/users/{test_another_user.id}/follow",
        headers={"Api-Key": test_user.api_key},
    )
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_create_tweet(client: AsyncClient, test_user: User):
    """Тестирует создание твита пользователем"""
    data = {"tweet_data": "test", "tweet_media_ids": []}
    resp = await client.post(
        "/api/tweets", headers={"Api-Key": test_user.api_key}, json=data
    )
    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_create_tweet_with_image(
    client: AsyncClient, test_user: User, db_session: AsyncSession
):
    """
    Тестирует создания твита с прикрепленным изображением
    """
    with (
        patch("app.api.routers.tweets.save_media_in_database") as mock_save_media,
        patch("app.api.routers.tweets.create_tweet") as mock_create_tweet,
        patch("app.api.routers.tweets.Path") as mock_path,
    ):
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_media = MagicMock()
        mock_media.id = 1
        mock_save_media.return_value = mock_media
        mock_tweet = MagicMock()
        mock_create_tweet.return_value = mock_tweet

        image_data = b"fake_image_data"
        files = {"file": ("test_image.jpg", image_data, "image/jpeg")}

        response_upload = await client.post(
            "/api/medias", files=files, headers={"API-Key": test_user.api_key}
        )

        assert response_upload.status_code == 201
        upload_data = response_upload.json()
        assert upload_data["result"] is True

        media_id = upload_data["media_id"]
        tweet_data = {"content": "Test tweet with image", "tweet_media_ids": [media_id]}

        response_tweet = await client.post(
            "/api/tweets", json=tweet_data, headers={"API-Key": test_user.api_key}
        )

        assert response_tweet.status_code == 201
        tweet_response_data = response_tweet.json()
        assert tweet_response_data["result"] is True


@pytest.mark.asyncio
async def test_delete_tweet(
    client: AsyncClient,
    test_user: User,
):
    """Тестирует удаление твита пользователем"""
    data = {"tweet_data": "test", "tweet_media_ids": []}
    resp = await client.post(
        "/api/tweets", headers={"Api-Key": test_user.api_key}, json=data
    )
    assert resp.status_code == status.HTTP_201_CREATED

    tweet_id = resp.json()["tweet_id"]
    resp = await client.delete(
        f"/api/tweets/{tweet_id}", headers={"Api-Key": test_user.api_key}
    )
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_deleting_tweet_by_another_user(
    client: AsyncClient,
    test_user: User,
    test_another_user: User,
):
    """Тестирует удаление твита пользователем, который не является его автором"""
    data = {"tweet_data": "test", "tweet_media_ids": []}
    resp = await client.post(
        "/api/tweets", headers={"Api-Key": test_user.api_key}, json=data
    )
    assert resp.status_code == status.HTTP_201_CREATED

    tweet_id = resp.json()["tweet_id"]
    resp = await client.delete(
        f"/api/tweets/{tweet_id}", headers={"Api-Key": test_another_user.api_key}
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_feed_for_current_user(
    client: AsyncClient,
    test_user: User,
    test_another_user: User,
):
    """Тестирует получение ленты твитов для текущего пользователя"""
    data = {"tweet_data": "test", "tweet_media_ids": []}
    resp = await client.post(
        "/api/tweets", headers={"Api-Key": test_user.api_key}, json=data
    )
    assert resp.status_code == status.HTTP_201_CREATED
    current_user_tweet_id = resp.json()["tweet_id"]

    resp = await client.post(
        "/api/tweets", headers={"Api-Key": test_another_user.api_key}, json=data
    )
    assert resp.status_code == status.HTTP_201_CREATED
    another_user_tweet_id = resp.json()["tweet_id"]

    resp = await client.post(
        f"/api/users/{test_another_user.id}/follow",
        headers={"Api-Key": test_user.api_key},
    )
    assert resp.status_code == status.HTTP_201_CREATED

    resp = await client.get("/api/tweets", headers={"Api-Key": test_user.api_key})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["tweets"][0]["id"] == current_user_tweet_id
    assert resp.json()["tweets"][1]["id"] == another_user_tweet_id


@pytest.mark.asyncio
async def test_like_tweet(
    client: AsyncClient,
    test_user: User,
    test_another_user: User,
):
    """Тестирует установку лайка на твит и корректное отображение их количества"""
    data = {"tweet_data": "test", "tweet_media_ids": []}
    resp = await client.post(
        "/api/tweets", headers={"Api-Key": test_user.api_key}, json=data
    )
    assert resp.status_code == status.HTTP_201_CREATED
    tweet_id = resp.json()["tweet_id"]

    resp = await client.post(
        f"/api/tweets/{tweet_id}/likes", headers={"Api-Key": test_user.api_key}
    )
    assert resp.status_code == status.HTTP_201_CREATED
    resp = await client.post(
        f"/api/tweets/{tweet_id}/likes", headers={"Api-Key": test_another_user.api_key}
    )
    assert resp.status_code == status.HTTP_201_CREATED

    resp = await client.get("/api/tweets", headers={"Api-Key": test_user.api_key})
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()["tweets"][0]["likes"]) == 2


@pytest.mark.asyncio
async def test_remove_like_from_tweet(
    client: AsyncClient,
    test_user: User,
    test_another_user: User,
):
    """Тестирует удаление лайка с твита и корректное отображение их количества"""
    data = {"tweet_data": "test", "tweet_media_ids": []}
    resp = await client.post(
        "/api/tweets", headers={"Api-Key": test_user.api_key}, json=data
    )
    assert resp.status_code == status.HTTP_201_CREATED
    tweet_id = resp.json()["tweet_id"]

    resp = await client.post(
        f"/api/tweets/{tweet_id}/likes", headers={"Api-Key": test_user.api_key}
    )
    assert resp.status_code == status.HTTP_201_CREATED
    resp = await client.post(
        f"/api/tweets/{tweet_id}/likes", headers={"Api-Key": test_another_user.api_key}
    )
    assert resp.status_code == status.HTTP_201_CREATED

    resp = await client.get("/api/tweets", headers={"Api-Key": test_user.api_key})
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()["tweets"][0]["likes"]) == 2

    resp = await client.delete(
        f"/api/tweets/{tweet_id}/likes", headers={"Api-Key": test_user.api_key}
    )
    assert resp.status_code == status.HTTP_200_OK
    resp = await client.delete(
        f"/api/tweets/{tweet_id}/likes", headers={"Api-Key": test_another_user.api_key}
    )
    assert resp.status_code == status.HTTP_200_OK

    resp = await client.get("/api/tweets", headers={"Api-Key": test_user.api_key})
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()["tweets"][0]["likes"]) == 0
