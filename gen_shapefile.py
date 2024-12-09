"""
gen_shapefile.py

Generate a shapefile from list of vertices

Usage:
    python gen_shapefile.py regions_apr22.txt regions_apr22.shp

You should be able to load the resulting shapefile(s) into QGIS
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from fiona.crs import from_epsg
import sys


def xwm(m='exiting in xwm()'):
    raise SystemExit(m)


def get_coords(df_sea, nh_only=False, sh_only=False):
    """Return a list of the coordinates for this sea"""
    coords = []

    for rec in range(1, len(df_sea) + 1):
        try:
            lat = float(df_sea[df_sea['Vertex_Index'] == rec]['Latitude'])
            lon = float(df_sea[df_sea['Vertex_Index'] == rec]['Longitude'])
        except TypeError:
            print('Error converting Latitude or Longitude')
            this_sea = df_sea[df_sea['Vertex_Index'] == rec]
            print(f'{this_sea}')
            xwm()

        coord = (lon, lat)
        coords.append(coord)

    if nh_only:
        for coord in coords:
            lon, lat = coord
            if lat > 0:
                return coords
        return None

    elif sh_only:
        for coord in coords:
            lon, lat = coord
            if lat < 0:
                return coords
        return None

    else:
        return coords


def gen_shapefile(ifn, ofn, is_nh, is_sh):
    """ """
    print(f'ifn: {ifn}')
    print(f'ofn: {ofn}')
    print(' ')

    df_txt = pd.read_csv(ifn, delim_whitespace=True)
    print('df_txt.info()')
    print(f'{df_txt.info()}')
    print(' ')

    # Find names of all seas
    sea_names = df_txt.Name.unique().tolist()
    # print(f'Unique sea names: {sea_names}')
    print(f'Number of unique sea names: {len(sea_names)}')
    print(' ')

    # Start the GeoDataFrame
    gdf = gpd.GeoDataFrame(crs='epsg:4326')
    gdf['geometry'] = None

    # Exclusion list: "overarching" sea_names
    excluded = (
        'Pacific_Ocean,_western_part',
        'Pacific_Ocean,_eastern_part',
        'North_Pacific_Ocean,_western_part',
        'North_Pacific_Ocean,_eastern_part',
        'North_Atlantic_Ocean',
        'Atlantic_Ocean',
        'Arctic_Ocean,_western_part',
        'Arctic_Ocean,_eastern_part',
        'Indian_Ocean',
        'Eastern_Basin',
        'Mediterranean_Region',
    )

    # Build a coordinates polygon for each Sea
    gdf_index = 0
    for sea_name in sea_names:
        if sea_name in excluded:
            print(f'Excluding (list): {sea_name}')
            continue

        df_sea = df_txt[df_txt['Name'] == sea_name]
        # print(f'df[{sea_name}]:')
        # print(f'{df_sea}')
        coords = get_coords(df_sea, nh_only=is_nh, sh_only=is_sh)
        if coords is None:
            print(f'Excluding (coords): {sea_name}')
            continue

        poly = Polygon(coords)

        gdf.loc[gdf_index, 'geometry'] = poly
        gdf.loc[gdf_index, 'Region'] = sea_name
        gdf.loc[gdf_index, 'Sea_ID'] = df_sea.iloc[0]['Sea_ID']

        gdf_index += 1

    # Set the CRS
    # gdf.crs = from_epsg(4326)

    # Check...
    print(gdf.info())
    print(' ')

    # Write the output
    gdf.to_file(ofn)
    print(f'Wrote: {ofn}')
    print(f'Total Seas: {gdf_index}')
    print(' ')


if __name__ == '__main__':
    try:
        ifn = sys.argv[1]
    except IndexError:
        print('Missing 1st arg: input fname (txt)')

    try:
        ofn = sys.argv[2]
    except IndexError:
        print('Missing 2nd arg: output fname (shp)')

    is_nh = '_nh' in ifn or 'nh_' in ifn
    is_sh = '_sh' in ifn or 'sh_' in ifn

    try:
        assert is_nh ^ is_sh  # ^ means xor
    except AssertionError:
        xwm(f'Need only one of nh ({is_nh}) or sh ({is_sh}) in ifn: {ifn}')

    gen_shapefile(ifn, ofn, is_nh, is_sh)
