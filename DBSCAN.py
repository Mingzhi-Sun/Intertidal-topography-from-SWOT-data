import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm  # 导入 tqdm 库


def DBSCAN_SWOT(file_path,output_file_path):
    # 初始化标准化器和 DBSCAN 模型
    scaler = StandardScaler()
    dbscan = DBSCAN(eps=0.1, min_samples=60)

    # 读取数据并显示进度条
    chunk_size = 200000  # 每次读取的行数，调整根据数据量大小
    final_results = []

    # 计算文件的总行数，用于设置进度条的最大值
    total_rows = sum(1 for _ in open(file_path))  # 计算文件总行数
    total_chunks = total_rows // chunk_size + 1  # 计算总共需要多少个数据块

    # 使用 tqdm 显示进度条，设置进度条为百分比格式
    for chunk in tqdm(pd.read_csv(file_path, sep='\s+', header=None, names=['Longitude', 'Latitude', 'Height'],
                                  chunksize=chunk_size, engine='python'),
                      desc="处理数据", total=total_chunks, unit="块", ncols=100,
                      bar_format="{l_bar}{bar}| {percentage:3.0f}%"):
        # 数据清洗
        chunk = chunk.apply(pd.to_numeric, errors='coerce')
        chunk = chunk.dropna()  # 去除 NaN 数据

        # 数据标准化
        data_scaled = scaler.fit_transform(chunk[['Longitude', 'Latitude', 'Height']])

        # DBSCAN 聚类
        cluster_labels = dbscan.fit_predict(data_scaled)

        # 添加聚类标签到数据
        chunk['Cluster'] = cluster_labels

        # 标记异常值
        chunk['Status'] = chunk['Cluster'].apply(lambda x: '异常' if x == -1 else '正常')

        # 将当前处理的块结果添加到最终结果列表
        final_results.append(chunk)

    # 合并所有处理结果并保存
    final_df = pd.concat(final_results, ignore_index=True)
    final_df.to_csv(output_file_path, index=False, header=False, sep=' ')

    print(f"处理后的数据已保存至 {output_file_path}")

# 设置文件路径

cycleNumber = "23"

passNumber1 = "159"

file_path = r"F:\Intertidal_topography\3Result_with_all_correction\CYCLE" + cycleNumber + "\c" + cycleNumber + "p" + passNumber1 + "DBSCAN_INPUT.dat"
output_file_path = r"F:\Intertidal_topography\3Result_with_all_correction\CYCLE" + cycleNumber + "\c" + cycleNumber + "p" + passNumber1 + "DBSCAN_OUTPUT.txt"
DBSCAN_SWOT(file_path,output_file_path)
