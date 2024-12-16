import json
import time
import httpx
import asyncio
from requests import Session
from fastapi import status
from zeep.exceptions import Fault
from zeep import Client, AsyncClient
from zeep.helpers import serialize_object
from zeep.wsse.username import UsernameToken
from sqlalchemy.ext.asyncio import AsyncSession
from zeep.transports import Transport, AsyncTransport

from src.logger import logger
from src.config import settings
from src.routers.elt import schemas, services
from src.schemas import schemas as global_schemas
from src.exceptions import exceptions as global_exceptions


class EltService:
    """
        ELT Сервис
    """
    _cache = {}
    _client = None
    _client_reso_guarantee = None
    available_companies = [
        'ВСК',
        'Согласие',
        'ИНГОССТРАХ',
        'Росгосстрах',
        'Согаз Москва',
        'АльфаСтрахование',
        'Энергогарант Москва',
        'РЕСО-Гарантия Москва',
        'Сбербанк страхование Москва',
        'Группа Ренессанс Страхование',
    ]

    def __init__(self, username: str, password: str):
        """
            Инициализация
        """
        self.username = username
        self.password = password

    @classmethod
    async def close(cls):
        """
            Закрытие клиента и сессии
        """
        if cls._client:
            cls._client = None  # Очищаем клиент

    @classmethod
    def request_reso_guarantee(cls, client_, cache_id: str, method: str, params=None):
        """
            Запрос
        """
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
        return data

    def get_client_reso_guarantee(self):
        """
            Получение клиента SOAP
        """

        if EltService._client_reso_guarantee is None:
            EltService._session_reso_guarantee = Session()
            EltService._session_reso_guarantee.headers.update({'Content-Type': 'application/json; charset=utf-8'})
            transport = Transport(session=EltService._session_reso_guarantee)
            EltService._client_reso_guarantee = Client(
                settings.RESO_GUARANTEE,
                transport=transport,
                wsse=UsernameToken(self.username, self.password),
            )
        return EltService._client_reso_guarantee

    @classmethod
    def close_reso_guarantee(cls):
        """
            Закрытие клиента и сессии
        """
        if cls._client_reso_guarantee:
            cls._client_reso_guarantee = None  # Очищаем клиент

    @classmethod
    async def request(cls, client_, cache_id: str, method: str, params=None):
        """
            Запрос
        """
        if method is None:
            return None

        # Выполнение запроса
        try:
            if params:
                data = await getattr(client_.service, method)(**params)
            else:
                data = await getattr(client_.service, method)()
        except Fault as e:
            print(f"SOAP Fault: {e}")
            return None
        return data

    async def get_client(self):
        """
            Получение клиента SOAP
        """
        if EltService._client is None:
            async_client = httpx.AsyncClient(
                auth=(self.username, self.password),
                verify=True,
                timeout=240,
            )
            transport = AsyncTransport(client=async_client)
            EltService._client = AsyncClient(settings.ELT_URL, transport=transport)
        return EltService._client

    @classmethod
    async def get_available_companies(cls, client_, login) -> list[str]:
        """
            Получение Доступных компаний
        """
        companies = serialize_object(await cls.get_list_sk(client_, login))
        companies_ids = []

        for company in companies:
            companies_ids.append(company.get('Id'))
        return companies_ids

    @classmethod
    async def get_list_sk(cls, client_, login: str):
        """
            Получение списка СК
        """
        cache_id = 'get_list_sk'
        return await cls.request(client_, cache_id, 'GetInsuranceCompanies', params={'Login': login})

    @classmethod
    async def get_kladr_by_name_regions(cls, name: str, client_):
        """
            Получения идентификатора, КЛАДРа с полным наименованием регионов
        """
        cache_id = 'get_kladr_full_regions'
        data = await cls.request(client_, cache_id,'GetRegionsExt')

        # Функция для фильтрации
        def filter_by_name(item):
            return name in item['Name']

        # Используем filter для получения отфильтрованных данных
        filtered_data = serialize_object(list(filter(filter_by_name, data)))
        if filtered_data:
            return filtered_data[0].get('Kladr')

    @staticmethod
    async def check_valid_more_three_companies(data: list[dict]):
        """
            Проверка на валидность более трех компаний
        """
        success_elt_companies = []
        for el in data:
            insurance_name = list(el.keys())[0]
            item = el.get(insurance_name)
            if item.get('data').get('Error') is None:
                success_elt_companies.append(insurance_name)

        if len(success_elt_companies) < 3:
            if data[3].get('RESO_GARANTIJA') and data[3].get('RESO_GARANTIJA').get('data'):
                data[3]['RESO_GARANTIJA']['data']['Error'] = ('Отправка котировок в Ресо-Гарантия возможно, '
                                                              'когда посчитаны 3 и более страховых компаний!')
            raise global_exceptions.MyHTTPException(
                status=global_schemas.StatusResponseEnum.ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
                message=json.dumps(data),
            )

    @staticmethod
    async def save_to_database(calc_id: int, calc_reso_id: int, rl_actions_data: dict, data: list, session):
        """
            Сохранение в Базу Данных
        """
        try:
            # Проверка есть ли в базе
            exist_insurance = await services.check_exist_insurance(calc_reso_id, session)
            print('exist_insurance: ', exist_insurance)
            if exist_insurance:
                await services.delete_insurance_by_calc_reso_id(calc_reso_id, session)
            await services.create_insurance_elt(calc_id, calc_reso_id, rl_actions_data, data, session)
        except Exception as exc:
            logger.error(exc)
            raise global_exceptions.MyHTTPException(
                status=global_schemas.StatusResponseEnum.ERROR,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Произошла ошибка при сохранении результата ELT в Базу Данных',
            )

    async def get_rl_actions(self,
                             data: schemas.ResoGuaranteeCreate,
                             companies: list[dict], session: AsyncSession):
        """
            Передача номер расчета ЕЛТ и премии конкурентов в Ресо Гарантию
        """
        params = {
            'parameter': {
                'CalcID': data.calc_id,
                'PrevCalcID': data.prev_calc_id,
                'CalculationList': {
                    'Calculation': companies,
                }
            }
        }
        response_rl_actions = self.request_reso_guarantee(
            self._client_reso_guarantee,
            'get_rl_actions',
            'GetRLActions',
            params=params,
        )
        data_rl_actions = serialize_object(response_rl_actions)
        if data_rl_actions.get('Error') == 'OK':
            quote_id = data_rl_actions.get('QuoteID')
            police_id = data_rl_actions.get('PolicyID')

            response_status = self.request_reso_guarantee(
                self._client_reso_guarantee,
                'get_rl_status',
                'GetRLStatus',
                params={'QuoteID': quote_id},
            )
            data_status = serialize_object(response_status)
            # Добавляем в Базу Квот
            await services.update_insurance(
                data.calc_id,
                {'quote_id': quote_id, 'police_id': police_id},
                session,
            )
            if data_status.get('Error') == 'OK':
                if data_status.get('Status') == 'SUCEESS':
                    return {'quote_id': quote_id, 'police_id': police_id}
                else:
                    raise global_exceptions.MyHTTPException(
                        status=global_schemas.StatusResponseEnum.ERROR,
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message=data_status,
                    )
            else:
                raise global_exceptions.MyHTTPException(
                    status=global_schemas.StatusResponseEnum.ERROR,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=data_status.get('Error'),
                )
        else:
            raise global_exceptions.MyHTTPException(
                status=global_schemas.StatusResponseEnum.ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
                message=data_rl_actions,
            )

    async def casco_calculation(self,
                                method: str,
                                cache_id: str,
                                data: schemas.EltCascoCalculation,
                                session: AsyncSession):
        """
            Метод получения расчета
        """
        calc_id = None
        result_requests = []
        calc_reso_id = data.calc_reso_id

        for company in data.active_companies:
            try:
                request = {
                    'AuthInfo': {
                        'Login': settings.ELT_USERNAME,
                        'Password': settings.ELT_PASSWORD.get_secret_value(),
                    },
                    'InsuranceCompany': company,
                    'ContractOptionId': 1,
                    'Params': data.model_dump(exclude={'calc_reso_id', 'active_companies'}),
                }
                result = await self.request(self._client, cache_id, method, request)
                # Преобразование результата в словарь
                result_dict = serialize_object(result)
                if not result_dict:
                    result_requests.append(
                        {
                            company: {
                                'status': global_schemas.StatusResponseEnum.ERROR,
                                'data': {
                                    'message': 'Не правильный запрос',
                                }
                            },
                        }
                    )
                result_requests.append(
                    {
                        company: {
                            'status': global_schemas.StatusResponseEnum.SUCCESS,
                            'data': result_dict,
                        },
                    }
                )
                if company == 'RESO_GARANTIJA':
                    calc_id = result_dict.get('SKCalcId')
            except Exception as e:
                logger.error(str(e))
                result_requests.append(
                    {
                        company: {
                            'status': global_schemas.StatusResponseEnum.ERROR,
                            'data': {
                                'message': 'Не правильный запрос',
                            }
                        },
                    }
                )

        # Проверка на валидность
        await self.check_valid_more_three_companies(result_requests)

        # Отправляем в Ресо Гарантию
        companies = [
            {
                'InsuranceCompany': company_name,
                'PremiumSum': company_info.get('data').get('PremiumSum'),
                'Franchise': int(company_info.get('data').get('TotalFranchise')) if company_info.get('data').get('TotalFranchise') else 0,
            } for company_data in result_requests for company_name, company_info in company_data.items()
        ]

        data_rl_actions = schemas.ResoGuaranteeCreate(
            calc_id=result_requests[3].get('RESO_GARANTIJA').get('data').get('SKCalcId'),
        )
        rl_actions_data = await self.get_rl_actions(data_rl_actions, companies, session)
        result_requests[3].get('RESO_GARANTIJA')['quote_id'] = rl_actions_data.get('quote_id')
        result_requests[3].get('RESO_GARANTIJA')['police_id'] = rl_actions_data.get('police_id')

        # Сохранение в БД
        calc_id = await self.save_to_database(calc_id, calc_reso_id, rl_actions_data, result_requests, session)
        return result_requests, calc_id


