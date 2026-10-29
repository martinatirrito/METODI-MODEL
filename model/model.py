import statistics

import networkx as nx

from database.DAO import DAO


class Model:
    def __init__(self):
        self._graph = nx.DiGraph()
        self._idMapC = {}

    def buildGraph(self, employee):
        self._graph.clear()
        self._idMapC.clear()

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

#TOP N ARCHI NON ORDINATI
    def getTop3Archi(self):
        return sorted(self._graph.edges(data=True), key=lambda x: x[2]["weight"], reverse=True)[:3]

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

# COMPONENTE PIU' GRANDE: per ogni nodo il PESO MASSIMO dei suoi archi incidenti
    #Per ogni nodo della componente connessa più grande,
    # stampare il peso massimo tra i suoi archi incidenti, in ordine decrescente.”
    def getLargestPesoMaxIncidente(self):
        if len(self._graph.nodes) == 0:
            return []
        largest = max(nx.weakly_connected_components(self._graph), key=len)
        # NON ORIENTATO: nx.connected_components

        lista = []
        for n in largest:
            # ORIENTATO: archi uscenti + entranti
            pesi = [d['weight'] for u, v, d in self._graph.out_edges(n, data=True)]
            pesi += [d['weight'] for u, v, d in self._graph.in_edges(n, data=True)]
            # NON ORIENTATO: pesi = [d['weight'] for u, v, d in self._graph.edges(n, data=True)]
            lista.append((n, max(pesi) if pesi else 0))

        lista.sort(key=lambda x: (-x[1], x[0].FirstName))
        return lista
        # peso MINIMO: min(pesi) e sort con +x[1] se lo chiede crescente

#NUMERO COMPONENTI DEBOLMENTE CONNESSE E LA PIU GRANDE COMPONENTE CONNESSA
    #weakly ignora direzione dell'arco
    #strongly ogni nodo deve raggiungere ogni altro seguendo le frecce, è molto più restrittiva
    def getComponentiConnesse(self):
        if len(self._graph.nodes) == 0:
            return 0, [], [], []
        # nx.number_connected_components(self._graph) anche cosi per numero componente connessa

        # per grafo non orientato basta togliere weakly

        components = list(nx.weakly_connected_components(self._graph))  # len --> numero componenti connesse
        num_components = len(components)
        largest = max(components,key=len)  # usa la dimensione della componente per decidere qual è la più grande. Mi da tutti i nodi
        # len largest mi da quanti ce ne sono

        # STAMPARE NODI DI LARGEST ORDINATI IN SENSO DECRESCENTE DI GRADO DI NODI
        largestOrdinata = sorted(largest, key=lambda n: self._graph.degree(n), reverse=True)

        #STAMPARE IN ORDINE PER ARCHI ENTRANTI decrescente, a parimerito alfabetico (solo ORIENTATO)
        listaEntranti = [(n, self._graph.in_degree(n)) for n in largest]
        listaEntranti.sort(key=lambda x: (-x[1], x[0].FirstName))

        # VARIANTI (cambi solo la funzione dentro la lista, il sort resta uguale):
        #   archi uscenti:   self._graph.out_degree(n)
        #   peso entrante:   self._graph.in_degree(n, weight='weight')
        #   peso uscente:    self._graph.out_degree(n, weight='weight')
        #   peso incidente:  self._graph.degree(n, weight='weight')
        #   NON ORIENTATO:   self._graph.degree(n)  (non esistono in/out)

        return num_components, largest, largestOrdinata, listaEntranti

# COMPONENTE CONNESSA CHE CONTIENE UN NODO “Dato un cliente selezionato, stampare la dimensione della componente connessa a cui appartiene e i suoi nodi.”
    # NEL CONTROLLER comp = self._model.getComponenteDiNodo(source), poi len(comp) per la dimensione.
    def getComponenteDiNodo(self, source):
        # ORIENTATO (debole): cerco la componente che contiene source
        for c in nx.weakly_connected_components(self._graph):
            if source in c:
                return c
        return set()
        # NON ORIENTATO (più semplice): return nx.node_connected_component(self._graph, source)
        # FORTE: stesso for con nx.strongly_connected_components

