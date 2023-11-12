from typing import Optional

import requests
from ipsw_parser.ipsw import IPSW
from remotezip import RemoteZip

from .types import *  # noqa: F403


class _API:
    def __init__(self):
        self._session = requests.Session()

    def __del__(self):
        self._session.close()

    def json_request(self, url: str, **kwargs):
        return self._session.get(url, **kwargs).json()


class Device(_API):
    def __init__(self, *, data: dict) -> None:
        super().__init__()
        self._parse_data(data)

    def _parse_data(self, data: dict) -> None:
        self._name = data['name']
        self._identifier = data['identifier']
        self._boards = [BoardVariant(*board.values()) for board in data['boards']]  # noqa: F405

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
    def search(cls, *, name: Optional[str] = None, identifier: Optional[str] = None):
        if name is None and identifier is None:
            raise ValueError('Either device name or identifier must be provided.')

        api_data = requests.get(get_url(GET_DEVICES)).json()  # noqa: F405

        if name:
            devices = [
                device
                for device in api_data
                if name.casefold() == device['name'].casefold()
                or name.casefold() in device['name'].casefold()
            ]
            match len(devices):
                case 0:
                    raise ValueError(f'No device found with name {name}')
                case 1:
                    device = devices[0]
                case _:
                    raise ValueError(
                        f'Multiple devices found with name {name} ({len(devices)}): {", ".join([device['name'] for device in devices])}'
                    )

        elif identifier:
            try:
                device = next(
                    device
                    for device in api_data
                    if identifier.casefold() == device['identifier'].casefold()
                )
            except StopIteration:
                raise ValueError(f'No device found with identifier {identifier}')

        return cls(data=device)

    def get_firmware(
        self, *, version: Optional[str] = None, buildid: Optional[str] = None
    ):
        if version is None and buildid is None:
            raise ValueError('Either firmware version or buildid must be provided.')

        api_data = _API().json_request(
            get_url(GET_DEVICE_IPSWS, identifier=self.identifier)  # noqa: F405
        )
        firmwares = api_data['firmwares']

        if version:
            firmwares = [
                firmware for firmware in firmwares if version == firmware['version']
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
            try:
                firmware = next(
                    firmware
                    for firmware in firmwares
                    if buildid.casefold() == firmware['buildid'].casefold()
                )
            except StopIteration:
                raise ValueError(f'No firmware found with buildid {buildid}')

        return IPSW(RemoteZip(firmware['url'], session=self._session))
