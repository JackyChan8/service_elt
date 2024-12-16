from typing import List, Optional, Any

from pydantic import BaseModel

from src.schemas.schemas import StatusResponseEnum


# ================================================================================================================== #
# ========================================================= Utils ================================================== #
# ================================================================================================================== #
class UtilsOption(BaseModel):
    Id: Optional[str] = None
    Name: str


# ================================================================================================================== #
# ========================================================= Request ================================================ #
# ================================================================================================================== #
class ModificationModel(BaseModel):
    # Name: str
    Power: int  # Мощность двигателя, л.с (неотрицательное целое число)
    EngineType: int  # Тип двигателя
    KPPTypeId: int  # Тип коробки передач
    BodyType: int  # Тип кузова
    Seats: Optional[str] = ''  # Количество мест
    Country: int  # Страна


class SpecialMachineryModel(BaseModel):
    SpecialMachineryMark: Optional[str] = ''
    SpecialMachineryModel: Optional[str] = ''
    Type: Optional[str] = ''
    Industry: Optional[str] = ''
    Mover: Optional[str] = ''


class VehicleModel(BaseModel):
    VIN: Optional[str] = ''
    Category: str  # Категория ТС
    MaxAllowedMass: int  # Максимально разрешенная масса
    VehicleUsage: int  # Использование ТС
    Mileage: int  # Пробег (км)
    SeatingCapacity: int
    # Classification: int  # Классификация


class DriverElement(BaseModel):
    Age: int  # Возраст водителя
    Experience: int  # Стаж водителя


class DriverModel(BaseModel):
    Driver: List[DriverElement] = []


class InsurerModel(BaseModel):
    SubjectType: int  # Тип страхователя
    INN: int  # ИНН страхователя


class LesseeModel(BaseModel):
    SubjectType: int  # Тип лизингополучателя
    INN: int  # ИНН лизингополучателя


class EltCascoCalculation(BaseModel):
    IsNew: str  # 0 или 1
    UsageStart: Optional[str] = ''  # Дата начала использования ТС
    UsageCityKLADR: str  # Регион регистрации
    VehicleYear: str
    Mark: str  # Марка
    Model: str  # Модель
    Modification: ModificationModel
    SpecialMachinery: SpecialMachineryModel
    Duration: int  # Срок страхования
    BankId: int  # Идентификатор банка
    Cost: int  # Цена ТС
    Franchise: Optional[str] = ''  # Франшиза, процент от Цены ТС или абсолютная величина (зависит от настроек системы)
    SSType: int  # 0 или 1
    STOA: int = 0  # Тип страхового возмещения
    Region: str | int  # Регион регистрации
    # Autostart: Optional[str] = ''
    # AtsSound: Optional[str] = ''
    # StandartImmobilizer: int
    # CentralLocking: int
    # MarkingGlasses: Optional[str] = ''  # 0 или 1
    # SelfIgnition: Optional[str] = ''  # 0 или 1
    # OutsideRoads: Optional[str] = ''  # 0 или 1
    NotConfirmedDamages: int
    NotConfirmedGlassesDamages: int
    PUUs: Optional[List[str]] = []  # Список PUU
    DriversCount: int
    ApprovedDriving: int
    Risk: int  # Риски
    PayType: int
    Vehicle: VehicleModel
    Drivers: List[DriverModel] = []
    GO: List[dict] = []
    NS: List[str] = []
    GAP: int  # 0 или 1
    Insurer: List[InsurerModel]
    Lessee: List[LesseeModel]
    # Калькулятор ID
    calc_reso_id: int
    active_companies: list[str]


class Car(BaseModel):
    Id: str
    Name: str
    Country: Optional[str] = None
    Power: int
    EngineType: str
    EngineVolume: int
    KPPTypeId: int
    BodyType: int
    DoorsCount: int
    Seats: Optional[int] = None


class Bank(BaseModel):
    Id: str
    Name: Optional[str] = None


class Do(BaseModel):
    Id: str
    Name: str
    Price: Optional[float] = None


class Opf(UtilsOption):
    pass


class InsuranceCompanies(BaseModel):
    Id: str
    Name: str
    LegalName: str
    INN: Optional[str] = None
    KPP: Optional[str] = None
    Logo: str


class Values(BaseModel):
    OptionValue: list[UtilsOption]


class InsuranceCompanyOption(BaseModel):
    Id: str
    Name: str
    InputType: str
    Values: Optional[Values]


class GetInsuranceCompanySpecificOptionsResult(BaseModel):
    InsuranceCompanyOption: List[InsuranceCompanyOption]


class Product(UtilsOption):
    pass


class Program(UtilsOption):
    pass


class PuuMark(UtilsOption):
    pass


class Country(UtilsOption):
    pass


class Stoa(UtilsOption):
    pass


class GoLimit(BaseModel):
    Id: int
    Sum: str


class Type(BaseModel):
    Type: list[str]


class PuuModel(UtilsOption):
    Types: Type


class RefInfo(UtilsOption):
    Values: Optional[Values]


class ResoGuaranteeCalc(BaseModel):
    InsuranceCompany: str
    PremiumSum: int
    Franchise: int


class ResoGuaranteeCreate(BaseModel):
    calc_id: int
    prev_calc_id: Optional[int] = False


class Franchise(UtilsOption):
    pass


class SSType(UtilsOption):
    pass
# ================================================================================================================== #
# ========================================================= Response =============================================== #
# ================================================================================================================== #

class ResponseErrorCascoCalculation(BaseModel):
    status: StatusResponseEnum = StatusResponseEnum.SUCCESS
    error_info: str


class ResponseSuccessCascoCalculation(BaseModel):
    status: StatusResponseEnum = StatusResponseEnum.SUCCESS
    data: Any


class InsuranceCompaniesResponse(BaseModel):
    companies: list[InsuranceCompanies]


class InsuranceCompanyOptionsResponse(BaseModel):
    GetInsuranceCompanySpecificOptionsResult: GetInsuranceCompanySpecificOptionsResult
    Error: Optional[str]


class ListProductsResponse(BaseModel):
    products: list[Product]


class ListProgramsResponse(BaseModel):
    programs: list[Program]


class ListPuuMarksResponse(BaseModel):
    puu_marks: list[PuuMark]


class ListPuuModelsResponse(BaseModel):
    puu_models: list[PuuModel]


class RefInfoResponse(BaseModel):
    ref_info: list[RefInfo]


class KladrRegion(UtilsOption):
    Kladr: str


class KladrCity(UtilsOption):
    Kladr: str


class KladrRegionResponse(BaseModel):
    regions: list[KladrRegion]


class KladrCitiesResponse(BaseModel):
    cities: list[KladrCity]


class CountriesResponse(BaseModel):
    countries: list[Country]


class StoaResponse(BaseModel):
    stoa: list[Stoa]


class GoLimitResponse(BaseModel):
    go_limit: list[GoLimit]


class ModificationResponse(BaseModel):
    cars: list[Car]


class BankResponse(BaseModel):
    banks: list[Bank]


class DoResponse(BaseModel):
    do: list[Do]


class OpfResponse(BaseModel):
    opf: list[Opf]


class FranchiseResponse(BaseModel):
    franchises: list[Franchise]


class SSTypeResponse(BaseModel):
    ss_types: list[SSType]


class QuoteResponse(BaseModel):
    quote_id: int
