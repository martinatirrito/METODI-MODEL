from dataclasses import dataclass


@dataclass
class Customer:
    CustomerId: int
    FirstName: str
    LastName: str
    Company: str
    Address: str
    City: str
    State: str
    Country: str
    PostalCode: str
    Phone: str
    Fax: str
    Email: str
    SupportRepId: int

    def __hash__(self):
        return hash(self.CustomerId)

    def __eq__(self, other):
        return self.CustomerId == other.CustomerId

    def __str__ (self):
        return f'{self.FirstName} {self.LastName}'