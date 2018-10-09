import metaplot.api as api
import os

class PTetraFiles(api.Reader):

    def rule(file):
        return os.path.basename(file.name) == "pictetra.hst"

    csv_parser = api.csv_parser(delimiter=' ')
    def parse(s):
        return [a for a in PTetraFiles.csv_parser(s) if a != '']

    def reader(file):
        csv_reader = api.csv_reader(file, parse=PTetraFiles.parse)
        line = None
        while not isinstance(line, api.DataLine):
            line = next(csv_reader)
        num_cols = len(line.data)
        num_objs = int((num_cols-6)/3)
        name = ['n', 't', 'ne', 'ni', 'Te', 'pot']
        long = ['timestep', 'time', 'electron density', 'ion density', '?', '?']
        units = ['1', 's', 'm**(-3)', 'm**(-3)', '1', '1']
        for i in range(num_objs):
            name.append('V[{}]'.format(i))
            name.append('Q[{}]'.format(i))
            name.append('I[{}]'.format(i))
            long.append('potential')
            long.append('charge')
            long.append('current')
            units.append('V')
            units.append('C')
            units.append('A')

        yield api.MetadataLine("xaxis", ["t"])
        yield api.MetadataLine("name", name)
        yield api.MetadataLine("long", long)
        yield api.MetadataLine("units", units)

        file.seek(0)
        csv_reader = api.csv_reader(file, parse=PTetraFiles.parse)
        for line in csv_reader:
            yield line
