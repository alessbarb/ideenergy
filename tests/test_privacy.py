#!/usr/bin/env python3

# Copyright (C) 2021-2026 Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import unittest
from unittest.mock import Mock

from ideenergy import Client, CommandError, InvalidContractError, InvalidData
from ideenergy import RequestFailedError, UserExpiredError


class TestPrivacySafeStrings(unittest.TestCase):
    def test_client_strings_do_not_expose_account_identifiers(self):
        username = "private-user@example.com"
        password = "super-secret-password"
        contract = "private-contract-123"
        client = Client(None, username, password, contract)

        rendered = f"{client} {client!r}"

        self.assertNotIn(username, rendered)
        self.assertNotIn(password, rendered)
        self.assertNotIn(contract, rendered)

    def test_request_error_does_not_expose_url(self):
        private_url = "https://www.i-de.es/contract/private-contract-123"
        response = Mock(status=403, reason="Forbidden", url=private_url)

        rendered = str(RequestFailedError(response))

        self.assertNotIn(private_url, rendered)
        self.assertNotIn("private-contract-123", rendered)
        self.assertIn("403", rendered)

    def test_payload_errors_keep_payload_out_of_string_representation(self):
        secret = "private-payload-value"

        errors = [
            CommandError({"secret": secret}),
            InvalidData({"secret": secret}),
            InvalidContractError(secret),
            UserExpiredError({"secret": secret}),
        ]

        for error in errors:
            with self.subTest(error=type(error).__name__):
                self.assertNotIn(secret, str(error))


if __name__ == "__main__":
    unittest.main()
