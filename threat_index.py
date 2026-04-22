from herbie import Herbie
import pandas as pd, numpy as np, xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
import cartopy.crs as ccrs, cartopy.feature as cfeature
from datetime import datetime, timedelta, time, timezone
import xarray as xr
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

DATA_FILE   = "/courses/meteo473/sp26/473_sp26_group1/data/gfs_event1.nc"
OUTPUT = "/courses/meteo473/sp26/473_sp26_group1/output"

import os
os.makedirs(OUTPUT, exist_ok=True)

ds = xr.open_dataset('gfs.nc')
ds
chosen_hour = 6
s_ds = ds.isel(valid_time = chosen_hour)
ds_ne = s_ds.sel(latitude = slice(50,40), longitude = slice(280, 300))  


t2m_f = (ds_ne['t2m'].values-273.15)* (9/5) + 32

tcc = ds_ne['tcc'].values

u = ds_ne['u10'].values * 2.23694 
v = ds_ne['v10'].values * 2.23694 
wind = np.sqrt(u**2 + v**2)

sde = ds_ne['sde'].values * 100

csnow = ds_ne['csnow'].values

tp = ds_ne['tp'].values * 2.54

lat = ds_ne.latitude.values
lon = ds_ne.longitude.values
tp_chosenhr= ds.tp.isel(valid_time= chosen_hour).sel(latitude = slice(50,40), longitude = slice(280, 300)).values
tp_prevhr = ds.tp.isel(valid_time= chosen_hour - 1).sel(latitude = slice(50,40), longitude = slice(280, 300)).values
tp_interval = tp_chosenhr - tp_prevhr
tp_interval = tp_interval * 0.03937 * 10
t2m_contribution = np.zeros_like(t2m_f)

valid_time = datetime.strptime(str(ds.valid_time.values[chosen_hour])[:16], "%Y-%m-%dT%H:%M").strftime("%H:%M UTC %b %d %Y")
initial_time = datetime.strptime(str(ds.valid_time.values[0])[:16], "%Y-%m-%dT%H:%M").strftime("%H:%M UTC %b %d %Y")


mask = (t2m_f >= 0) & (t2m_f < 20)
t2m_contribution[mask] = (1 - ((20 - t2m_f[mask])/20)**2)


mask = (t2m_f >= 20) & (t2m_f <= 32)
t2m_contribution[mask] = 1.0


mask = (t2m_f > 32) & (t2m_f < 50)
t2m_contribution[mask] = (1 - ((t2m_f[mask] - 32)/18)**2)

mask = t2m_f >= 50
t2m_contribution[mask] = 0


plt.pcolormesh(lon, lat, np.flipud(t2m_contribution), vmin = 0, vmax = 1)
plt.colorbar()
plt.xlabel("Longitude")
plt.ylabel("Latidude")
plt.axis('off')
plt.title(f"GFS 2 Meter Temperature (contribution)\nInitial Time: {initial_time}\n Valid Time: {valid_time}")
plt.savefig("output/t2mcontribution_006.png", dpi=150, bbox_inches="tight")
plt.close()


tcc_contribution = np.zeros_like(tcc)


mask = (tcc >= 0) & (tcc <= 50)
tcc_contribution[mask] = (0.01)*(tcc[mask]) + 0.5


mask = (tcc > 50)
tcc_contribution[mask] = (-0.01)*(tcc[mask]) + 1.5

plt.pcolormesh(np.flipud(tcc_contribution), vmin = 0, vmax = 1)
plt.colorbar()
plt.xlabel("Longitude")
plt.ylabel("Latidude")
plt.axis('off')
plt.title(f"GFS Total Cloud Cover (contribution)\n Initial Time: {initial_time}\n Valid Time: {valid_time}")
plt.savefig("output/tcccontribution_006.png", dpi=150, bbox_inches="tight")
plt.close()


wind_contribution = np.zeros_like(wind)


