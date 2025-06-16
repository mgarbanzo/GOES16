#!/usr/bin/env python3
"""Plot GOES-16 GLM events for a full day.

This script downloads GOES-16 GLM L2 Lightning Cluster and Flash
Attributes (LCFA) data from NOAA's public S3 bucket and plots all events
for a given day on a world map.

Usage
-----
    python plot_glm_day.py YYYY-MM-DD

The date must be provided in the ``YYYY-MM-DD`` format.
The script requires ``xarray``, ``s3fs`` and ``cartopy`` to access the
data and plot the results.
"""

from __future__ import annotations

import argparse
import datetime as dt
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import s3fs
import xarray as xr
import cartopy.crs as ccrs


def fetch_glm_day(date: dt.datetime) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Download GLM event latitude, longitude and energy for ``date``.

    Parameters
    ----------
    date : datetime
        Day to retrieve. Only the date part is used.

    Returns
    -------
    tuple of numpy.ndarray
        Arrays containing latitudes, longitudes and event energy.
    """

    year = date.strftime("%Y")
    doy = date.strftime("%j")
    fs = s3fs.S3FileSystem(anon=True)

    lats = []
    lons = []
    energy = []

    for hour in range(24):
        prefix = f"noaa-goes16/GLM-L2-LCFA/{year}/{doy}/{hour:02d}/"
        try:
            files = sorted(fs.glob(prefix + "*.nc"))
        except Exception as exc:  # pragma: no cover - network access
            raise RuntimeError(f"Failed to list files for {prefix}: {exc}")
        for path in files:
            with fs.open(path, mode="rb") as f:
                ds = xr.open_dataset(f)
                lats.append(ds["event_lat"].values)
                lons.append(ds["event_lon"].values)
                energy.append(ds["event_energy"].values)
                ds.close()

    return (
        np.concatenate(lats),
        np.concatenate(lons),
        np.concatenate(energy),
    )


def plot_events(lat: np.ndarray, lon: np.ndarray, energy: np.ndarray, date: dt.datetime) -> None:
    """Create a scatter plot of GLM events."""

    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    sc = ax.scatter(
        lon,
        lat,
        c=np.log10(energy),
        s=1,
        cmap="turbo",
        alpha=0.6,
        transform=ccrs.PlateCarree(),
    )
    plt.colorbar(sc, ax=ax, label="log10(Event energy)")
    ax.set_title(f"GOES-16 GLM Events {date:%Y-%m-%d}")
    plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot GOES-16 GLM data for a day")
    parser.add_argument("date", help="Date in YYYY-MM-DD format")
    args = parser.parse_args()
    date = dt.datetime.strptime(args.date, "%Y-%m-%d")

    lat, lon, energy = fetch_glm_day(date)
    plot_events(lat, lon, energy, date)


if __name__ == "__main__":
    main()
