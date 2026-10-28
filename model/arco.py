from dataclasses import dataclass

from model.customer import Customer


@dataclass
class Arco:
    c1: Customer
    c2: Customer
    peso: int
