from zeep import Client
from fastapi import status
from requests import Session
from zeep.exceptions import Fault
from zeep.transports import Transport
from zeep.helpers import serialize_object
from zeep.wsse.username import UsernameToken

from src.config import settings
from src.routers.elt import schemas
from src.schemas import schemas as global_schemas
from src.exceptions import exceptions as global_exceptions


class SoapService:
    _cache = {}
    _client = None
    _session = None

    def __init__(self, username: str, password: str):
        """
            Initializing
        """
        self.username = username
        self.password = password

    @staticmethod
    def get_client(username: str, password: str):
        """
            Получение клиента SOAP
        """
        if SoapService._client is None:
            SoapService._session = Session()
            transport = Transport(session=SoapService._session)
            SoapService._client = Client(settings.ELT_URL, transport=transport, wsse=UsernameToken(username, password))
        return SoapService._client

    @classmethod
    def close(cls):
        """
        Закрытие клиента и сессии
        """
        if cls._client:
            cls._client = None  # Очищаем клиент
        if cls._session:
            cls._session.close()  # Закрываем сессию
            cls._session = None

    @classmethod
    def request(cls, client_, cache_id: str, method: str, params=None):
        # cache_time = 1000  # Время кэширования в секундах
        # current_time = time.time()
        #
        # # Проверка кэша
        # if cache_id in cls._cache and (current_time - cls._cache[cache_id]['timestamp'] < cache_time):
        #     return cls._cache[cache_id]['data']

        if method is None:
            return None

        # Выполнение запроса
        try:
            if params:
                data = getattr(client_.service, method)(**params)
            else:
                data = getattr(client_.service, method)()
        except Fault as e:
            print(f"SOAP Fault: {e}")
            return None

        # Сохранение в кэш
        # cls._cache[cache_id] = {'data': data, 'timestamp': current_time}
        return data

    @classmethod
    def get_insurance_brand_values(cls, client_):
        """
            Получение Брендов Авто
        """
        cache_id = 'insurance_brand_values'
        return cls.request(client_, cache_id, 'GetAutoMarks')

    @classmethod
    def get_insurance_model_values(cls, client_, mark: str):
        """
            Получение Моделей Авто
        """
        cache_id = 'insurance_model_values'
        return cls.request(client_, cache_id, 'GetAutoModels', params={'Mark': mark})

    @classmethod
    def get_insurance_companies(cls, client_):
        """
            Получение Страховых компаний
        """
        cache_id = "insuranceCompanies"
        return cls.request(client_, cache_id, "GetInsuranceCompanies")

    @classmethod
    def get_modification_ts(cls, client_, mark: str, model: str):
        """
            Получение модификаций ТС
        """
        cache_id = "modification_ts"
        return cls.request(client_, cache_id, 'GetAutoModifications', params={'Mark': mark, 'Model': model})

    @classmethod
    def get_banks(cls, client_):
        """
            Получение Банков
        """
        cache_id = 'get_banks'
        return cls.request(client_, cache_id, "GetBanks")

    @classmethod
    def get_stoa(cls, client_):
        """
            Получение Типа страхового возмещения
        """
        cache_id = 'get_stoa'
        return cls.request(client_, cache_id, "GetSTOA")

    @classmethod
    def get_go_limit(cls, client_, company_id: str):
        """
            Получения страховых сумм СК по риску Расширению ГО
        """
        cache_id = 'get_go_limit'
        return cls.request(client_, cache_id, "GetGOLimit", params={'InsuranceCompany': company_id})

    @classmethod
    def get_do(cls, client_):
        """
            Получения списка типов ДО
        """
        cache_id = 'get_do'
        return cls.request(client_, cache_id, "GetDOTypes")

    @classmethod
    def get_opf(cls, client_):
        """
            Получения справочника ОПФ
        """
        cache_id = 'get_opf'
        return cls.request(client_, cache_id, "GetOPF")

    @classmethod
    def get_list_sk(cls, client_, login: str):
        """
            Получение списка СК
        """
        cache_id = 'get_list_sk'
        return cls.request(client_, cache_id, 'GetInsuranceCompanies', params={'Login': login})

    @classmethod
    def get_options_characteristic(cls, client_, company_id: str):
        """
            Получения списка опций, характерных для конкретной СК
        """
        cache_id = 'get_options_characteristic'
        return cls.request(
            client_,
            cache_id,
            'GetInsuranceCompanySpecificOptions',
            params={'InsuranceCompany': company_id},
        )

    @classmethod
    def get_list_products_sk(cls, client_, company_id: str):
        """
            Получения списка продуктов СК
        """
        cache_id = 'get_list_products_sk'
        return cls.request(client_, cache_id, 'GetProducts', params={'InsuranceCompany': company_id})

    @classmethod
    def get_list_programs_sk(cls, client_, company_id: str, product: str = None):
        """
            Получения списка программ СК
        """
        cache_id = 'get_list_programs_sk'
        return cls.request(
            client_,
            cache_id,
            'GetPrograms',
            params={'InsuranceCompany': company_id, 'Product': product},
        )

    @classmethod
    def get_list_puu_marks(cls, client_):
        """
            Получения списка марок ПУУ
        """
        cache_id = 'get_puu_marks'
        return cls.request(
            client_,
            cache_id,
            'GetPUUMarks',
        )

    @classmethod
    def get_list_models_puu_by_mark(cls, client_, mark_id: str):
        """
            Получения списка моделей ПУУ по марке
        """
        cache_id = 'get_list_models_puu_by_mark'
        return cls.request(
            client_,
            cache_id,
            'GetPUUModels',
            params={'Mark': mark_id},
        )

    @classmethod
    def get_ref_info(cls, client_):
        """
            Получения справочной информации
        """
        cache_id = 'get_ref_info'
        return cls.request(
            client_,
            cache_id,
            'GetOptions',
        )

    @classmethod
    def get_full_kladr_regions(cls, client_):
        """
            Получения идентификатора, КЛАДРа с полным наименованием регионов
        """
        cache_id = 'get_kladr_full_regions'
        return cls.request(client_, cache_id,'GetRegionsExt')

    @classmethod
    def get_full_kladr_cities(cls, client_):
        """
            Получения идентификатора, КЛАДРа города/населённого пункта.
        """
        cache_id = 'get_kladr_full_cities'
        return cls.request(client_, cache_id, 'GetCitiesExt')

    @classmethod
    def get_full_kladr_countries(cls, client_):
        """
            Получения списка стран
        """
        cache_id = 'get_kladr_full_countries'
        return cls.request(client_, cache_id, 'GetCountries')

    @classmethod
    def get_puu_marks(cls, client_, type_=None):
        cache_id = "insurance_puu_values"
        puu = cls.request(client_, cache_id, "GetPUUMarks")

        if type_ == 1 and puu:
            return {mark.Id: mark.Name for mark in puu}
        return puu

    @classmethod
    def get_puu_models(cls, client_, id, name=''):
        params = {'id': id}
        if name:
            params['Name'] = name
        return client_.service.GetPUUModels(params)

    @classmethod
    def get_available_print_forms(cls, client_, order_id: str):
        """
            Получения печатных форм доступных для страхового продукта
        """
        params = {
            'AuthInfo': {
                'Login': 'divanov',
                'Password': '123456',
            },
            'OrderId': order_id,
        }
        return client_.service.GetAvailablePrintForms(params)

    @classmethod
    def get_print_form(cls, client_, order_id):
        params = {
            'AuthInfo': {
                'Login': 'divanov',
                'Password': '123456',
                'SessionId': ''
            },
            'OrderId': order_id,
            'FormId': 'policy'
        }
        return client_.service.GetPrintForm(params)

    @classmethod
    def get_print_kp(cls, client_, arr, calc_id):
        params = {
            'AuthInfo': {
                'Login': 'divanov',
                'Password': '123456',
                'SessionId': ''
            },
            'CalcList': arr,
            'CalcId': calc_id
        }
        return client_.service.GetPrintKP(params)

    @classmethod
    def get_types(cls, client_, key: str):
        """
            Получение Типа коробки передач
        """
        options = client_.service.GetOptions()
        filtered_type = next((item for item in options if item['Id'] == key), None)
        if filtered_type:
            option_values = filtered_type['Values']['OptionValue']
            return option_values
        else:
            return None

    @classmethod
    def get_regions(cls, client_) -> list[dict[str, str]]:
        """
            Получение регионов
        """
        return client_.service.GetRegionsExt()

    @classmethod
    def casco_calculation(cls,
                          client_,
                          method: str,
                          company: str,
                          cache_id: str,
                          data: schemas.EltCascoCalculation):
        """
            Метод получения расчета
        """

        request = {
            'AuthInfo': {
                'Login': settings.ELT_USERNAME,
                'Password': settings.ELT_PASSWORD.get_secret_value(),
            },
            'InsuranceCompany': company,
            'ContractOptionId': 1,
            'Params': data.model_dump(),
        }
        result = cls.request(client_, cache_id, method, request)

        # Преобразование результата в словарь
        result_dict = serialize_object(result)
        if not result_dict:
            raise global_exceptions.MyHTTPException(
                status=global_schemas.StatusResponseEnum.ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
                message='Не правильный запрос',
            )

        # Проверка на ошибку
        error = result_dict.get('Error')
        if error:
            raise global_exceptions.MyHTTPException(
                status=global_schemas.StatusResponseEnum.ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
                message=error,
            )
        return schemas.ResponseSuccessCascoCalculation(
            status=schemas.StatusResponseEnum.SUCCESS,
            data=result_dict,
        )
