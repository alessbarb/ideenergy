#!/usr/bin/env python3

# Copyright (C) 2021-2026 Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import asyncio
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

from ideenergy import AuthenticationError, Client, RequestFailedError, UserExpiredError

FIXTURES_DIR = os.path.dirname(__file__) + "/fixtures"


def read_fixture(fixture_name: str) -> bytes:
    with open(f"{FIXTURES_DIR}/{fixture_name}.bin", "rb") as fh:
        return fh.read()


def failed_response(status: int) -> Mock:
    return Mock(status=status, url="https://www.i-de.es/test", reason="test failure")


class TestSessionRecovery(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = Client(None, "user", "password")
        self.client._login_ts = datetime.now()

    async def test_authentication_http_failure_reauthenticates_once(self):
        error = RequestFailedError(failed_response(403))
        self.client.request_json = AsyncMock(
            side_effect=[error, {"codContrato": "contract"}]
        )
        self.client.login = AsyncMock()

        data = await self.client.get_contract_details()

        self.assertEqual(data["codContrato"], "contract")
        self.client.login.assert_awaited_once_with()
        self.assertEqual(self.client.request_json.await_count, 2)

    async def test_second_authentication_http_failure_is_not_retried(self):
        error = RequestFailedError(failed_response(403))
        self.client.request_json = AsyncMock(side_effect=[error, error])
        self.client.login = AsyncMock()

        with self.assertRaises(RequestFailedError):
            await self.client.get_contract_details()

        self.client.login.assert_awaited_once_with()
        self.assertEqual(self.client.request_json.await_count, 2)

    async def test_transient_server_failure_does_not_force_login(self):
        error = RequestFailedError(failed_response(503))
        self.client.request_json = AsyncMock(side_effect=error)
        self.client.login = AsyncMock()

        with self.assertRaises(RequestFailedError):
            await self.client.get_contract_details()

        self.client.login.assert_not_awaited()
        self.client.request_json.assert_awaited_once()

    async def test_expired_session_logs_in_before_request(self):
        self.client._login_ts = None

        async def login() -> None:
            self.client._login_ts = datetime.now()

        self.client.login = AsyncMock(side_effect=login)
        self.client.request_json = AsyncMock(return_value={"codContrato": "contract"})

        await self.client.get_contract_details()

        self.client.login.assert_awaited_once_with()
        self.client.request_json.assert_awaited_once()

    async def test_concurrent_requests_share_single_login(self):
        self.client._login_ts = None

        async def login() -> None:
            await asyncio.sleep(0)
            self.client._login_ts = datetime.now()

        self.client.login = AsyncMock(side_effect=login)
        self.client.request_json = AsyncMock(return_value={"codContrato": "contract"})

        await asyncio.gather(
            self.client.get_contract_details(),
            self.client.get_contract_details(),
        )

        self.client.login.assert_awaited_once_with()
        self.assertEqual(self.client.request_json.await_count, 2)

    async def test_renew_session_extends_local_session_age(self):
        old_login = datetime.now() - timedelta(minutes=1)
        self.client._login_ts = old_login
        self.client.request_json = AsyncMock(return_value={"usSes": True})

        await self.client.renew_session()

        self.assertGreater(self.client._login_ts, old_login)

    async def test_historical_generation_requires_authentication(self):
        self.client._login_ts = None
        start = datetime(2022, 8, 19)
        end = start + timedelta(days=7)

        async def login() -> None:
            self.client._login_ts = datetime.now()

        self.client.login = AsyncMock(side_effect=login)
        with patch(
            "ideenergy.Client.request_bytes",
            new_class=AsyncMock,
            return_value=read_fixture("historical-generation"),
        ):
            data = await self.client.get_historical_generation(start, end)

        self.client.login.assert_awaited_once_with()
        self.assertEqual(len(data.periods), 168)


class TestAuthenticationErrors(unittest.IsolatedAsyncioTestCase):
    async def test_login_rejection_uses_authentication_error(self):
        client = Client(None, "user", "bad-password")

        with patch(
            "ideenergy.Client.request_bytes",
            new_class=AsyncMock,
            side_effect=[b"", b'{"success": "false"}'],
        ):
            with self.assertRaises(AuthenticationError):
                await client.login()

    async def test_expired_user_uses_specific_authentication_error(self):
        client = Client(None, "user", "password")

        with patch(
            "ideenergy.Client.request_bytes",
            new_class=AsyncMock,
            side_effect=[b"", b'{"success": "userExpired"}'],
        ):
            with self.assertRaises(UserExpiredError):
                await client.login()


if __name__ == "__main__":
    unittest.main()