#TUTTE LE COMPONENTI CON PIU' DI UN NODO, ordinate per dimensione decrescente
    def getComponentiNonBanali(self):
        components = list(nx.strongly_connected_components(self._graph))
        # DEBOLI (ORIENTATO): nx.weakly_connected_components
        # NON ORIENTATO:      nx.connected_components

        lista = [c for c in components if len(c) > 1]  # scarta quelle da 1 nodo
        lista.sort(key=lambda c: len(c), reverse=True)
        return lista
        # numero: len(lista); dimensione i-esima: len(lista[i])

# MIGLIOR INFLUENZA PESO ARC USCETE - PESO ARC ENTRANTE
    def getBestInfluenza(self):
        if len(self._graph.nodes) == 0:
            return None, 0
        listNodesPesata = []
        for n in self._graph.nodes:
            score = 0
            for a in self._graph.out_edges(n, data=True):  # arco uscente  #data = true : dammi gli attributi
                score += a[2]["weight"]  # il peso perchè è una tupla
            for a in self._graph.in_edges(n, data=True):  # entranti
                score -= a[2]["weight"]
            listNodesPesata.append((n, score))

        #listNodesPesata.sort(key=lambda x: (-x[1], x[0].FirstName)) alfabetico
        listNodesPesata.sort(key=lambda x: x[1], reverse=True)
        return listNodesPesata[0]

# TOP N NODI PIU PROFITTEVOLI
    def getNodiPiuProfittevoli(self):
        # deve per ogni nodo associare la somma dei pesi uscenti meno la somma dei pesi entranti
        listNodesPesata = []
        for n in self._graph.nodes:
            score = 0
            for a in self._graph.out_edges(n, data=True):  # arco uscente  #data = true : dammi gli attributi
                score += a[2]["weight"]  # il peso perchè è una tupla
            for a in self._graph.in_edges(n, data=True):  # entranti
                score -= a[2]["weight"]
            listNodesPesata.append((n, score))

        listNodesPesata.sort(key=lambda x: x[1], reverse=True)

        return listNodesPesata[0:5]

#SUCCESSORI DI UN NODO ORDINATI PER PESO
    def getSuccessori(self, source):
        #source = self._idMapC[int(idSource)]
        lista = [(n, self._graph[source][n]['weight']) for n in self._graph.successors(source)]
        lista.sort(key=lambda x: (-x[1], x[0].FirstName))
        return lista
    # entranti: predecessors(source) e peso self._graph[n][source]['weight']
    # NON ORIENTATO: neighbors(source) al posto di successors

# PREDECESSORI DI UN NODO ORDINATI PER PESO (solo ORIENTATO)
    def getPredecessori(self, source):
        lista = [(n, self._graph[n][source]['weight']) for n in self._graph.predecessors(source)]
        # attenzione: l'arco va da n a source, quindi [n][source] e non [source][n]
        lista.sort(key=lambda x: (-x[1], x[0].FirstName))
        return lista

# TUTTI I VICINI (entranti + uscenti, senza duplicati)
    def getVicini(self, source):
        vicini = set(self._graph.successors(source)) | set(self._graph.predecessors(source))
        # NON ORIENTATO: list(self._graph.neighbors(source))
        return sorted(vicini, key=lambda n: n.FirstName)

# VICINI/ADIACENTI ORDINATI PER PESO (NON ORIENTATO)
    def getViciniPesati(self, source):
        lista = [(v, self._graph[source][v]['weight']) for v in self._graph.neighbors(source)]
        lista.sort(key=lambda x: x[1], reverse=True)
        return lista
        # ORIENTATO: per gli uscenti usa getSuccessori, per gli entranti getPredecessori

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

#NODI ISOLATI (vale per ORIENTATO e NON ORIENTATO)
    def getNodiIsolati(self):
        return list(nx.isolates(self._graph))
        # equivalente a mano: [n for n in self._graph.nodes if self._graph.degree(n) == 0]

    # "numero di nodi isolati"
    def getNumIsolati(self):
        return nx.number_of_isolates(self._graph)

