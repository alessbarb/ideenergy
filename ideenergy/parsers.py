# Copyright (C) 2021-2022 Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.


import itertools
from datetime import UTC, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from . import client
from .types import (
    ConsumptionForPeriod,
    DemandAtInstant,
    HistoricalConsumption,
    HistoricalGeneration,
    HistoricalPowerDemand,
    InProgressConsumption,
    PeriodValue,
)

LOCAL_TZ = ZoneInfo("Europe/Madrid")


def as_local_datetime(dt: datetime) -> datetime:
    """Interpret legacy naive values locally while preserving aware values."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=LOCAL_TZ)
    return dt.astimezone(LOCAL_TZ)


def _elapsed_hour_period(base_dt: datetime, idx: int) -> tuple[datetime, datetime]:
    """Return one real elapsed hour from a Spanish local-time origin.

    Building periods with naive ``base + timedelta(hours=idx)`` produces an
    impossible 02:00 hour during the spring DST transition and loses one of
    the two 02:00 hours during the autumn transition. Convert the local origin
    to UTC first, advance in real elapsed hours, then convert each boundary
    back to Europe/Madrid so ``fold`` and offsets remain correct.
    """
    base_utc = as_local_datetime(base_dt).astimezone(UTC)
    start = (base_utc + timedelta(hours=idx)).astimezone(LOCAL_TZ)
    end = (base_utc + timedelta(hours=idx + 1)).astimezone(LOCAL_TZ)
    return start, end


def parser_generic_historical_data(data, base_dt: datetime) -> dict[str, Any]:
    def _normalize(idx: int, item: dict | None) -> PeriodValue | None:
        if item is None:
            return None

        start, end = _elapsed_hour_period(base_dt, idx)
        try:
            return PeriodValue(start=start, end=end, value=float(item["valor"]))
        except (KeyError, ValueError, TypeError):
            return None

    g = (_normalize(idx, item) for (idx, item) in enumerate(data["y"]["data"][0]))
    historical_values = [x for x in g if x is not None]
    historical_values = list(sorted(historical_values, key=lambda x: x.start))

    return {
        # "accumulated": float(data["acumulado"]),
        # "accumulated-co2": float(data["acumuladoCO2"]),
        "historical": historical_values,
    }


def parse_historical_consumption(data) -> HistoricalConsumption:
    def list_to_dict(values, keys):
        return {keys[idx]: values[idx] for idx in range(len(values))}

    start = datetime.strptime(data[0]["fechaDesde"], "%d-%m-%Y").replace(
        hour=0, minute=0, second=0
    )

    period_names = data[0]["periodos"]

    ret = HistoricalConsumption(
        total=data[0]["total"],
        desglosed=list_to_dict(data[0]["totalesPeriodosTarifarios"], period_names),
    )

    for idx, value in enumerate(data[0]["valores"]):
        period_start, period_end = _elapsed_hour_period(start, idx)
        ret.periods.append(
            ConsumptionForPeriod(
                start=period_start,
                end=period_end,
                value=value,
                desglosed=list_to_dict(
                    data[0]["valoresPeriodosTarifarios"][idx], period_names
                ),
            )
        )

    ret.periods = list(sorted(ret.periods, key=lambda x: x.start))

    return ret


def parse_in_progress_consumption(data) -> InProgressConsumption:
    ret = InProgressConsumption()
    periods = ret.periods
    onehour = timedelta(hours=1)
    fechas = data.get("fechas")
    consumos = data.get("consumos")
    if not (fechas and consumos):
        if fechas or consumos:
            raise client.InvalidData(data)
        # Between 00:00 and 01:00: {'mensaje': 'No existen datos disponibles'}
        return ret
    for endstr, value in zip(data["fechas"], data["consumos"]):
        end = datetime.strptime(endstr, "%Y-%m-%d %H")
        periods.append(PeriodValue(start=end - onehour, end=end, value=value))
    return ret


def parse_historical_generation(data) -> HistoricalGeneration:
    start = datetime.strptime(data["fechaPeriodo"], "%d-%m-%Y%H:%M:%S").replace(
        hour=0, minute=0, second=0
    )

    parsed = parser_generic_historical_data(data, start)

    return HistoricalGeneration(periods=parsed["historical"])


def parse_historical_power_demand_data(data) -> HistoricalPowerDemand:
    def _normalize_item(item: dict) -> DemandAtInstant:
        return DemandAtInstant(
            dt=datetime.strptime(item["name"], "%d/%m/%Y %H:%M"),
            value=item["y"],
        )

    potMaxMens = data["potMaxMens"]
    potMaxMens = list(itertools.chain.from_iterable([x for x in potMaxMens]))

    demands = [_normalize_item(x) for x in potMaxMens]
    demands = list(sorted(demands, key=lambda x: x.dt))

    return HistoricalPowerDemand(demands=demands)
