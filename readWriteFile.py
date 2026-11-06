
'''写文件'''
def write_file(filepath, text):
    with open(filepath, 'w') as wf:
        wf.write(text + '\n')

'''读文件'''
def read_file(filepath):
    with open(filepath) as fp:
        content = fp.read();
    return content

'''读取某一行'''
def loadDataSet(fileName, n):
    with open(fileName) as fr:
        for line in fr.readlines()[n - 1 : n]:
            return line.strip('\n')