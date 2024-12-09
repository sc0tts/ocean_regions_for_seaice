"""
python add_landmask.py

Adds a land mask to a raw .dat file stitche from reprojected quads

Usage:
    python add_landmask.py <grid_name> <stiched_dat_fn> <withland_fn>
  eg
    python add_landmask.py psn25  ./regions_20211003_nh_3411.dat ./regions_20211003_nh_3411_withland.dat  #noqa
"""

import os
import sys
import numpy as np

# These are in all land mask raw data files
land_encoding_value = 30
coast_encoding_value = 31
lake_encoding_value = 32

# These are unique to our new BU-MODIS-derived masks
landice_encoding_value=33
iceshelf_encoding_value=34
discon_encoding_value=35
offearth_encoding_value=40

landmask_fns = {
    # Derived from NT code
    # 'psn25': './landmask-shoredistance-north.dat',
    # 'pss25': './landmask-shoredistance-south.dat',

    # Derived from AMSR_U2 .he5 files
    #'psn25': './amsru_landmask_n25km.dat',
    #'pss25': './amsru_landmask_s25km.dat',
    #'psn12.5': './amsru_landmask_n12.5km.dat',
    #'pss12.5': './amsru_landmask_s12.5km.dat',

    # Our masks calculated from BU-MODIS, ADD, BMG
    'psn25': '/home/scotts/bumodis_gen//loilid_files/psn25_loilid.dat',
    'psn12.5': '/home/scotts/bumodis_gen//loilid_files/psn12.5_loilid.dat',
    'psn6.25': '/home/scotts/bumodis_gen//loilid_files/psn6.25_loilid.dat',
    'psn3.125': '/home/scotts/bumodis_gen//loilid_files/psn3.125_loilid.dat',

    'pss25': '/home/scotts/bumodis_gen//loilid_files/pss25_loilid.dat',
    'pss12.5': '/home/scotts/bumodis_gen//loilid_files/pss12.5_loilid.dat',
    'pss6.25': '/home/scotts/bumodis_gen//loilid_files/pss6.25_loilid.dat',
    'pss3.125': '/home/scotts/bumodis_gen//loilid_files/pss3.125_loilid.dat',

    'e2n25': '/home/scotts/bumodis_gen//loilid_files/e2n25_loilid.dat',
    'e2n12.5': '/home/scotts/bumodis_gen//loilid_files/e2n12.5_loilid.dat',
    'e2n6.25': '/home/scotts/bumodis_gen//loilid_files/e2n6.25_loilid.dat',
    'e2n3.125': '/home/scotts/bumodis_gen//loilid_files/e2n3.125_loilid.dat',

    'e2s25': '/home/scotts/bumodis_gen//loilid_files/e2s25_loilid.dat',
    'e2s12.5': '/home/scotts/bumodis_gen//loilid_files/e2s12.5_loilid.dat',
    'e2s6.25': '/home/scotts/bumodis_gen//loilid_files/e2s6.25_loilid.dat',
    'e2s3.125': '/home/scotts/bumodis_gen//loilid_files/e2s3.125_loilid.dat',
}

binary_shapes = {
    'psn25': (448, 304),
    'psn12.5': (896, 608),
    'psn6.25': (1792, 1216),
    'psn3.125': (3584, 2432),

    'pss25': (316, 332),
    'pss12.5': (632, 664),
    'pss6.25': (1264, 1328),
    'pss3.125': (2528, 2656),

    'e2n25': (720, 720),
    'e2n12.5': (1440, 1440),
    'e2n6.25': (2880, 2880),
    'e2n3.125': (5760, 5760),

    'e2s25': (720, 720),
    'e2s12.5': (1440, 1440),
    'e2s6.25': (2880, 2880),
    'e2s3.125': (5760, 5760),
}

grid_name = sys.argv[1]
assert grid_name in binary_shapes.keys()
assert grid_name in landmask_fns.keys()

data_fn = sys.argv[2]
assert os.path.isfile(data_fn)

ofn = sys.argv[3]
assert data_fn != ofn

landmask = np.fromfile(landmask_fns[grid_name], dtype=np.uint8).reshape(
    binary_shapes[grid_name])

data = np.fromfile(data_fn, dtype=np.uint8).reshape(binary_shapes[grid_name])

try:
    assert np.all(data != land_encoding_value)
except AssertionError:
    raise SystemExit(f'Data already has land value: {land_encoding_value}, {np.sum(np.where(data == land_encoding_value))} times')  # noqa

try:
    assert np.all(data != coast_encoding_value)
except AssertionError:
    raise SystemExit(f'Data already has coast value: {coast_encoding_value}, {np.sum(np.where(data == coast_encoding_value))} times')  # noqa

try:
    assert np.all(data != lake_encoding_value)
except AssertionError:
    raise SystemExit(f'Data already has lake value: {lake_encoding_value}, {np.sum(np.where(data == lake_encoding_value))} times')  # noqa

try:
    assert np.all(data != landice_encoding_value)
except AssertionError:
    raise SystemExit(f'Data already has landice value: {landice_encoding_value}, {np.sum(np.where(data == landice_encoding_value))} times')  # noqa

try:
    assert np.all(data != iceshelf_encoding_value)
except AssertionError:
    raise SystemExit(f'Data already has iceshelf value: {iceshelf_encoding_value}, {np.sum(np.where(data == iceshelf_encoding_value))} times')  # noqa

try:
    assert np.all(data != discon_encoding_value)
except AssertionError:
    raise SystemExit(f'Data already has discon value: {discon_encoding_value}, {np.sum(np.where(data == discon_encoding_value))} times')  # noqa

try:
    assert np.all(data != offearth_encoding_value)
except AssertionError:
    raise SystemExit(f'Data already has offearch value: {offearth_encoding_value}, {np.sum(np.where(data == offearth_encoding_value))} times')  # noqa


if 'shoredistance' in landmask_fns[grid_name]:
    # For the CDR "shoredistance" masks
    is_land = (landmask == 1) | (landmask == 7)
    is_coast = (landmask == 2)
    is_lake = (landmask == 6)

    data[is_land] = land_encoding_value
    data[is_coast] = coast_encoding_value
    data[is_lake] = lake_encoding_value
elif 'amsru' in landmask_fns[grid_name]:
    # For the AMSRU-derived land masks
    print('WARNING: AMSRU-derived land masks only include land; not lakes or coast')  # noqa
    is_land = (landmask == 120)
    # is_coast = (landmask == 2)
    # is_lake = (landmask == 6)

    data[is_land] = land_encoding_value
    # data[is_coast] = coast_encoding_value
    # data[is_lake] = lake_encoding_value
elif 'loilid' in landmask_fns[grid_name]:
    # For the land masks we generate from BU-MODIS, ADD, BMG data
    # landmask ocean (val=50) not re-encoded
    is_discon = (landmask == 80)
    is_land = (landmask == 150)
    is_lake = (landmask == 175)
    is_landice = (landmask == 200)
    is_iceshelf = (landmask == 220)
    is_offearth = (landmask == 250)

    data[is_discon] = discon_encoding_value
    data[is_land] = land_encoding_value
    data[is_lake] = lake_encoding_value
    data[is_landice] = landice_encoding_value
    data[is_iceshelf] = iceshelf_encoding_value
    data[is_offearth] = offearth_encoding_value
else:
    raise SystemExit(f'Cannot interpet land mask values from: {landmask_fns[grid_name]}')  # noqa

data.tofile(ofn)
print(f'Wrote landmasked data to: {ofn}')
