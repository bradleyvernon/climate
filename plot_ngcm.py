import zipfile
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cmaps

# unzip the model output
zip_file = "../../data/ngm_output.zip"
out_dir = "../../data/ngm_output"
z = zipfile.ZipFile(zip_file)
z.extractall(out_dir)
nc_files = [f"{out_dir}/{name}" for name in z.namelist() if name.endswith(".nc")]

# open every member, stack them along a new "seed" dimension, average them
ens = xr.concat([xr.open_dataset(f) for f in nc_files], dim="seed")
precip = ens.precipitation.mean("seed")

# Utah is on MDT (UTC-6) in October, so a Utah day runs 06Z to 06Z.
# Each 6-hour value is the precip that fell in the 6 hours before its time stamp.
days = ["2026-10-09", "2026-10-10", "2026-10-11"]
levels = [1, 2, 3, 5, 7, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150]   # mm/day
colors = cmaps.prcp_1.colors[1:16]  
fig, axes = plt.subplots(1, 3, figsize=(12, 2.6), layout="compressed", subplot_kw={"projection": ccrs.PlateCarree()})

for ax, day in zip(axes, days):
    start = pd.Timestamp(day) + pd.Timedelta(hours=6)
    daily = precip.sel(time=slice(start + pd.Timedelta(hours=6), start + pd.Timedelta(hours=24))).sum("time")


## contourf SMOOTHS gridcells, generally avoid this for precipitation --> aesthetic purposes only 

    pc = ax.contourf(daily.longitude, daily.latitude, daily, levels=levels, colors=colors,
                     extend="max", transform=ccrs.PlateCarree())
    ax.set_extent([-135, -68, 18, 48], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.STATES, linewidth=0.4)
    ax.coastlines(linewidth=0.6)
    ax.gridlines(draw_labels=["bottom", "left"], xlocs=[-130, -110, -90, -70], ylocs=[25, 35, 45],
                 linewidth=0.3, color="gray", x_inline=False, y_inline=False)
    ax.set_title(day)

fig.colorbar(pc, ax=axes, shrink=0.8, pad=0.01, aspect=12, label="Precipitation (mm)")
fig.suptitle(f"NeuralGCM ensemble-mean daily precipitation (n=5)")
plt.savefig("precip_us_oct9-11.png", dpi=150, bbox_inches="tight")
plt.show()
