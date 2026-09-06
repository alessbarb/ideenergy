#!/usr/bin/env python3

# Copyright (C) 2021-2026 Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import unittest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

from ideenergy import CircuitOpenError, Client, RequestFailedError


def failed_response(status: int) -> Mock:
    return Mock(status=status, url="https://www.i-de.es/test", reason="test failure")


class TestCircuitBreaker(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = Client(None, "user", "password")
        self.client._login_ts = datetime.now()

    async def test_three_transient_failures_open_circuit(self):
        error = RequestFailedError(failed_response(503))
        self.client.request_json = AsyncMock(side_effect=error)

        for _ in range(3):
            with self.assertRaises(RequestFailedError):
                await self.client.get_contract_details()

        with self.assertRaises(CircuitOpenError):
            await self.client.get_contract_details()

        self.assertEqual(self.client.request_json.await_count, 3)

    async def test_success_resets_consecutive_failure_count(self):
        error = RequestFailedError(failed_response(503))
        self.client.request_json = AsyncMock(
            side_effect=[
                error,
                error,
                {"codContrato": "contract"},
                error,
                error,
                {"codContrato": "contract"},
            ]
        )

        for _ in range(2):
            with self.assertRaises(RequestFailedError):
                await self.client.get_contract_details()

        await self.client.get_contract_details()

        for _ in range(2):
            with self.assertRaises(RequestFailedError):
                await self.client.get_contract_details()

        data = await self.client.get_contract_details()
        self.assertEqual(data["codContrato"], "contract")
        self.assertEqual(self.client.request_json.await_count, 6)

    async def test_final_403_counts_as_one_operation_failure(self):
        error = RequestFailedError(failed_response(403))
        self.client.request_json = AsyncMock(side_effect=[error, error])
        self.client.login = AsyncMock()

        with self.assertRaises(RequestFailedError):
            await self.client.get_contract_details()

        self.assertEqual(self.client._circuit_failure_count, 1)
        self.client.login.assert_awaited_once_with()
        self.assertEqual(self.client.request_json.await_count, 2)

    async def test_expired_circuit_allows_request_again(self):
        self.client._circuit_failure_count = 3
        self.client._circuit_open_until = datetime.now() - timedelta(seconds=1)
        self.client.request_json = AsyncMock(return_value={"codContrato": "contract"})

        data = await self.client.get_contract_details()

        self.assertEqual(data["codContrato"], "contract")
        self.assertEqual(self.client._circuit_failure_count, 0)
        self.assertIsNone(self.client._circuit_open_until)
        self.client.request_json.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
