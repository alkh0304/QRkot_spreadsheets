import copy

from datetime import datetime
from typing import List
from http import HTTPStatus

from aiogoogle import Aiogoogle
from fastapi import HTTPException

from app.core.config import settings
from app.models import CharityProject

FORMAT = "%Y/%m/%d %H:%M:%S"
COLUMNS = 11
ROWS = 100
TITLE = 'Отчет на {}'

SPREADSHEET = {
    'properties': {'locale': 'ru_RU'},
    'sheets': [{'properties': {
        'sheetType': 'GRID',
        'sheetId': 0,
        'title': 'Лист1',
        'gridProperties': {
            'rowCount': ROWS,
            'columnCount': COLUMNS
        }
    }}]
}
SPREADSHEET_HEADER = [
    ['Отчет от', ''],
    ['Рейтинг проектов по скорости закрытия'],
    ['Проект', 'Время сбора', 'Описание']
]


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = copy.deepcopy(SPREADSHEET)
    spreadsheet_body['properties']['title'] = TITLE.format(str(now_date_time))
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        charity_projects: List[CharityProject],
        wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_header = copy.deepcopy(SPREADSHEET_HEADER)
    spreadsheet_header[0][1] = str(now_date_time)
    project_rows = ((
        str(charity_project.name),
        str(charity_project.close_date - charity_project.create_date),
        str(charity_project.description)
    ) for charity_project in charity_projects)
    table_values = [
        *spreadsheet_header,
        *[list(row) for row in project_rows],
    ]
    current_rows = len(table_values)
    current_columns = max(len(table) for table in spreadsheet_header)
    if current_rows > ROWS or current_columns > COLUMNS:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Данные не помещаются в таблице")
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{ROWS}C{COLUMNS}',
            valueInputOption='USER_ENTERED',
            json={
                'majorDimension': 'ROWS',
                'values': table_values
            }
        )
    )
