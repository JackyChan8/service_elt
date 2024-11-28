from fastapi import APIRouter, status
from zeep.helpers import serialize_object

from src.config import settings
from src.routers.elt import schemas, utils
from src.schemas import schemas as global_schemas
from src.exceptions import exceptions as global_exceptions

router = APIRouter(prefix='/elt', tags=['elt'])

@router.get(path='/casco-get-marks',
            status_code=status.HTTP_200_OK,
            response_model=list[str],
            description='Метод получения списка марок ТС')
def casco_get_marks():
    """
        Get marks service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        return soap.get_insurance_brand_values(client)
    finally:
        soap.close()


@router.get(path='/casco-get-mark',
            status_code=status.HTTP_200_OK,
            response_model=list[str],
            description='Метод получения списка моделей ТС по марке')
def casco_get_mark(mark_name: str):
    """
        Get mark service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        return soap.get_insurance_model_values(client, mark_name)
    finally:
        soap.close()


@router.get(path='/casco-get-modification-ts',
            status_code=status.HTTP_200_OK,
            response_model=schemas.ModificationResponse,
            description='Метод получения списка модификаций ТС по марке и модели')
def casco_get_modification_ts(mark_name: str, model_name: str):
    """
        Get modification service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_modification_ts(client, mark_name, model_name)
        car_models = [schemas.Car(**serialize_object(car)) for car in result]
        return schemas.ModificationResponse(cars=car_models)
    finally:
        soap.close()


@router.get('/casco-get-banks',
            status_code=status.HTTP_200_OK,
            response_model=schemas.BankResponse,
            description='Метод получения списка Банков')
def casco_get_banks():
    """
        Get banks service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_banks(client)
        bank_models = [schemas.Bank(**serialize_object(bank)) for bank in result]
        return schemas.BankResponse(banks=bank_models)
    finally:
        soap.close()


@router.get(path='/casco-get-do',
            status_code=status.HTTP_200_OK,
            response_model=schemas.DoResponse,
            description='Метод получения типов ДО')
def casco_get_do():
    """
        Get DO service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_do(client)
        do_models = [schemas.Do(**serialize_object(do)) for do in result]
        return schemas.DoResponse(do=do_models)
    finally:
        soap.close()


@router.get(path='/casco-get-opf',
            status_code=status.HTTP_200_OK,
            response_model=schemas.OpfResponse,
            description='Метод получения справочника ОПФ')
def casco_get_opf():
    """
        Get Opf Service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_opf(client)
        opf_models = [schemas.Opf(**serialize_object(opf)) for opf in result]
        return schemas.OpfResponse(opf=opf_models)
    finally:
        soap.close()


@router.get(path='/casco-get-list-sk',
            status_code=status.HTTP_200_OK,
            response_model=schemas.InsuranceCompaniesResponse,
            description='Метод получения списка СК')
def casco_get_list_sk():
    """
        Get List SK Service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_list_sk(client, elt_username)
        company_models = [schemas.InsuranceCompanies(**serialize_object(company)) for company in result]
        return schemas.InsuranceCompaniesResponse(companies=company_models)
    finally:
        soap.close()


@router.get(path='/casco-get-options-characteristic',
            status_code=status.HTTP_200_OK,
            response_model=schemas.InsuranceCompanyOptionsResponse,
            description='Метод получения списка опций, характерных для конкретной СК')
def casco_get_options_characteristic(company_id: str):
    """
        Get Options Characteristics
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_options_characteristic(client, company_id)
        return schemas.InsuranceCompanyOptionsResponse(**serialize_object(result))
    finally:
        soap.close()


@router.get(path='/casco-get-products-sk',
            status_code=status.HTTP_200_OK,
            response_model=schemas.ListProductsResponse,
            description='Метод получения списка продуктов СК')
def casco_get_products_sk(company_id: str):
    """
        Get Products SK Service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_list_products_sk(client, company_id)
        product_models = [schemas.Product(**serialize_object(product)) for product in result]
        return schemas.ListProductsResponse(products=product_models)
    finally:
        soap.close()


@router.get(path='/casco-get-programs-sk',
            status_code=status.HTTP_200_OK,
            response_model=schemas.ListProgramsResponse,
            description='Метод получения списка программ СК')
def casco_get_programs_sk(company_id: str, product: str = None):
    """
        Get Programs SK Service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_list_programs_sk(client, company_id, product)
        program_models = [schemas.Program(**serialize_object(program)) for program in result]
        return schemas.ListProgramsResponse(programs=program_models)
    finally:
        soap.close()


@router.get(path='/casco-get-puu-marks',
            status_code=status.HTTP_200_OK,
            response_model=schemas.ListPuuMarksResponse,
            description='Метод получения списка марок ПУУ')