mask = (wind >= 0) & (wind <= 50)
wind_contribution[mask] = ((-1/50)*(wind[mask])) + 1

 
plt.pcolormesh(np.flipud(wind_contribution), vmin = 0, vmax = 1)
plt.colorbar()
plt.xlabel("Longitude")
plt.ylabel("Latidude")
plt.axis('off')
plt.title(f"GFS Wind (contribution)\n Initial Time: {initial_time}\n Valid Time: {valid_time}")
tp_snow_only = np.where(csnow == 1, tp_interval, 0)
plt.savefig("output/windcontribution_006.png", dpi=150, bbox_inches="tight")
plt.close()


tp_contribution = np.zeros_like(tp_snow_only)


mask = (tp_snow_only >= 0) & (tp_snow_only <= 6)
tp_contribution[mask] = ((1/6)*(tp_snow_only[mask]))
mask = (tp_snow_only > 6)
tp_contribution[mask] = 1


plt.pcolormesh(np.flipud(tp_contribution), vmin = 0, vmax = 1)
plt.colorbar()
plt.xlabel("Longitude")
plt.ylabel("Latidude")
plt.axis('off')
plt.title(f"GFS Total Snow Precipitation (contribution)\n Initial Time: {initial_time}\n Valid Time: {valid_time}")
plt.savefig("output/tpcontribution_006.png", dpi=150, bbox_inches="tight")
plt.close()


PUI = (t2m_contribution*0.4 + tcc_contribution*0.1 + wind_contribution*0.2 + tp_contribution*0.3)*100


plt.pcolormesh(np.flipud(PUI), vmin = 0, vmax = 100)
plt.colorbar()
plt.xlabel("Longitude")
plt.ylabel("Latidude")
plt.axis('off')
plt.title(f"GFS Final Equation\n Initial Time: {initial_time}\n Valid Time: {valid_time}")
plt.savefig("output/total_contribution_006.png", dpi=150, bbox_inches="tight")
plt.close()

chosen_ts = [1,3,5,7,9,11]


def threat_index(ds, chosen_ts):
    s_ds = ds.isel(valid_time = chosen_ts) 
        
        
    ds_ne = s_ds.sel(latitude = slice(50,40), longitude = slice(280, 300))
    
    t2m_f = (ds_ne['t2m'].values-273.15)* (9/5) + 32
    tcc = ds_ne['tcc'].values
    u = ds_ne['u10'].values * 2.23694 
    v = ds_ne['v10'].values * 2.23694 
    wind = np.sqrt(u**2 + v**2)
    csnow= ds_ne['csnow'].values
    tp_chosenhr= ds.tp.isel(valid_time= chosen_ts).values
    tp_prevhr = ds.tp.isel(valid_time= chosen_ts - 1).values
    tp_interval = tp_chosenhr - tp_prevhr
        
    sde = ds_ne['sde'].values * 100
        
        
    t2m_contribution = np.zeros_like(t2m_f)
        
    mask = (t2m_f >= 0) & (t2m_f < 20)
    t2m_contribution[mask] = (1 - ((20 - t2m_f[mask])/20)**2)
        
    mask = (t2m_f >= 20) & (t2m_f <= 32)
    t2m_contribution[mask] = 1.0
        
    mask = (t2m_f > 32) & (t2m_f < 50)
    t2m_contribution[mask] = (1 - ((t2m_f[mask] - 32)/18)**2)
        
    mask = t2m_f >= 50
    t2m_contribution[mask] = 0
    
    tcc_contribution = np.zeros_like(tcc)
        
    mask = (tcc >= 0) & (tcc <= 50)
    tcc_contribution[mask] = (0.01)*(tcc[mask]) + 0.5
        
    mask = (tcc > 50)
    tcc_contribution[mask] = (-0.01)*(tcc[mask]) + 1.5
        
    
        
    wind_contribution = np.zeros_like(wind)
        
    mask = (wind >= 0) & (wind <= 50)
    wind_contribution[mask] = ((-1/50)*(wind[mask])) + 1


    
    sde_contribution = np.zeros_like(sde)
    
    mask = (sde < 25)
    sde_contribution[mask] = 0
    mask = (sde >= 25) & (sde <= 500)
    sde_contribution[mask] = ((1/500)*((sde[mask]) - 25))
        
         
    tp_chosenhr= ds.tp.isel(valid_time= chosen_ts).sel(latitude = slice(50,40), longitude = slice(280, 300)).values
    tp_prevhr = ds.tp.isel(valid_time= chosen_ts - 1).sel(latitude = slice(50,40), longitude = slice(280, 300)).values
    tp_interval = tp_chosenhr - tp_prevhr
    tp_interval = tp_interval * 0.03937 * 10
    tp_snow_only = np.where(csnow == 1, tp_interval, 0)
    tp_contribution = np.zeros_like(tp_snow_only)
    mask = (tp_snow_only >= 0) & (tp_snow_only <= 6)
    tp_contribution[mask] = ((1/6)*(tp_snow_only[mask]))
    mask = (tp_snow_only > 6)
    tp_contribution[mask] = 1

    
    PUI = (t2m_contribution*0.4 + tcc_contribution*0.1 + wind_contribution*0.2 + tp_contribution*0.3)*100
    
    
    return PUI, t2m_contribution, tcc_contribution, wind_contribution, tp_contribution

  
