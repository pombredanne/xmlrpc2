import pytest

from xmlrpc2.utils import iso8601


@pytest.mark.parametrize("input", ["2006-10-11T00:14:33Z", "20061011T00:14:33Z"])
def test_iso8601_regex(input):
    assert iso8601.ISO8601_REGEX.match(input)


def test_timezone_regex():
    assert iso8601.TIMEZONE_REGEX.match("+01:00")
    assert iso8601.TIMEZONE_REGEX.match("+00:00")
    assert iso8601.TIMEZONE_REGEX.match("+01:20")
    assert iso8601.TIMEZONE_REGEX.match("-01:00")


@pytest.mark.parametrize("input", ["2006-10-20T15:34:56Z", "20061020T15:34:56Z"])
def test_parse_date(input):
    d = iso8601.parse(input)

    assert d.year == 2006
    assert d.month == 10
    assert d.day == 20
    assert d.hour == 15
    assert d.minute == 34
    assert d.second == 56
    assert d.tzinfo == iso8601.UTC


@pytest.mark.parametrize("input", ["2006-10-20T15:34:56.123Z", "20061020T15:34:56.123Z"])
def test_parse_date_fraction(input):
    d = iso8601.parse(input)

    assert d.year == 2006
    assert d.month == 10
    assert d.day == 20
    assert d.hour == 15
    assert d.minute == 34
    assert d.second == 56
    assert d.microsecond == 123000
    assert d.tzinfo == iso8601.UTC


@pytest.mark.parametrize("input", ["2007-5-7T11:43:55.328Z'"])
def test_parse_date_fraction_2(input):
    d = iso8601.parse(input)

    assert d.year == 2007
    assert d.month == 5
    assert d.day == 7
    assert d.hour == 11
    assert d.minute == 43
    assert d.second == 55
    assert d.microsecond == 328000
    assert d.tzinfo == iso8601.UTC


@pytest.mark.parametrize("input", ["2006-10-20T15:34:56.123+02:30", "20061020T15:34:56.123+02:30"])
def test_parse_date_tz(input):
    d = iso8601.parse(input)

    assert d.year == 2006
    assert d.month == 10
    assert d.day == 20
    assert d.hour == 15
    assert d.minute == 34
    assert d.second == 56
    assert d.microsecond == 123000
    assert d.tzinfo.tzname(None) == "+02:30"

    offset = d.tzinfo.utcoffset(None)

    assert offset.days == 0
    assert offset.seconds == 60 * 60 * 2.5


def test_parse_invalid_date():
    with pytest.raises(iso8601.ParseError):
        iso8601.parse(None)


def test_parse_invalid_date2():
    with pytest.raises(iso8601.ParseError):
        iso8601.parse("23")


@pytest.mark.parametrize("input", ["2007-01-01T08:00:00", "20070101T08:00:00"])
def test_parse_no_timezone(input):
    """
    This tests what happens when you parse a date with no timezone. While not
    strictly correct this is quite common. I'll assume UTC for the time zone
    in this case.
    """
    d = iso8601.parse(input)

    assert d.year == 2007
    assert d.month == 1
    assert d.day == 1
    assert d.hour == 8
    assert d.minute == 0
    assert d.second == 0
    assert d.microsecond == 0
    assert d.tzinfo == iso8601.UTC


@pytest.mark.parametrize("input", ["2007-01-01T08:00:00", "20070101T08:00:00"])
def test_parse_no_timezone_different_default(input):
    tz = iso8601.FixedOffset(2, 0, "test offset")
    d = iso8601.parse(input, default_timezone=tz)

    assert d.tzinfo == tz


def test_space_separator():
    """
    Handle a separator other than T
    """
    d = iso8601.parse("2007-06-23 06:40:34.00Z")

    assert d.year == 2007
    assert d.month == 6
    assert d.day == 23
    assert d.hour == 6
    assert d.minute == 40
    assert d.second == 34
    assert d.microsecond == 0
    assert d.tzinfo == iso8601.UTC