def casco_get_puu_marks():
    """
        Get PUU Marks Service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_list_puu_marks(client)
        puu_mark_models = [schemas.PuuMark(**serialize_object(puu_mark)) for puu_mark in result]
        return schemas.ListPuuMarksResponse(puu_marks=puu_mark_models)
    finally:
        soap.close()


@router.get(path='/casco-get-puu-models',
            status_code=status.HTTP_200_OK,
            responses={
                status.HTTP_404_NOT_FOUND: {
                    'description': 'Модель не найдена',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {'detail': 'string'}
                            }
                        }
                    }
                },
            },
            response_model=schemas.ListPuuModelsResponse,
            description='Метод получения моделей ПУУ по марке')
def casco_get_puu_models_by_mark_id(mark_id: str):
    """
        Get PUU Models By Mark Service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_list_models_puu_by_mark(client, mark_id)
        if result:
            puu_models = [schemas.PuuModel(**serialize_object(puu_model)) for puu_model in result]
            return schemas.ListPuuModelsResponse(puu_models=puu_models)

        raise global_exceptions.MyHTTPException(
            status=global_schemas.StatusResponseEnum.ERROR,
            status_code=status.HTTP_404_NOT_FOUND,
            message='Модель не найдена',
        )
    finally:
        soap.close()


@router.get(path='/casco-get-ref-info',
            status_code=status.HTTP_200_OK,
            response_model=schemas.RefInfoResponse,
            description='Метод получения справочной информации')
def casco_get_ref_info():
    """
        Get Reference information Service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_ref_info(client)
        ref_info_models = [schemas.RefInfo(**serialize_object(ref_info)) for ref_info in result]
        return schemas.RefInfoResponse(ref_info=ref_info_models)
    finally:
        soap.close()


@router.get(path='/casco-get-kladr-regions',
            status_code=status.HTTP_200_OK,
            response_model=schemas.KladrRegionResponse,
            description='Метод получения идентификатора, КЛАДРа с полным наименованием регионов')
def casco_get_kladr_regions():
    """
        Get Kladr Regions Service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_full_kladr_regions(client)
        kladr_regions_models = [schemas.KladrRegion(**serialize_object(kladr_region)) for kladr_region in result]
        return schemas.KladrRegionResponse(regions=kladr_regions_models)
    finally:
        soap.close()


@router.get(path='/casco-get-kladr-countries',
            status_code=status.HTTP_200_OK,
            response_model=schemas.CountriesResponse,
            description='Метод получения списка стран')
def casco_get_countries():
    """
        Get Countries Service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_full_kladr_countries(client)
        countries = [schemas.Country(**serialize_object(country)) for country in result]
        return schemas.CountriesResponse(countries=countries)
    finally:
        soap.close()


@router.get(path='/casco-get-stoa',
            status_code=status.HTTP_200_OK,
            response_model=schemas.StoaResponse,
            description='Получения вариантов возмещений')
def casco_get_soa():
    """
        Get Stoa Service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_stoa(client)
        stoa = [schemas.Stoa(**serialize_object(stoa)) for stoa in result]
        return schemas.StoaResponse(stoa=stoa)
    finally:
        soap.close()


@router.get(path='/casco-get-go-limit',
            status_code=status.HTTP_200_OK,
            response_model=schemas.GoLimitResponse,
            description='Метод получения страховых сумм СК по риску Расширению ГО')
def get_go_limit(company_id: str):
    """
        Get Go Limit Service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        result = soap.get_go_limit(client, company_id)
        go_limit = [schemas.GoLimit(**serialize_object(limit)) for limit in result]
        return schemas.GoLimitResponse(go_limit=go_limit)
    finally:
        soap.close()



@router.get(path='/casco-get-print-forms',
            status_code=status.HTTP_200_OK,
            description='Методы получения печатных форм')
def get_print_forms(order_id: str):
    """
        Get Print Forms Service
    """
    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        return soap.get_available_print_forms(client, order_id)
    finally:
        soap.close()


@router.post(path='/casco-calculation',
             status_code=status.HTTP_200_OK,
             responses={
                status.HTTP_400_BAD_REQUEST: {
                    'description': 'Произошла ошибка при получения предварительного расчета Спецтехники',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {'detail': 'string'}
                            }
                        }
                    }
                },
             },
             response_model=schemas.ResponseSuccessCascoCalculation,
             description='Метод получения предварительного расчета Спецтехники',)
def casco_calculation_service(company: str, data: schemas.EltCascoCalculation):
    """
        Casco calculation service
    """
    method = 'PreliminaryKASKOCalculation'
    cache_id = 'preliminary_casco_calculation'

    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        return soap.casco_calculation(client, method, company, cache_id, data)
    finally:
        soap.close()


@router.post(path='/finish-casco-calculation',
             status_code=status.HTTP_200_OK,
             description='Метод получения окончательного расчета и предварительного сохранения КАСКО')
async def finish_casco_calculation_service(company: str, data: schemas.EltCascoCalculation):
    """
        Finish Casco calculation service
    """
    method = 'FinalKASKOCalculation'
    cache_id = 'final_casco_calculation'

    elt_username, elt_password = settings.ELT_USERNAME, settings.ELT_PASSWORD.get_secret_value()

    soap = utils.SoapService(elt_username, elt_password)
    client = soap.get_client(elt_username, elt_password)

    try:
        return soap.casco_calculation(client, method, company, cache_id, data)
    finally:
        soap.close()