initial_time = pd.to_datetime(ds.valid_time.values[0]).strftime("%H:%M UTC %b %d %Y")

colorbar_range = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
colorbar_custom = ['#ffffff','#f0f8ff','#afeeee','#87cefa','#1e90ff','#0000cd','#191970','#4b0082','#ba2be2','#ff00ff']
colorbar_cmap=mcolors.ListedColormap(colorbar_custom)

def basemap():
    fig = plt.figure(figsize = (12,6))
    axs = fig.subplots(nrows = 2, ncols = 3, subplot_kw = {'projection': ccrs.PlateCarree()})
    for ax in axs.flatten():
        ax.set_extent([-80,-60,40,50], ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE, linewidth = 0.7)
        ax.add_feature(cfeature.STATES, linestyle=':', linewidth = 0.5)
        ax.add_feature(cfeature.BORDERS, linewidth = 0.7)
        gridlines = ax.gridlines(crs = ccrs.PlateCarree(), draw_labels = False, linewidth = 0.5, color = 'gray', alpha = 0.5, linestyle = '--')
        axs[1,2].set_visible(False)  

    return fig, axs

for t in chosen_ts:
    lat = ds_ne.latitude.values
    lon = ds_ne.longitude.values
    PUI, t2m_contribution, tcc_contribution, wind_contribution, tp_contribution = threat_index(ds, t)
    time_str = str(ds.valid_time.values[t])
    valid_time = datetime.strptime(time_str[:19], "%Y-%m-%dT%H:%M:%S").strftime("%H:%M UTC %b %d %Y")
    initial_time = datetime.strptime(str(ds.valid_time.values[0])[:19], "%Y-%m-%dT%H:%M:%S").strftime("%H:%M UTC %b %d %Y")


    hour = t*6
    fig, axs = basemap()
        
    ax=axs[0,0]
    plot1 = axs[0,0].pcolormesh(lon, lat, t2m_contribution , transform = ccrs.PlateCarree(), cmap='Blues',  vmin = 0, vmax = 1)
    axins = inset_axes(ax, width = "100%", height = "3%", loc = 'lower left', bbox_to_anchor = (0, -.05, 1, 1), bbox_transform=ax.transAxes, borderpad = 0)
    plt.colorbar(plot1, cax = axins, orientation = 'horizontal') 
    axs[0,0].set_title("GFS Temp Contribution")
    
    ax2=axs[0,1]
    plot2 = axs[0,1].pcolormesh(lon, lat, tcc_contribution , transform = ccrs.PlateCarree(), cmap='binary',  vmin = 0, vmax = 1)
    axins = inset_axes(ax2, width = "100%", height = "3%", loc = 'lower left', bbox_to_anchor = (0, -.05, 1, 1), bbox_transform=ax2.transAxes, borderpad = 0)
    plt.colorbar(plot2, cax = axins, orientation = 'horizontal') 
    axs[0,1].set_title("GFS Cloud Contribution")

    ax3 = axs[0,2]
    plot3 = axs[0,2].pcolormesh(lon, lat, wind_contribution , transform = ccrs.PlateCarree(), cmap='Purples',  vmin = 0, vmax = 1)
    axins = inset_axes(ax3, width = "100%", height = "3%", loc = 'lower left', bbox_to_anchor = (0, -.05, 1, 1), bbox_transform=ax3.transAxes, borderpad = 0)
    plt.colorbar(plot3, cax = axins, orientation = 'horizontal')
    axs[0,2].set_title("GFS Wind Contribution")

    ax4 = axs[1,0]
    plot4 = axs[1,0].pcolormesh(lon, lat, tp_contribution , transform = ccrs.PlateCarree(), cmap='PuBu',  vmin =0, vmax = 1)
    axins = inset_axes(ax4, width = "100%", height = "3%", loc = 'lower left', bbox_to_anchor = (0, -.05, 1, 1), bbox_transform=ax4.transAxes, borderpad = 0)
    plt.colorbar(plot4, cax = axins, orientation = 'horizontal')
    axs[1,0].set_title("GFS Snow Precip Contribution")

    ax5 = axs[1,1]
    plot5 = axs[1,1].pcolormesh(lon, lat, PUI , transform = ccrs.PlateCarree(), cmap=colorbar_cmap,  vmin = 0, vmax = 100)
    axins = inset_axes(ax5, width = "100%", height = "3%", loc = 'lower left', bbox_to_anchor = (0, -.05, 1, 1), bbox_transform=ax5.transAxes, borderpad = 0)
    plt.colorbar(plot5, cax = axins, orientation = 'horizontal')
    axs[1,1].set_title("GFS Threat Index")
    
    
    fig.suptitle(f"GFS Threat Index\n Initial Time: {initial_time}, Valid Time: {valid_time}", fontsize=16) 
    fig.tight_layout(w_pad=3) 

    outpath = os.path.join(OUTPUT, f"5-plot-threat_{hour:03d}.png")
    plt.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f" Saved: {outpath}")
