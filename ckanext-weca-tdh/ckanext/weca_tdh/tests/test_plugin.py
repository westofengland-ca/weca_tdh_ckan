"""
Tests for plugin.py
"""

import pytest
import ckan.plugins as plugins

@pytest.mark.ckan_config("ckan.plugins", "weca_tdh")
@pytest.mark.usefixtures("with_plugins")
def test_plugin():
    assert plugins.plugin_loaded("weca_tdh")

def test_contact_endpoint(app):
    url = plugins.toolkit.url_for('weca_tdh.contact')
    response = app.get(url)

    assert response.status_code == 200

def test_policy_endpoint(app):
    url = plugins.toolkit.url_for('weca_tdh.policy')
    response = app.get(url)

    assert response.status_code == 200

def test_accessibility_endpoint(app):
    url = plugins.toolkit.url_for('weca_tdh.accessibility')
    response = app.get(url)

    assert response.status_code == 200
