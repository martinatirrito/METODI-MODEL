import traceback

import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    def fillDDEmployee(self):
        employee = self._model.getAllEmployee()
        for e in employee:
            self._view._ddEmployee.options.append(ft.dropdown.Option(e))
        self._view.update_page()

    def handleCreaGrafo(self, e):
        employee = self._view._ddEmployee.value

        if employee is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(ft.Text(f'Errore, scegliere un dipendente.', color = "red"))
            self._view._page.update()
            return

        try:
            self._model.buildGraph(employee)
            self._view._btnstampa.disabled = False
            self._view.txt_result.controls.clear()
            Nnodi, Narchi = self._model.getGraphDetails()
            self._view.txt_result.controls.append(
                ft.Text("Grafo correttamente creato.")
            )
            self._view.txt_result.controls.append(
                ft.Text(f"Numero di nodi: {Nnodi}")
            )
            self._view.txt_result.controls.append(
                ft.Text(f"Numero di archi: {Narchi}")
            )

            self._view._page.update()

        except Exception as ex:
            traceback.print_exc()
            self._view.create_alert(f"Errore nella creazione del grafo: {ex}")
            #self._view.txt_result.controls.append(ft.Text(f"Errore nella creazione del grafo: {ex}")) se non ho il metodo nella view
            #self._view._page.update()


    def handleSampaInfo(self, e):
        self._view.txt_result.controls.clear()

        nNodi, nArchi = self._model.getGraphDetails()
        if nNodi == 0:
            self._view.create_alert("Creare prima il grafo.")
            return

        try:

        #TOP 5 ARCHI PESO MAGGIORE DECRESCENTE A PARITA' DI PESO ORDINE ALFABETICO
            top5 = self._model.getTop5Archi()
            self._view.txt_result.controls.append(ft.Text("Top 5 archi:", color = "red"))
            for a in top5:
                self._view.txt_result.controls.append(ft.Text(f'{a[0]} -> {a[1]} : {a[2]}')) #a[2]["weight"] errore perchè ho preso i data nel mio model!!!

        #MAGGIOR NUMERO ARCHI USCENTI E ENTRANTI
            best_node, max_degree = self._model.getBestUscenti()
            self._view.txt_result.controls.append(ft.Text(f'Maggior numero archi uscenti: {best_node} {max_degree}', color = "red"))

            #STAMPA SE HO PIU' NODI PARIMERITO
            best_nodes, max_degree = self._model.getBestEntranti()
            self._view.txt_result.controls.append(
                ft.Text(f"Nodi con più archi entranti", color = "red"))
            for n in best_nodes:
                self._view.txt_result.controls.append(
                    ft.Text(f"{n.FirstName} {n.LastName}: {max_degree}"))

        #SOMMA PESI USCENTI PIU' ALTA
            best_nodes, max_peso = self._model.getMaxPesoUscente()
            self._view.txt_result.controls.append(
                ft.Text(f"Somma pesi uscenti più alta", color = "red"))
            for n in best_nodes:
                self._view.txt_result.controls.append(
                    ft.Text(f"{n.FirstName} {n.LastName}: {max_peso}"))

        #SOMMA PESI ENTRANTI PIU' ALTA
            best_nodes, max_peso = self._model.getMaxPesoEntrante()
            self._view.txt_result.controls.append(
                ft.Text(f"Somma pesi entranti più alta", color="red"))
            for n in best_nodes:
                self._view.txt_result.controls.append(
                    ft.Text(f"{n.FirstName} {n.LastName}: {max_peso}"))

        #COMPONENTI CONNESSE
            num_components, largest, largestOrdinata = self._model.getComponentiConnesse()
            self._view.txt_result.controls.append(
                ft.Text(f"Il grafo ha {num_components} componenti connesse debolmente."))
            self._view.txt_result.controls.append(
                ft.Text(f'Componente connessa più grande ({len(largest)} nodi)', color="red"))
            for c in largest:
                self._view.txt_result.controls.append(ft.Text(str(c)))

        #SUCCESSORI
            lista = self._model.getSuccessori()
            self._view.txt_result.controls.append(ft.Text(f"I successori sono {len(lista)}"))
            for s in lista:
                self._view.txt_result.controls.append(ft.Text(str(s)))

        #RAGGIUNGIBILI
            numeroNodiRaggiungibili = self._model.getNumRaggiungibili()
            self._view.txt_result.controls.append(ft.Text(f"I nodi raggiungibili sono {numeroNodiRaggiungibili}"))

        #RAGGIUNGIBILI CON VISITA
        """
            nodi = self._model.getBFSNodesFromEdges(source) #IL SOURCE SARA IL MIO VALORE DEL NODO
            self._view.txt_result.controls.append(
                ft.Text(f"Visita in ampiezza da {source.FirstName}: {len(nodi)} nodi", color="red"))
            for i, n in enumerate(nodi, start=1):
                self._view.txt_result.controls.append(ft.Text(f"{i}. {n.FirstName} {n.LastName}"))
            self._view.update_page()
        """

            
            self._view.update_page()

    except Exception as ex:
        traceback.print_exc()
        self._view.create_alert(f"Errore nella stampa delle info: {ex}")

