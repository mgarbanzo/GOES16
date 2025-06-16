# GOES16

Programs related to teaching and researching product generation from GOES 16.

## GLM daily plot

The script `plot_glm_day.py` downloads all GOES-16 GLM L2 LCFA files for a
specified day and plots the lightning events on a world map.  It requires the
`xarray`, `s3fs`, `cartopy` and `matplotlib` packages.  Usage:

```bash
python plot_glm_day.py YYYY-MM-DD
```

The script accesses the public NOAA AWS bucket anonymously.  Downloading a
full day involves many files, so network access is required.