# ARCHI CON PESO SOPRA LA MEDIA
    #Raccolgono tutti i pesi in una lista.
    #Calcolano la media, che è sum/len, oppure la mediana.
    #Rileggono gli archi e tengono solo quelli col peso sopra la soglia.
    def getArchiSopraMedia(self):
        if len(self._graph.edges) == 0:
            return 0, []

        pesi = [d['weight'] for u, v, d in self._graph.edges(data=True)]
        media = sum(pesi) / len(pesi)

        archi = [(u, v, d['weight']) for u, v, d in self._graph.edges(data=True)
                    if d['weight'] > media]
        archi.sort(key=lambda x: -x[2])  # dal più pesante
        return media, archi
        # quanti sono: len(archi)
        # "maggiore o uguale" -> usa >=
#questi due metodi sopra e sotto valgono per ORIENTATI E NON
# ARCHI CON PESO SOPRA LA MEDIANA
    def getArchiSopraMediana(self):
        if len(self._graph.edges) == 0:
            return 0, []

        pesi = [d['weight'] for u, v, d in self._graph.edges(data=True)]
        mediana = statistics.median(pesi)

        archi = [(u, v, d['weight']) for u, v, d in self._graph.edges(data=True)
                 if d['weight'] > mediana]
        archi.sort(key=lambda x: -x[2])
        return mediana, archi

# ARCHI DI PESO MASSIMO (tutti, anche a parimerito)
    def getArchiPesoMax(self):
        if len(self._graph.edges) == 0:
            return 0, []

        max_peso = max(d['weight'] for u, v, d in self._graph.edges(data=True))
        archi = [(u, v, d['weight']) for u, v, d in self._graph.edges(data=True)
                 if d['weight'] == max_peso]
        return max_peso, archi
        # peso MINIMO: min(...) al posto di max(...)

# NODI POZZO: nessun arco uscente, almeno uno entrante (solo ORIENTATO)
    def getNodiPozzo(self):
        return [n for n in self._graph.nodes
                if self._graph.out_degree(n) == 0 and self._graph.in_degree(n) > 0]

# NODI SORGENTE: nessun arco entrante, almeno uno uscente (solo ORIENTATO)
    def getNodiSorgente(self):
        return [n for n in self._graph.nodes
                if self._graph.in_degree(n) == 0 and self._graph.out_degree(n) > 0]

# ARCHI SOPRA/SOTTO UNA SOGLIA
    def getArchiSoglia(self, soglia):
        sopra = 0
        sotto = 0
        for u, v, d in self._graph.edges(data=True):
            if d['weight'] > soglia:
                sopra += 1
            elif d['weight'] < soglia:
                sotto += 1
            # uguali alla soglia: non contati (leggi bene la traccia: >= / <=)
        return sopra, sotto
    """ nel controller:
    sogliaStr = self._view._txtSoglia.value
    try:
        soglia = float(sogliaStr)      # int(...) se la traccia dice "intero"
    except ValueError:
        self._view.create_alert("Inserire un numero valido.")
        return
    sopra, sotto = self._model.getArchiSoglia(soglia)
    """

#CAMMINO MINIMO DUE NODI “Selezionati due clienti A e B, stampare il cammino più breve da A a B (numero di archi) e il suo peso totale.”
    # (ORIENTATO e NON ORIENTATO)
    def getCamminoMinimo(self, source, target):
        if not nx.has_path(self._graph, source, target):
            return [], 0

        # minimo NUMERO DI ARCHI (ignora i pesi)
        path = nx.shortest_path(self._graph, source, target)
        # minimo PESO TOTALE: nx.shortest_path(self._graph, source, target, weight='weight')

        peso = sum(self._graph[path[i]][path[i + 1]]['weight'] for i in range(len(path) - 1))
        return path, peso
        # numero archi = len(path) - 1

# TOP N NODI PER PESO MEDIO DEGLI ARCHI USCENTI
    #Per ogni nodo con almeno un arco uscente, calcolare il peso medio degli archi uscenti. Stampare i primi 5 in ordine decrescente
    def getTopPesoMedio(self, n=5):
        lista = []
        for nodo in self._graph.nodes:
            k = self._graph.out_degree(nodo)  # quanti archi
            if k > 0:  # evita divisione per zero
                somma = self._graph.out_degree(nodo, weight='weight')
                lista.append((nodo, somma / k))
        lista.sort(key=lambda x: (-x[1], x[0].FirstName))
        return lista[:n]
        # ENTRANTI: in_degree   NON ORIENTATO: degree


    def getAllEmployee(self):
        return DAO.getAllEmployee()

    def getClienti(self):
        return list(self._graph.nodes)

