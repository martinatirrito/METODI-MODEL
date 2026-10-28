import networkx as nx

from database.DAO import DAO


class Model:
    def __init__(self):
        self._graph = nx.DiGraph()
        self._idMapC = {}

    def buildGraph(self, employee):
        self._graph.clear()

        nodi = DAO.getAllNodes(employee)
        for c in nodi:
            self._idMapC[c.CustomerId] = c
        self._graph.add_nodes_from(nodi)

        edges = DAO.getAllEdges(employee, self._idMapC)
        for e in edges:
            self._graph.add_edge(e.c1, e.c2, weight = e.peso)

    def getGraphDetails(self):
        return len(self._graph.nodes), len(self._graph.edges)

#TOP N ARCHI ORDINATI
    #QUESTO METODO VA BENE SOLO SE IL GRAFO NON è ORIENTATO
    """ 
    def getTop5Archi(self):
        if len(self._graph.edges) == 0:
            return []

        edges_with_weights = []
        for u, v in self._graph.edges:
            u, v = sorted((u, v), key=lambda c: c.FirstName)
            edges_with_weights.append((u, v, self._graph[u][v]['weight']))

        edges_sorted = sorted(edges_with_weights,
                              key=lambda x: (-x[2], x[0].FirstName, x[1].FirstName))

        return edges_sorted[:5]
    """
    #GRAFO ORIENTATO:
    def getTop5Archi(self):
        if len(self._graph.edges) == 0:
            return []

        edges_with_weights = []
        for u, v, d in self._graph.edges(data=True):
            edges_with_weights.append((u, v, d['weight']))

        edges_sorted = sorted(edges_with_weights,
                              key=lambda x: (-x[2], x[0].FirstName, x[1].FirstName))

        return edges_sorted[:5]

#MAGGIOR NUMERO ARCHI USCENTI
    def getBestUscenti(self):
        if len(self._graph.nodes) == 0:
            return None, 0

        max_degree = -1
        best_node = None
        for node, degree in self._graph.out_degree():
            if degree > max_degree:
                max_degree = degree
                best_node= node
        return best_node, max_degree

#MAGGIOR NUMERO ARCHI ENTRANTI
    def getBestEntranti(self):
        if len(self._graph.nodes) == 0:
            return None, 0

        max_degree = -1
        best_nodes = None
        for node, degree in self._graph.in_degree():
            if degree > max_degree:
                max_degree = degree
                best_nodes = [n for n, d in self._graph.in_degree() if d == max_degree]  #COSI HO PIU NODI SE C'E' PARIMERITO
        return best_nodes, max_degree

    #ARCHI USCENTI ED ENTRANTI LI POSSONO AVERE SOLO GRAFI ORIENTATI
#GRADO
    #NEL CASO DI GRAFI NON ORIENTATI PUO' ESSERE CHIESTO SOLO IL GRADO
    #QUESTO METODO VA BENE PER TROVARE IL GRADO ANCHE DI UN GRAFO NON ORIENTATO QUANDO NON VIENE PRECISATO ENTRANTE O USCENTE
    """
    def getBestNodoDegree(self):
        if len(self._graph.nodes) == 0:
            return None, 0

        max_degree = -1
        best_artist = None
        for node, degree in self._graph.degree():
            if degree > max_degree:
                max_degree = degree
                best_artist = node  #se non voglio più di uno metto la lista come fatto sopra
        return best_artist, max_degree
    """

#SOMMA PESI USCENTI PIU' ALTA
    def getMaxPesoUscente(self):
        if len(self._graph.nodes) == 0:
            return [], 0

        max_peso = max(self._graph.out_degree(n, weight='weight') for n in self._graph.nodes)
        best_nodes = [n for n in self._graph.nodes
                      if self._graph.out_degree(n, weight='weight') == max_peso]
        return best_nodes, max_peso

#SOMA PESI ENTRANTI PIU' ATA
    def getMaxPesoEntrante(self):
        if len(self._graph.nodes) == 0:
            return [], 0

        max_peso = max(self._graph.in_degree(n, weight='weight') for n in self._graph.nodes)
        best_nodes = [n for n in self._graph.nodes
                      if self._graph.in_degree(n, weight='weight') == max_peso]
        return best_nodes, max_peso

