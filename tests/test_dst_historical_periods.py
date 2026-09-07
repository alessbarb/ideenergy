"""Regression tests for Spanish daylight-saving historical periods."""

import unittest
from datetime import timedelta

from ideenergy.parsers import parse_historical_consumption


def consumption_payload(date: str, hours: int):
    """Build the minimal i-DE historical payload for an hourly day."""
    return [
        {
            "fechaDesde": date,
            "periodos": [],
            "total": float(hours),
            "totalesPeriodosTarifarios": [],
            "valores": [1.0] * hours,
            "valoresPeriodosTarifarios": [[] for _ in range(hours)],
        }
    ]


class HistoricalDstTests(unittest.TestCase):
    def assert_real_hour_spacing(self, periods):
        timestamps = [period.start.timestamp() for period in periods]
        self.assertTrue(
            all(
                current - previous == timedelta(hours=1).total_seconds()
                for previous, current in zip(timestamps, timestamps[1:])
            )
        )

    def test_spring_forward_skips_nonexistent_local_hour(self):
        historical = parse_historical_consumption(consumption_payload("29-03-2026", 23))

        self.assertEqual(len(historical.periods), 23)
        self.assert_real_hour_spacing(historical.periods)

        first = historical.periods[0]
        second = historical.periods[1]
        last = historical.periods[-1]

        self.assertEqual((first.start.hour, first.end.hour), (0, 1))
        self.assertEqual((second.start.hour, second.end.hour), (1, 3))
        self.assertEqual(second.start.utcoffset(), timedelta(hours=1))
        self.assertEqual(second.end.utcoffset(), timedelta(hours=2))
        self.assertEqual((last.end.day, last.end.hour), (30, 0))

    def test_autumn_fallback_preserves_both_local_two_oclock_hours(self):
        historical = parse_historical_consumption(consumption_payload("25-10-2026", 25))

        self.assertEqual(len(historical.periods), 25)
        self.assert_real_hour_spacing(historical.periods)

        first_two = historical.periods[2]
        second_two = historical.periods[3]
        last = historical.periods[-1]

        self.assertEqual(first_two.start.hour, 2)
        self.assertEqual(second_two.start.hour, 2)
        self.assertEqual(first_two.start.fold, 0)
        self.assertEqual(second_two.start.fold, 1)
        self.assertEqual(first_two.start.utcoffset(), timedelta(hours=2))
        self.assertEqual(second_two.start.utcoffset(), timedelta(hours=1))
        self.assertEqual((last.end.day, last.end.hour), (26, 0))


if __name__ == "__main__":
    unittest.main()
