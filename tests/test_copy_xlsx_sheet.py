import datetime

import openpyxl
import pytest

import copy_xlsx_sheet


@pytest.mark.parametrize(
    ('day', 'expected'),
    [(1, 1), (7, 1), (8, 2), (14, 2), (15, 3), (28, 4), (29, 5), (31, 5)],
)
def test_get_nth_week(day, expected):
    assert copy_xlsx_sheet.get_nth_week(day) == expected


def test_get_nth_dow():
    # 2020-12-21 は第 3 月曜日です。
    assert copy_xlsx_sheet.get_nth_dow(2020, 12, 21) == (3, 0)


@pytest.mark.parametrize(
    ('today', 'expected'),
    [
        # 水曜日 (定期実行の曜日) なら翌週の月曜日。
        (datetime.date(2020, 12, 16), datetime.date(2020, 12, 21)),
        # 日曜日なら翌日。
        (datetime.date(2020, 12, 20), datetime.date(2020, 12, 21)),
        # 月曜日ならその日。
        (datetime.date(2020, 12, 21), datetime.date(2020, 12, 21)),
        # 月またぎ。
        (datetime.date(2020, 12, 30), datetime.date(2021, 1, 4)),
    ],
)
def test_get_next_monday(today, expected):
    assert copy_xlsx_sheet.get_next_monday(today) == expected


def test_get_next_monday_defaults_to_today():
    next_monday = copy_xlsx_sheet.get_next_monday()
    assert next_monday.weekday() == 0
    assert 0 <= (next_monday - datetime.date.today()).days < 7


def _make_workbook(path):
    workbook = openpyxl.Workbook()
    workbook.active.title = 'Format base'
    workbook['Format base']['A1'] = 'template'
    workbook.save(path)


def test_run_adds_sheet_copied_from_format_base(tmp_path, monkeypatch):
    path = tmp_path / 'book.xlsx'
    _make_workbook(path)
    monkeypatch.setattr(
        copy_xlsx_sheet, 'get_next_monday', lambda: datetime.date(2020, 12, 21)
    )

    copy_xlsx_sheet.run(str(path))

    workbook = openpyxl.load_workbook(path)
    assert workbook.sheetnames == ['Format base', '12月第3月曜日']
    assert workbook['12月第3月曜日']['A1'].value == 'template'


def test_run_skips_existing_sheet(tmp_path, monkeypatch):
    path = tmp_path / 'book.xlsx'
    _make_workbook(path)
    monkeypatch.setattr(
        copy_xlsx_sheet, 'get_next_monday', lambda: datetime.date(2020, 12, 21)
    )

    copy_xlsx_sheet.run(str(path))
    copy_xlsx_sheet.run(str(path))

    workbook = openpyxl.load_workbook(path)
    assert workbook.sheetnames == ['Format base', '12月第3月曜日']
