from typing import Optional

import requests
from ipsw_parser.ipsw import IPSW
from remotezip import RemoteZip

from .types import *  # noqa: F403


class _API:
    def __init__(self, *, session: requests.Session):
        self._session = session

    def __del__(self):
        self._session.close()

    def json_request(self, url: str, **kwargs):
        return self._session.get(url, **kwargs).json()


class Device(_API):
    def __init__(
        self, *, identifier: Optional[str], session: Optional[requests.Session] = None
    ) -> None:
        if session is None:
            session = requests.Session()

        super().__init__(session=session)

        if identifier is None:
            raise ValueError('A device identifier must be provided.')

        api_data = self.json_request(get_url(GET_DEVICE_INFO, identifier=identifier))  # noqa: F405

        self._name = api_data['name']
        self._identifier = api_data['identifier']
        self._boards = [BoardVariant(*board.values()) for board in api_data['boards']]  # noqa: F405

    @property
    def name(self) -> str:
        return self._name

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def boards(self) -> list[BoardVariant]:  # noqa: F405
        return self._boards

    @classmethod
    def search(
        cls, *, name: Optional[str] = None, session: Optional[requests.Session] = None
    ):
        if name is None:
            raise ValueError('Ddevice name must be provided.')

        if session is None:
            session = requests.Session()

        api_data = session.get(get_url(GET_DEVICES)).json()  # noqa: F405

        # TODO: Move to fuzzy-searching strings and choosing the closest device
        devices = [
            device
            for device in api_data
            if (name.casefold() == device['name'].casefold())
            or (name.casefold() in device['name'].casefold())
        ]

        match len(devices):
            case 0:
                raise ValueError(f'No device found with name {name}')
            case 1:
                device = devices[0]
            case _:
                raise ValueError(
                    f'Multiple devices found with name {name} ({len(devices)}): {", ".join([device["name"] for device in devices])}'
                )

        return cls(identifier=device['identifier'], session=session)

    def get_firmware(
        self, *, version: Optional[str] = None, buildid: Optional[str] = None
    ):
        if version is None and buildid is None:
            raise ValueError('Either firmware version or buildid must be provided.')

        if version:
            api_data = self.json_request(
                get_url(GET_DEVICE_INFO, identifier=self.identifier)  # noqa: F405
            )

            firmwares = [
                firmware
                for firmware in api_data['firmwares']
                if version == firmware['version']
            ]
            match len(firmwares):
                case 0:
                    raise ValueError(f'No firmware found with version {version}')
                case 1:
                    firmware = firmwares[0]
                case _:
                    raise ValueError(
                        f'Multiple firmwares found with version {version} ({len(firmwares)})'
                    )

        elif buildid:
            firmware = self.json_request(
                get_url(GET_IPSW_INFO, identifier=self.identifier, buildid=buildid)  # noqa: F405
            )

        # TODO: Write a separate class for IPSW, store ipsw_parser.IPSW in it as an attribute
        return IPSW(RemoteZip(firmware['url'], session=self._session))
