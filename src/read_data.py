# TODO: Write the function to read the data from gesture capturing and return it to lstm
import pandas as pd
import numpy as np
import ast
from os.path import dirname, abspath
import os
from pathlib import Path
from dataclass import Data
import re


def read_data():
    parent_directory = dirname(dirname(abspath(__file__)))
    parent_directory = Path(parent_directory)
    path = parent_directory / "HandDataset"
    file_names_dummy = os.listdir(str(path))
    file_names = []
    data_list = []
    for file in file_names_dummy:
        if file.endswith(".txt"):
            file_names.append(file)

    for file_name in file_names:
        file_path = parent_directory / "HandDataset" / file_name
        file = open(str(file_path), 'r')
        label = re.sub(r"_\d", "", file_name.replace('.txt', '')).replace('gesture', '')
        dataframes = file.readlines()
        empty_list = []
        for frame in dataframes:
            frame = ast.literal_eval(frame)
            df = pd.DataFrame(frame)
            empty_list.append(df)
        data_array = np.asarray(empty_list)
        data_1 = Data(data=data_array, label=label)
        data_list.append(data_1)
    return data_list