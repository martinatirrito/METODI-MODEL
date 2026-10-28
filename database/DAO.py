from database.DB_connect import DBConnect
from model.arco import Arco
from model.customer import Customer


class DAO():
    @staticmethod
    def getAllEmployee():
        try:
            conn = DBConnect.get_connection()
            cursor = conn.cursor(dictionary=True)

        except ConnectionError:
            print("Errore di connessione al databse")
            return

        result = []

        query = """select distinct e.FirstName as employee
                    from Employee e, Customer c
                    where e.ReportsTo is not NULL
                    and e.EmployeeId = c.SupportRepId
                    """

        cursor.execute(query, )

        for row in cursor:
            result.append(row["employee"])

        cursor.close()
        conn.close()
        return result


    @staticmethod
    def getAllNodes(employee): #i clienti seguiti da quel dipendente
        try:
            conn = DBConnect.get_connection()
            cursor = conn.cursor(dictionary=True)

        except ConnectionError:
            print("Errore di connessione al databse")
            return

        result = []

        query = """select distinct c.*
                    from Customer c, Employee e
                    where c.SupportRepId = e.EmployeeId and e.FirstName = %s"""

        cursor.execute(query, (employee, ))

        for row in cursor:
            result.append(Customer(**row))

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllEdges(employee, idMapC):  # due clienti sono collegati se hanno comprato almeno una traccia dello stesso album.
        # Arco orientato dal cliente che ha speso di più a quello che ha speso meno (con i pari in entrambe le direzioni).
        try:
            conn = DBConnect.get_connection()
            cursor = conn.cursor(dictionary=True)

        except ConnectionError:
            print("Errore di connessione al databse")
            return

        result = []

        query = """select c1.CustomerId as c1, c2.CustomerId as c2, count(distinct c1.AlbumId) as peso
                    from (select c.CustomerId , i.Total, t.TrackId, a.AlbumId
                            from Customer c, Employee e, Invoice i, InvoiceLine il, Track t, Album a
                            where c.SupportRepId = e.EmployeeId and e.FirstName = %s and c.CustomerId = i.CustomerId
                            and i.InvoiceId = il.InvoiceId and il.TrackId = t.TrackId and t.AlbumId = a.AlbumId ) c1, 
                                (select c.CustomerId , i.Total, t.TrackId, a.AlbumId
                                    from Customer c, Employee e, Invoice i, InvoiceLine il, Track t, Album a
                                    where c.SupportRepId = e.EmployeeId and e.FirstName = %s and c.CustomerId = i.CustomerId
                                    and i.InvoiceId = il.InvoiceId and il.TrackId = t.TrackId and t.AlbumId = a.AlbumId ) c2,
                                        (select c.CustomerId, sum(i.Total) as spesaTotale
                                        from Customer c, Employee e, Invoice i
                                        where c.SupportRepId = e.EmployeeId and e.FirstName = %s and c.CustomerId = i.CustomerId
                                        group by c.CustomerId) st1, 
                                            (select c.CustomerId, sum(i.Total) as spesaTotale
                                                from Customer c, Employee e, Invoice i
                                                where c.SupportRepId = e.EmployeeId and e.FirstName = %s and c.CustomerId = i.CustomerId
                                                group by c.CustomerId) st2
                    where c1.CustomerId != c2.CustomerId
                    and c1.AlbumId = c2.AlbumId
                    and c1.CustomerId = st1.CustomerId and c2.CustomerId = st2.CustomerId
                    and st1.spesaTotale >= st2.spesaTotale
                    group by c1.CustomerId, c2.CustomerId
                    order by peso desc"""


        cursor.execute(query, (employee, employee, employee, employee))

        for row in cursor:
            result.append(Arco(idMapC[row["c1"]], idMapC[row["c2"]], row["peso"]))

        cursor.close()
        conn.close()
        return result