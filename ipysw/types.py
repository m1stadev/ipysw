from dataclasses import dataclass
from enum import IntEnum

BASE_API = 'https://api.ipsw.me/v4'


class APIEndpointArgType(IntEnum):
    NONE = 0
    DEVICE_VERSION = 1
    IDENTIFIER = 2
    IDENTIFIER_BUILDID = 3
    #    ITUNES_PLATFORM = 4
    #    ITUNES_PLATFORM_VERSION = 5
    MODEL = 6
    PLATFORM_VERSION = 7
    VERSION = 8


@dataclass(frozen=True)
class BoardVariant:
    boardconfig: str
    platform: str
    cpid: int
    bdid: int


@dataclass(frozen=True)
class APIEndpoint:
    endpoint: str
    arg_type: APIEndpointArgType


GET_MODEL_IDENTIFIER = APIEndpoint('/model/{model}', APIEndpointArgType.MODEL)
GET_DEVICES = APIEndpoint('/devices', APIEndpointArgType.NONE)

GET_DEVICE_INFO = APIEndpoint('/device/{identifier}', APIEndpointArgType.IDENTIFIER)
GET_IPSW_DOWNLOAD = APIEndpoint(
    '/ipsw/download/{identifier}/{buildid}', APIEndpointArgType.IDENTIFIER_BUILDID
)
GET_IPSW_INFO = APIEndpoint(
    '/ipsw/{identifier}/{buildid}', APIEndpointArgType.IDENTIFIER_BUILDID
)
GET_VERSION_IPSWS = APIEndpoint('/ipsw/{version}', APIEndpointArgType.VERSION)

GET_VERSION_OTAS = APIEndpoint('/ota/{version}', APIEndpointArgType.VERSION)
GET_OTA_DOCS = APIEndpoint(
    '/ota/documentation/{device}/{version}', APIEndpointArgType.DEVICE_VERSION
)
GET_OTA_DOWNLOAD = APIEndpoint(
    '/ota/download/{identifier}/{buildid}', APIEndpointArgType.IDENTIFIER_BUILDID
)
GET_OTA_INFO = APIEndpoint(
    '/ota/{identifier}/{buildid}', APIEndpointArgType.IDENTIFIER_BUILDID
)


def get_url(endpoint: APIEndpoint, **kwargs) -> str:
    try:
        match endpoint.arg_type:
            case APIEndpointArgType.NONE:
                endpoint = endpoint.endpoint
            case APIEndpointArgType.DEVICE_VERSION:
                endpoint = endpoint.endpoint.format(
                    device=kwargs['device'], version=kwargs['version']
                )
            case APIEndpointArgType.IDENTIFIER:
                endpoint = endpoint.endpoint.format(identifier=kwargs['identifier'])
            case APIEndpointArgType.IDENTIFIER_BUILDID:
                endpoint = endpoint.endpoint.format(
                    identifier=kwargs['identifier'], buildid=kwargs['buildid']
                )
            case APIEndpointArgType.MODEL:
                endpoint = endpoint.endpoint.format(model=kwargs['model'])
            case APIEndpointArgType.PLATFORM_VERSION:
                endpoint = endpoint.endpoint.format(version=kwargs['platform_version'])
            case APIEndpointArgType.VERSION:
                endpoint = endpoint.endpoint.format(version=kwargs['version'])
    except KeyError:
        raise ValueError(f'Invalid arguments for endpoint: {endpoint}')

    return BASE_API + endpoint
