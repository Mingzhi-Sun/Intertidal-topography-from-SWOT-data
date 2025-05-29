import os
from netCDF4 import Dataset
from datetime import datetime, timedelta
import numpy as np

file_path = r"H:\SWOT_L2_HR_PIXC_Intertidal_topography\Jiangsu\23"
save_path = r"F:\Intertidal_topography\3Result_with_all_correction\CYCLE23"

# 江苏
lon_min, lon_max = 120.9, 121.4
lat_min, lat_max = 32.5, 33.4

names = os.listdir(file_path)
for name in names:
    SWOT_L2_HR_PIXC_path = os.path.join(file_path, name)
    print(SWOT_L2_HR_PIXC_path)
    # 读取数据文件
    SWOT_L2_HR_PIXC = Dataset(SWOT_L2_HR_PIXC_path)
    # 获取数据
    pixel_cloud = SWOT_L2_HR_PIXC.groups["pixel_cloud"]
    lat = pixel_cloud["latitude"][:]
    lon = pixel_cloud["longitude"][:]
    classification = pixel_cloud["classification"][:]
    sig0_qual = pixel_cloud["sig0_qual"][:]


    # 筛选出指定经纬度范围内的数据 & 质量控制
    mask = (lon >= lon_min) & (lon <= lon_max) & (sig0_qual == 0) & \
           (lat >= lat_min) & (lat <= lat_max)

    # 虚拟验潮站
    lon_min_tide, lon_max_tide = 121.05, 121.055
    lat_min_tide, lat_max_tide = 32.95, 33.05
    # lat_min_tide, lat_max_tide = 32.9, 33.25     # set for cycle 17
    mask_tide_station = (lon >= lon_min_tide) & (lon <= lon_max_tide) & (sig0_qual == 0) &\
                        (classification == 4) & (lat >= lat_min_tide) & (lat <= lat_max_tide)

    # 起始时间（2000年1月1日零时）
    start_time = datetime(2000, 1, 1)

    # 检查是否有符合条件的数据
    if np.any(mask):
        print("有数据")
        sig0 = pixel_cloud["sig0"][:]
        height = pixel_cloud["height"][:] - pixel_cloud["geoid"][:]
        illumination_time = pixel_cloud["illumination_time"][:]
        # 辅助数据
        ancillary_surface_classification_flag = pixel_cloud["ancillary_surface_classification_flag"][:]
        sig0_qual = pixel_cloud["sig0_qual"][:]
        classification_qual = pixel_cloud["classification_qual"][:]
        bright_land_flag = pixel_cloud["bright_land_flag"][:]
        water_frac_uncert = pixel_cloud["water_frac_uncert"][:]
        water_frac = pixel_cloud["water_frac"][:]
        pole_tide = pixel_cloud["pole_tide"][:]
        solid_earth_tide = pixel_cloud["solid_earth_tide"][:]

        # 提取符合条件的数据
        print("筛选数据")
        selected_lon = lon[mask]
        selected_lat = lat[mask]
        selected_sig0 = sig0[mask]
        selected_classification = classification[mask]
        selected_ancillary_surface_classification_flag = ancillary_surface_classification_flag[mask]
        selected_sig0_qual = sig0_qual[mask]
        selected_classification_qual = classification_qual[mask]
        selected_bright_land_flag = bright_land_flag[mask]
        selected_water_frac_uncert = water_frac_uncert[mask]
        selected_water_frac = water_frac[mask]
        selected_pole_tide = pole_tide[mask]
        selected_solid_earth_tide = solid_earth_tide[mask]
        # 计算水位高度，考虑固体潮、极潮改正
        selected_height = height[mask] + selected_pole_tide + selected_solid_earth_tide


        # 卫星过境时间 UTC请注意时差
        selected_time = illumination_time[mask]
        selected_dates = [start_time + timedelta(seconds=sec) for sec in selected_time]
        swot_time_overfly = selected_dates[0].strftime('%Y%m%dT%Hh%Mm%Ss')
        print(swot_time_overfly)


        # 检查 sig0 的数据类型
        if np.issubdtype(selected_sig0.dtype, np.str_):
            # 如果 sig0 是字符串类型，替换 "--" 为 NaN 并转换为浮点数
            processed_sig0 = np.where(selected_sig0 == "--", np.nan, selected_sig0).astype(float)
        else:
            # 如果 sig0 是数值类型，直接处理，将大于 3000 的值替换为 NaN
            processed_sig0 = np.where(selected_sig0 > 3000, np.nan, selected_sig0)

        formatted_data = [
            f"{lon:.8f}\t{lat:.8f}\t{height:.6f}\t{classification:.1f}\t{sig0:.6f}\t" \
            f"{ancillary_surface_classification_flag:.1f}\t{water_frac:.6f}\t{water_frac_uncert:.6f}"

            for lon, lat, height, classification, sig0, ancillary_surface_classification_flag,water_frac,water_frac_uncert in

            zip(selected_lon, selected_lat, selected_height, selected_classification, processed_sig0,
                selected_ancillary_surface_classification_flag,selected_water_frac, selected_water_frac_uncert)
        ]


        # 保存到 txt 文件
        output_file = os.path.join(save_path, f"{name[0:-42]}_{swot_time_overfly}.dat")
        with open(output_file, 'w') as f:
            f.write(
                "# Longitude\tLatitude\theight\tclassification\tsig0\tancillary_surface_classification_flag\twater_frac\twater_frac_uncert\n")
            f.write("\n".join(formatted_data))