# SOMMA PESI INCIDENTI
    # pesi incidenti si calcolano in un grafo non orientato perchè non ha pesi uscenti e entranti
    """
    questo va solo su non orientato perchè usa neighbours
    restituisco solo un nodo quindi in caso li voglio tutti metto lista best nodes come prima 

    def getSommaPesiIncidenti(self):
        if len(self._graph.nodes) == 0:
            return None, 0

        max_sum = -1
        best_artist = None
        for node in self._graph.nodes:
            weight_sum = sum(
                self._graph[node][neighbor]['weight']
                for neighbor in self._graph.neighbors(node)
            )
                if weight_sum > max_sum:
                max_sum = weight_sum
                best_artist = node
        return best_artist, max_sum
    """
    # versione universale
    # invece questo posso usarlo anche in uno orientato e mi da entranti + uscenti
    def getMaxPesoIncidente(self):
        if len(self._graph.nodes) == 0:
            return [], 0

        max_peso = max(self._graph.degree(n, weight='weight') for n in self._graph.nodes)
        best_nodes = [n for n in self._graph.nodes
                      if self._graph.degree(n, weight='weight') == max_peso]
        return best_nodes, max_peso

#NUMERO COMPONENTI DEBOLMENTE CONNESSE E LA PIU GRANDE COMPONENTE CONNESSA
    #weakly ignora direzione dell'arco
    #strongly ogni nodo deve raggiungere ogni altro seguendo le frecce, è molto più restrittiva
    def getComponentiConnesse(self):
        # nx.number_connected_components(self._graph) anche cosi per numero componente connessa

        components = list(nx.weakly_connected_components(self._graph))  # len --> numero componenti connesse
        num_components = len(components)
        largest = max(components,
                      key=len)  # usa la dimensione della componente per decidere qual è la più grande. Mi da tutti i nodi
        # len largest mi da quanti ce ne sono

        # STAMPARE NODI DI LARGEST ORDINATI IN SENSO DECRESCENTE DI GRADO DI NODI
        largestOrdinata = sorted(largest, key=lambda n: self._graph.degree(n), reverse=True)

        return num_components, largest, largestOrdinata

    #per grafo non orientato basta togliere weakly

#SUCCESSORI DI UN NODO ORDINATI PER PESO
    def getSuccessori(self, source):
        lista = [(n, self._graph[source][n]['weight']) for n in self._graph.successors(source)]
        lista.sort(key=lambda x: (-x[1], x[0].FirstName))
        return lista
    # entranti: predecessors(source) e peso self._graph[n][source]['weight']
    # NON ORIENTATO: neighbors(source) al posto di successors

#NODI RAGGIUNGIBILI
    # "numero di nodi raggiungibili da un nodo" (sorgente ESCLUSA)
    def getNumRaggiungibili(self, source):
        return len(nx.descendants(self._graph, source))  # ORIENTATO
        # NON ORIENTATO: len(nx.node_connected_component(self._graph, source)) - 1 #-1 per escludere la sorgente

    # VISITE: stessi nodi, ordine diverso
    #se non viene specificato ampiezza e profondita i nodi raggiungibili è uguale farlo con nc.descendants o con bfs/dfs
    # BFS = in ampiezza (per livelli), DFS = in profondità
    def getBFSNodesFromEdges(self, source):  # sorgente ESCLUSA
        return [v for u, v in nx.bfs_edges(self._graph, source)]

    def getDFSNodesFromEdges(self, source):  # sorgente ESCLUSA
        return [v for u, v in nx.dfs_edges(self._graph, source)]

    def getBFSNodesFromTree(self, source):  # sorgente INCLUSA
        return list(nx.bfs_tree(self._graph, source).nodes())

    def getDFSNodesFromTree(self, source):  # sorgente INCLUSA
        return list(nx.dfs_tree(self._graph, source).nodes())






    def getBestInfluenzaArtista(self):
        #MIGLIOR INFLUENZA PESO ARC USCETE - PESO ARC ENTRANTE
        listNodesPesata = []
        for n in self._graph.nodes:
            score = 0
            for a in self._graph.out_edges(n, data=True):  # arco uscente  #data = true : dammi gli attributi
                score += a[2]["weight"]  # il peso perchè è una tupla
            for a in self._graph.in_edges(n, data=True):  # entranti
                score -= a[2]["weight"]
            listNodesPesata.append((n, score))

        listNodesPesata.sort(key=lambda x: x[1], reverse=True)
        return listNodesPesata[0]

    def getAllEmployee(self):
        return DAO.getAllEmployee()