class SoapService:
    """
        ELT Сервис
    """
    _cache = {}
    _client = None
    _session = None
    available_companies = [
        'ВСК',
        'Согласие',
        'ИНГОССТРАХ',
        'Росгосстрах',
        'Согаз Москва',
        'АльфаСтрахование',
        'Энергогарант Москва',
        'РЕСО-Гарантия Москва',
        'Сбербанк страхование Москва',
        'Группа Ренессанс Страхование',
    ]

    def __init__(self, username: str, password: str):
        """
            Initializing
        """
        self.username = username
        self.password = password

    @classmethod
    def get_available_companies(cls, client_, login) -> list[str]:
        """
            Get Available Companies
        """
        companies = serialize_object(cls.get_list_sk(client_, login))
        companies_ids = []

        for company in companies:
            companies_ids.append(company.get('Id'))
        return companies_ids

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
    def request(cls, client_, cache_id: str, method: str, params=None, is_cache: bool = False, cache_time: int = 1000):
        current_time = time.time()

        if is_cache:
            # Проверка кэша
            if cache_id in cls._cache and (current_time - cls._cache[cache_id]['timestamp'] < cache_time):
                return cls._cache[cache_id]['data']

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

        if is_cache:
            # Сохранение в кэш
            cls._cache[cache_id] = {'data': data, 'timestamp': current_time}
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
        return cls.request(client_, cache_id,'GetRegionsExt', is_cache=True, cache_time=86400)

    @classmethod
    def get_full_kladr_cities(cls, client_, region_id: str):
        """
            Получения идентификатора, КЛАДРа города/населённого пункта.
        """
        cache_id = f'get_kladr_full_cities_{region_id}'
        return cls.request(
            client_,
            cache_id,
            'GetCitiesExt',
            params={'RegionId': region_id},
            is_cache=True,
            cache_time=86400,
        )

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
    def testing(cls, client_):
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
    def check_valid_more_three_companies(cls, data: list):
        """
            Проверка на валидность более трех компаний
        """
        success_elt_companies = []
        for el in data:
            # test = el[el.keys()[0]]
            insurance_name = list(el.keys())[0]
            data = el.get(insurance_name)
            if data.get('data').get('Error') is None:
                success_elt_companies.append(insurance_name)

        if len(success_elt_companies) < 3:
            raise global_exceptions.MyHTTPException(
                status=global_schemas.StatusResponseEnum.ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
                message='Отправка котировок в Ресо-Гарантия возможно, когда посчитаны 3 и более страховых компаний!',
            )

    @classmethod
    def save_to_database(cls, calc_id: int, data: list, session):
        """
            Сохранение в Базу Данных
        """
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(services.create_insurance_elt(calc_id, data, session))
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
        finally:
            loop.close()

    @classmethod
    def casco_calculation(cls,
                          client_,
                          method: str,
                          cache_id: str,
                          companies: list[str],
                          data: schemas.EltCascoCalculation,
                          session: AsyncSession) -> tuple:
        """
            Метод получения расчета
        """
        calc_id = None
        result_requests = []

        for company in companies:
            try:
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
                    result_requests.append(
                        {
                            company: {
                                'status': global_schemas.StatusResponseEnum.ERROR,
                                'data': {
                                    'message': 'Не правильный запрос',
                                }
                            },
                        }
                    )
                result_requests.append(
                    {
                        company: {
                            'status': global_schemas.StatusResponseEnum.SUCCESS,
                            'data': result_dict,
                        },
                    }
                )
                if company == 'RESO_GARANTIJA':
                    calc_id = result_dict.get('SKCalcId')
            except Exception as e:
                logger.error(str(e))
                result_requests.append(
                    {
                        company: {
                            'status': global_schemas.StatusResponseEnum.ERROR,
                            'data': {
                                'message': 'Не правильный запрос',
                            }
                        },
                    }
                )

        # Проверка на валидность
        cls.check_valid_more_three_companies(result_requests)

        # Сохранение в БД
        cls.save_to_database(calc_id, result_requests, session)

        return result_requests, calc_id


