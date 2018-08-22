from vis.models.indexed_piece import Importer
import vis
VIS_path = vis.__path__[0]

folder = VIS_path + '/tests/corpus/elvisdownload2'
dendro_setts = {'graph_settings': {'filename_and_type': 'Dendrogram_output.png'}}
ap = Importer(folder)
intervals = ap.get('vertical_interval')
ap.get(combined_experimenter='dendrogram', data=[intervals], settings=dendro_setts)