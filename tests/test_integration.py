from src.models import Apartment, ApartmentSettlement, TenantSettlement
from src.manager import Manager
from src.models import Parameters
import pytest 


def test_load_data():
    parameters = Parameters()
    manager = Manager(parameters)
    assert isinstance(manager.apartments, dict)
    assert isinstance(manager.tenants, dict)
    assert isinstance(manager.transfers, list)
    assert isinstance(manager.bills, list)

    for apartment_key, apartment in manager.apartments.items():
        assert isinstance(apartment, Apartment)
        assert apartment.key == apartment_key

def test_tenants_in_manager():
    parameters = Parameters()
    manager = Manager(parameters)
    assert len(manager.tenants) > 0
    names = [tenant.name for tenant in manager.tenants.values()]
    for tenant in ['Jan Nowak', 'Adam Kowalski', 'Ewa Adamska']:
        assert tenant in names

def test_if_tenants_have_valid_apartment_keys():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.check_tenants_apartment_keys() == True

    manager.tenants['tenant-1'].apartment = 'invalid-key'
    assert manager.check_tenants_apartment_keys() == False
    
def test_get_apartment_costs():
    parameters = Parameters()
    manager = Manager(parameters)

    assert manager.get_apartment_costs("apart-polanka", 2025, 1) == 910.0
    assert manager.get_apartment_costs("apart-polanka", 2025, 2) == 0.0
    assert manager.get_apartment_costs("apart-polanka", 2025) == 910.0
    assert manager.get_apartment_costs("apart-polanka") == 910.0
    assert manager.get_apartment_costs("brak-mieszkania", 2025, 1) == None
    with pytest.raises(ValueError):
        manager.get_apartment_costs("apart-polanka", 2025, 13)


def test_create_apartment_settlement():
    parameters = Parameters()
    manager = Manager(parameters)

    settlement = manager.create_apartment_settlement("apart-polanka", 2025, 1)

    assert settlement is not None
    assert isinstance(settlement, ApartmentSettlement)
    assert settlement.apartment == "apart-polanka"
    assert settlement.year == 2025
    assert settlement.month == 1
    assert settlement.total_bills_pln == 910.0
    assert settlement.balance_pln == -910.0

    empty_settlement = manager.create_apartment_settlement("apart-polanka", 2025, 2)

    assert empty_settlement is not None
    assert empty_settlement.apartment == "apart-polanka"
    assert empty_settlement.year == 2025
    assert empty_settlement.month == 2
    assert empty_settlement.total_bills_pln == 0.0
    assert empty_settlement.balance_pln == 0.0

    assert manager.create_apartment_settlement("brak-mieszkania", 2025, 1) is None
    with pytest.raises(ValueError):
        manager.create_apartment_settlement("apart-polanka", 2025, 13)


def test_create_tenant_settlements():
    parameters = Parameters()
    manager = Manager(parameters)
    settlement = manager.create_apartment_settlement("apart-polanka", 2025, 1)

    tenant_settlements = manager.create_tenant_settlements(settlement)
    assert len(tenant_settlements) == 3
    assert isinstance(tenant_settlements[0], TenantSettlement)
    assert tenant_settlements[0].tenant == "tenant-1"
    assert tenant_settlements[0].month == 1
    assert tenant_settlements[0].year == 2025
    assert tenant_settlements[0].bills_pln == pytest.approx(910.0 / 3)
    assert tenant_settlements[0].balance_pln == pytest.approx(-910.0 / 3)
    assert tenant_settlements[1].bills_pln == pytest.approx(910.0 / 3)
    assert tenant_settlements[2].bills_pln == pytest.approx(910.0 / 3)

    del manager.tenants["tenant-3"]
    two_tenants_settlements = manager.create_tenant_settlements(settlement)
    assert len(two_tenants_settlements) == 2
    assert two_tenants_settlements[0].bills_pln == 455.0
    assert two_tenants_settlements[1].bills_pln == 455.0
    assert two_tenants_settlements[0].balance_pln == -455.0

    del manager.tenants["tenant-2"]
    one_tenant_settlements = manager.create_tenant_settlements(settlement)
    assert len(one_tenant_settlements) == 1
    assert one_tenant_settlements[0].tenant == "tenant-1"
    assert one_tenant_settlements[0].bills_pln == 910.0
    assert one_tenant_settlements[0].balance_pln == -910.0

    del manager.tenants["tenant-1"]
    no_tenants_settlements = manager.create_tenant_settlements(settlement)
    assert len(no_tenants_settlements) == 0
    assert no_tenants_settlements == []