class ResoGuarantee:
    """
        Ресо Гарантия
    """
    _client = None
    _session = None

    def __init__(self, username: str, password: str):
        """
            Инициализация
        """
        self.username = username
        self.password = password

    @classmethod
    def request(cls, client_, cache_id: str, method: str, params=None):
        """
            Запрос
        """
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
        return data

    def get_client(self):
        """
            Получение клиента SOAP
        """

        if ResoGuarantee._client is None:
            ResoGuarantee._session = Session()
            ResoGuarantee._session.headers.update({'Content-Type': 'application/json; charset=utf-8'})
            transport = Transport(session=ResoGuarantee._session)
            ResoGuarantee._client = Client(
                settings.RESO_GUARANTEE,
                transport=transport,
                wsse=UsernameToken(self.username, self.password),
            )
        return ResoGuarantee._client

    @classmethod
    def close(cls):
        """
            Закрытие клиента и сессии
        """
        if cls._client:
            cls._client = None  # Очищаем клиент
        if cls._session:
            cls._session = None

    def get_rl_status(self, quote_id: int):
        """
            Получение премии по Квоте
        """
        response_status = self.request(
            self._client,
            'get_rl_status',
            'GetRLStatus',
            params={'QuoteID': quote_id},
        )
        data_status = serialize_object(response_status)
        if data_status.get('Error') == 'OK':
            if data_status.get('Status') == 'SUCEESS':
                raise global_exceptions.MyHTTPException(
                    status=global_schemas.StatusResponseEnum.SUCCESS,
                    status_code=status.HTTP_200_OK,
                    message=data_status,
                )
            else:
                raise global_exceptions.MyHTTPException(
                    status=global_schemas.StatusResponseEnum.ERROR,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=data_status,
                )
        else:
            raise global_exceptions.MyHTTPException(
                status=global_schemas.StatusResponseEnum.ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
                message=data_status.get('Error'),
            )

    async def get_rl_actions(self,
                             data: schemas.ResoGuaranteeCreate,
                             companies: list[dict], session: AsyncSession):
        """
            Передача номер расчета ЕЛТ и премии конкурентов в Ресо Гарантию
        """
        params = {
            'parameter': {
                'CalcID': data.calc_id,
                'PrevCalcID': data.prev_calc_id,
                'CalculationList': {
                    'Calculation': companies,
                }
            }
        }

        response_rl_actions = self.request(
            self._client,
            'get_rl_actions',
            'GetRLActions',
            params=params,
        )
        data_rl_actions = serialize_object(response_rl_actions)

        if data_rl_actions.get('Error') == 'OK':
            quote_id = data_rl_actions.get('QuoteID')
            police_id = data_rl_actions.get('PolicyID')

            response_status = self.request(
                self._client,
                'get_rl_status',
                'GetRLStatus',
                params={'QuoteID': quote_id},
            )
            data_status = serialize_object(response_status)
            # Добавляем в Базу Квот
            await services.update_insurance(
                data.calc_id,
                {'quote_id': quote_id, 'police_id': police_id},
                session,
            )

            if data_status.get('Error') == 'OK':
                if data_status.get('Status') == 'SUCEESS':
                    return schemas.QuoteResponse(quote_id=quote_id)
                else:
                    raise global_exceptions.MyHTTPException(
                        status=global_schemas.StatusResponseEnum.ERROR,
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message=data_status,
                    )
            else:
                raise global_exceptions.MyHTTPException(
                    status=global_schemas.StatusResponseEnum.ERROR,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=data_status.get('Error'),
                )
        else:
            raise global_exceptions.MyHTTPException(
                status=global_schemas.StatusResponseEnum.ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
                message=data_rl_actions,
            )


