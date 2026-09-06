#!/usr/bin/env python3

# Copyright (C) 2021-2026 Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import os
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from ideenergy import Client

FIXTURES_DIR = os.path.dirname(__file__) + "/fixtures"


def read_fixture(fixture_name: str) -> bytes:
    with open(f"{FIXTURES_DIR}/{fixture_name}.bin", "rb") as fh:
        return fh.read()


class TestHistoricalRangeNormalization(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = Client(None, "user", "password")
        self.client._login_ts = datetime.now()
        self.start = datetime(2022, 8, 19)
        self.end = datetime(2022, 8, 26)

    async def test_consumption_normalizes_reversed_range(self):
        with patch(
            "ideenergy.Client.request_bytes",
            new_class=AsyncMock,
            return_value=read_fixture("historical-consumption"),
        ) as request_bytes:
            await self.client.get_historical_consumption(self.end, self.start)

        url = request_bytes.await_args.args[1]
        self.assertIn("/19-08-2022/26-08-2022/", url)

    async def test_generation_normalizes_reversed_range(self):
        with patch(
            "ideenergy.Client.request_bytes",
            new_class=AsyncMock,
            return_value=read_fixture("historical-generation"),
        ) as request_bytes:
            data = await self.client.get_historical_generation(self.end, self.start)

        url = request_bytes.await_args.args[1]
        self.assertIn(
            "/fechaInicio/19-08-202200:00:00/fechaFinal/26-08-202200:00:00/",
            url,
        )
        self.assertEqual(len(data.periods), 168)


if __name__ == "__main__":
    unittest.main()