print('Done.')



        
PUI, t2m_contribution, tcc_contribution, wind_contribution, sde_contribution = threat_index(ds, 6)
ds_high = xr.open_dataset("gfs.nc_high")


ds_low = xr.open_dataset("gfs.nc_low")
chosen_hour_high = 4
PUI_high, t2m_c, tcc_c, wind_c, tp_c = threat_index(ds_high, chosen_hour_high)
valid_time_high = datetime.strptime(str(ds_high.valid_time.values[chosen_hour_high])[:16], "%Y-%m-%dT%H:%M").strftime("%H:%M UTC %b %d %Y")
initial_time_high = datetime.strptime(str(ds_high.valid_time.values[0])[:16], "%Y-%m-%dT%H:%M").strftime("%H:%M UTC %b %d %Y")
chosen_hour_low = 5
PUI_low, t2m_c, tcc_c, wind_c, tp_c = threat_index(ds_low, chosen_hour_low)
valid_time_low = datetime.strptime(str(ds_low.valid_time.values[chosen_hour_low])[:16], "%Y-%m-%dT%H:%M").strftime("%H:%M UTC %b %d %Y")
initial_time_low = datetime.strptime(str(ds_low.valid_time.values[0])[:16], "%Y-%m-%dT%H:%M").strftime("%H:%M UTC %b %d %Y")
def map():
    fig = plt.figure(figsize = (8,10))
    ax = fig.add_subplot(111, projection = ccrs.PlateCarree())
    
    ax.set_extent([-80,-60,40,50], ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE, linewidth = 0.7)
    ax.add_feature(cfeature.STATES, linestyle=':', linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS, linewidth = 0.7)

    gridlines = ax.gridlines(crs = ccrs.PlateCarree(), draw_labels = False, linewidth = 0.5, color = 'gray', alpha = 0.5, linestyle = '--')

    return fig, ax