class ResoGuaranteeAsync:
    """
        Ресо Гарантия
    """
    _client = None
    _session = None

    def __init__(self, username: str, password: str):
        """
            Инициализация
        """
        self.username = username
        self.password = password

    @classmethod
    async def request(cls, client_, cache_id: str, method: str, params=None):
        """
            Запрос
        """
        if method is None:
            return None

        # Выполнение запроса
        try:
            if params:
                data = await getattr(client_.service, method)(**params)
            else:
                data = await getattr(client_.service, method)()
        except Fault as e:
            print(f"SOAP Fault: {e}")
            return None
        return data

    async def get_client(self):
        """
            Получение клиента SOAP
        """

        if ResoGuaranteeAsync._client is None:
            async_client = httpx.AsyncClient(
                auth=(self.username, self.password),
                verify=True,
                timeout=240,
            )
            transport = AsyncTransport(client=async_client)
            ResoGuaranteeAsync._client = AsyncClient(settings.RESO_GUARANTEE, transport=transport)
        return ResoGuaranteeAsync._client

    @classmethod
    async def close(cls):
        """
            Закрытие клиента и сессии
        """
        if cls._client:
            cls._client = None  # Очищаем клиент
        if cls._session:
            cls._session = None

    async def get_rl_status(self):
        pass

    async def get_rl_actions(self, calc_id: int):
        params = {
            'parameter': {
                'CalcID': calc_id,
                'CalculationList': {
                    'Calculation': [
                        {
                            'InsuranceCompany': 'SOGAZ_77',
                            'PremiumSum': 151074,
                            'Franchise': 15000,
                        },
                        {
                            'InsuranceCompany': 'Rensins',
                            'PremiumSum': 126190,
                            'Franchise': 15000,
                        },
                        {
                            'InsuranceCompany': 'VSK',
                            'PremiumSum': 143567,
                            'Franchise': 15000,
                        },
                        {
                            'InsuranceCompany': 'RESO_GARANTIJA',
                            'PremiumSum': 263101,
                            'Franchise': 15000,
                        },
                    ]
                }
            }
        }

        response_rl_actions = await self.request(
            self._client,
            'get_rl_actions',
            'GetRLActions',
            params=params,
        )
        data_rl_actions = serialize_object(response_rl_actions)

        if data_rl_actions.get('Error') == 'OK':
            response_status = await self.request(
                self._client,
                'get_rl_status',
                'GetRLStatus',
                params={'QuoteID': data_rl_actions.get('QuoteID')},
            )
            data_status = serialize_object(response_status)
            if data_status.get('Error') == 'OK':
                if data_status.get('Status') == 'SUCEESS':
                    print('SUCCESS')
                else:
                    raise global_exceptions.MyHTTPException(
                        status=global_schemas.StatusResponseEnum.ERROR,
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message=data_status.get('Error'),
                    )
            else:
                raise global_exceptions.MyHTTPException(
                    status=global_schemas.StatusResponseEnum.ERROR,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=data_status.get('Error'),
                )
        else:
            raise global_exceptions.MyHTTPException(
                status=global_schemas.StatusResponseEnum.ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
                message=data_rl_actions,
            )
