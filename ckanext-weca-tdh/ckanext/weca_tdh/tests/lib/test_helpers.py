"""
Tests for helpers.py
"""

from ckanext.weca_tdh.lib.helpers import filter_datetime

def test_filter_datetime():
    # Sunny day
    assert filter_datetime("2023-06-20T12:50:49.555555") == "20 Jun 2023 12:50:49"
    assert filter_datetime("2023-06-20T12:50:49.555555", 'short') == "20 Jun 2023"

    # Invalid format
    assert filter_datetime("2023-06-20T12:50:49") != "20 Jun 2023 12:50:49"
    assert filter_datetime("2023-06-20") != "20 Jun 2023"
    assert filter_datetime("AAAAA") == ""
    
    # Invalid type
    assert filter_datetime("") == ""
    assert filter_datetime(None) == ""
