def add(num1, num2):
    return num1 + num2


class InsufficientFundsError(Exception):
    pass


class BackAccount:
    def __init__(self, balance=0):
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFundsError("Insufficient funds")
        self.balance -= amount

    def collect_interest(self, rate):
        self.balance *= 1 + rate
