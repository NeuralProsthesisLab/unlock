
__author__ = 'jpercent'

class DataLoader(object):
    def __init__(self):
        super(DataLoader, self).__init__()

class FileSystemDataLoader(object):
    def __init__(self, file_name, separator=','):
        self.file_name = file_name
        self.separator = separator

    def load(self):
        raw_file = open(self.file_name, 'r')
        words = line.split(',')
        for line in fin:

            time.append(float(words[1]))
            signal.append(float(words[0]))
        fin.close()

        time,signal = np.array(time),np.array(signal)

class Schema(object):
    def __init__(self, data, timestamps, trigger):
        self.data_indices = data
        self.sample_timestamp_indices = timestamps
        self.trigger_indices = triggers

    def data(self):
        return self.data_indices

    def timestamps(self):
        return self.sample_timestamp_indicies

    def triggers(self):
        return self.triggers_indicies

class DataTable(object):
    def __init__(self, schema, loader):
        self.schema = schema
        self.file_name = file_name

    def load_data(self):
        self.raw_data = self.loader.load()



samplingRate = time.size / time[-1]



argParser = argparse.ArgumentParser()
argParser.add_argument('datafile')
args = argParser.parse_args()
