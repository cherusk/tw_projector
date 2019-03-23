
from ascii_graph import Pyasciigraph

class Depictor:

    def __init__(self):
        pass

    def conjure(self, scenario):
        label = "Scenario (durations in weeks)"

        data = [tuple([k, v]) for k, v in
                sorted(scenario.items(), key=lambda v: v[1])]

        graph = Pyasciigraph(
                             line_length=100,
                             min_graph_length=50,
                             separator_length=10,
                             multivalue=False,
                             human_readable='si',
                             graphsymbol="*",
                             float_format='{0:,.0f}')

        for line in graph.graph(label=label, data=data):
            print(line)
