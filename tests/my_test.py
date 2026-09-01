import pytest

from calculations.add import add, BackAccount, InsufficientFundsError


@pytest.fixture
def zero_bank_account():
    return BackAccount()


@pytest.fixture
def bank_account_with_initial_balance():
    return BackAccount(1000)


@pytest.mark.parametrize("num1,num2,expected", [(1, 2, 3), (2, 3, 5)])
def test_add(num1, num2, expected):
    assert add(num1, num2) == expected


def test_bank_set_initial_balance(bank_account_with_initial_balance):
    assert bank_account_with_initial_balance.balance == 1000


def test_bank_default_balance(zero_bank_account):
    assert zero_bank_account.balance == 0


def test_bank_deposit(zero_bank_account):
    zero_bank_account.deposit(1000)
    assert zero_bank_account.balance == 1000


def test_bank_withdraw(bank_account_with_initial_balance):
    bank_account_with_initial_balance.withdraw(500)
    assert bank_account_with_initial_balance.balance == 500


def test_bank_withdraw_more_than_balance(bank_account_with_initial_balance):
    with pytest.raises(InsufficientFundsError):
        bank_account_with_initial_balance.withdraw(1500)
