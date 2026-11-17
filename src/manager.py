from src.models import Apartment, ApartmentSettlement, Bill, Parameters, Tenant, TenantSettlement, Transfer


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True
    
    def get_apartment_costs(self, apartment_key: str, year: int = None, month: int = None):
        if apartment_key not in self.apartments:
            return None

        if month is not None and (month < 1 or month > 12):
            raise ValueError("Miesiąc musi być z przedziału 1-12")

        total = 0.0
        for bill in self.bills:
            if bill.apartment == apartment_key:
                if year is not None and bill.settlement_year != year:
                    continue
                if month is not None and bill.settlement_month != month:
                    continue
                total += bill.amount_pln

        return total

    def create_apartment_settlement(self, apartment_key: str, year: int, month: int):
        if apartment_key not in self.apartments:
            return None

        if month < 1 or month > 12:
            raise ValueError("Miesiąc musi być z przedziału 1-12")

        total_bills = self.get_apartment_costs(apartment_key, year, month)
        total_transfers = 0.0
        balance = total_transfers - total_bills

        settlement = ApartmentSettlement(
            apartment=apartment_key,
            month=month,
            year=year,
            total_rent_pln=0.0,
            total_bills_pln=total_bills,
            total_due_pln=total_bills,
            balance_pln=balance
        )
        return settlement

    def create_tenant_settlements(self, apartment_settlement: ApartmentSettlement):
        if apartment_settlement is None:
            return []

        apartment_tenants = []
        for tenant_key, tenant in self.tenants.items():
            if tenant.apartment == apartment_settlement.apartment:
                apartment_tenants.append(tenant_key)

        if len(apartment_tenants) == 0:
            return []

        bills_share = apartment_settlement.total_bills_pln / len(apartment_tenants)
        settlement_id = f"{apartment_settlement.apartment}-{apartment_settlement.year}-{apartment_settlement.month}"

        settlements = []
        for tenant_key in apartment_tenants:
            tenant_settlement = TenantSettlement(
                tenant=tenant_key,
                apartment_settlement=settlement_id,
                month=apartment_settlement.month,
                year=apartment_settlement.year,
                rent_pln=0.0,
                bills_pln=bills_share,
                total_due_pln=bills_share,
                balance_pln=-bills_share
            )
            settlements.append(tenant_settlement)

        return settlements