fig, ax6 = map()
plot6 = ax6.pcolormesh(lon, lat, PUI_high, transform = ccrs.PlateCarree(), cmap=colorbar_cmap, vmin = 0, vmax = 100)
axins = inset_axes(ax6, width = "100%", height = "3%", loc = 'lower left', bbox_to_anchor = (0, -.05, 1, 1), bbox_transform=ax6.transAxes, borderpad = 0)
plt.colorbar(plot6, cax = axins, orientation = 'horizontal')
ax6.set_title(f"GFS High-End Event Threat Index\n Initial Time: {initial_time_high}\n Valid Time: {valid_time_high}")
plt.savefig("output/high_index_004.png", dpi=150, bbox_inches="tight")
plt.close()

fig, ax7 = map()
plot7 = ax7.pcolormesh(lon, lat, PUI_low, transform = ccrs.PlateCarree(), cmap=colorbar_cmap, vmin = 0, vmax = 100)
axins = inset_axes(ax7, width = "100%", height = "3%", loc = 'lower left', bbox_to_anchor = (0, -.05, 1, 1), bbox_transform=ax7.transAxes, borderpad = 0)
plt.colorbar(plot7, cax = axins, orientation = 'horizontal')
ax7.set_title(f"GFS Low-End Event Threat Index\n Initial Time: {initial_time_low}\n Valid Time: {valid_time_low}")
plt.savefig("output/low_index_005.png", dpi=150, bbox_inches="tight")
plt.close()




for t in range(len(ds.valid_time)):
    step = t*1
    PUI, t2m_contribution, tcc_contribution, wind_contribution, tp_contribution = threat_index(ds, t)
    
    s_ds = ds.isel(valid_time=t)
    ds_ne = s_ds.sel(latitude=slice(50,40), longitude=slice(280,300))
    
    lat = ds_ne.latitude.values
    lon = ds_ne.longitude.values
    
    valid_time = datetime.strptime(str(s_ds.valid_time.values)[:16], "%Y-%m-%dT%H:%M").strftime("%H:%M UTC %b %d %Y")
    
    fig = plt.figure(figsize=(8,6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    ax.set_extent([-80, -60, 40, 50])
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.STATES, linestyle=':')
    
    colorbar_range = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    colorbar_custom = [
        '#ffffff',
        '#f0f8ff',
        '#afeeee',
        '#87cefa',
        '#1e90ff',
        '#0000cd',
        '#191970',
        '#4b0082',
        '#ba2be2',
        '#ff00ff'
    ]
    colorbar_cmap=mcolors.ListedColormap(colorbar_custom)
    
    plot = ax.pcolormesh(lon, lat, PUI, transform=ccrs.PlateCarree(),cmap=colorbar_cmap, vmin=0, vmax=100)
    
    axins = inset_axes(ax, width = "100%", height = "3%", loc = 'lower left', bbox_to_anchor = (0, -.05, 1, 1), bbox_transform=ax.transAxes, borderpad = 0)
    plt.colorbar(plot, cax = axins, orientation = 'horizontal')

    
    ax.set_title(f"GFS Threat Index\n Initial Time: {initial_time} \nValid Time: {valid_time}")
    
    
    outpath = os.path.join(OUTPUT, f"threat_{step:03d}.png")
    plt.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f" Saved: {outpath}")
print('Done.')
