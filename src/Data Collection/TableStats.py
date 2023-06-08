import pandas as pd
import math
import pathlib

result_directory_path = str(pathlib.Path(__file__).parent.resolve()) + '/../../Results/'

modes = ['Basic', 'Standard', 'Improved', 'BasicReduced']

file_names = ['lc10{}'.format(i) for i in range(1, 10)]
file_names += ['lc20{}'.format(i) for i in range(1, 9)]
file_names += ['lr10{}'.format(i) for i in range(1, 10)]
file_names += ['lr11{}'.format(i) for i in range(3)]
file_names += ['lr20{}'.format(i) for i in range(1, 10)]
file_names += ['lr21{}'.format(i) for i in range(2)]
file_names += ['lrc10{}'.format(i) for i in range(1, 9)]
file_names += ['lrc20{}'.format(i) for i in range(1, 9)]

Dicts = [{} for i in range(len(modes))]

for i in range(len(modes)):
    mode = modes[i]
    for file_name in file_names:
        with open(result_directory_path + mode + r'/' + file_name + '.txt', 'r') as f:
            Data = f.readlines()
            Data = [float(data[:-1]) for data in Data]
            mean = sum(Data) / len(Data)
            std = math.sqrt(sum([(data - mean)*(data - mean) for data in Data]) / len(Data))
            Dicts[i].update({file_name : [round(mean, 2), round(std, 2)]})

for i in range(len(modes)):
    Dict = Dicts[i]
    mode = modes[i]

    df = pd.DataFrame(Dict)
    df = df.T
    df.to_excel(result_directory_path + mode + r'/Table.xls')


