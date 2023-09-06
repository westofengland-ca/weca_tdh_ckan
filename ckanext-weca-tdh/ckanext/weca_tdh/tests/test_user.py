"""
Tests for user.py
"""

import pytest
import unittest
from unittest.mock import MagicMock, patch
from ckanext.weca_tdh.user import User
from ckan.logic import NotFound

user_data = {
        'id': 'ad-5f43883e-63a8-4dc6-a070-b27681a5d000',
        'name': 'muser10789', 
        'fullname': 'Mock User'
    }

def setup_mock_user_show(data_dict):
    # Helper function to set up the mock for user_show action
    return user_data

def setup_mock_user_update(context, data_dict):
    # Helper function to set up the mock for user_update action
    user_data['fullname'] = 'Updated User'
    return user_data

class ADUser(unittest.TestCase):
    def test_get_or_create_ad_user_new_user(self):
        # Test the scenario where the user does not exist and should be created
        # Set up the mocks
        mock_user_show = MagicMock(side_effect=NotFound)
        mock_user_update = MagicMock(side_effect=setup_mock_user_update)

        with patch('ckan.plugins.toolkit.get_action', side_effect = [mock_user_show, mock_user_update]), patch('ckan.model.Session', autospec=True):
            # Prepare the claims data
            claims_map = {
                'id': '5f43883e-63a8-4dc6-a070-b27681a5d000',
                'email': 'mockuser@email.com',
                'given_name': 'Mock',
                'surname': 'User',
                'sysadmin': False
            }

            username = User.get_or_create_ad_user(claims_map)

            # Assert that 'user_show' was called once with user id
            mock_user_show.assert_called_once_with(data_dict={'id': 'ad-5f43883e-63a8-4dc6-a070-b27681a5d000'})

            # Assert that 'user_update' was not called
            mock_user_update.assert_not_called()

            # Assert a user was created
            assert username is not None

    @pytest.mark.ckan_config("feature_flag.ad.update_user", 'True')
    def test_get_or_create_ad_user_existing_user(self):
        # Test the scenario where the user does exist and should not be updated
        # Set up the mocks
        mock_user_show = MagicMock(side_effect=setup_mock_user_show)
        mock_user_update = MagicMock(side_effect=setup_mock_user_update)
        mock_user_create = MagicMock()

        with patch('ckan.plugins.toolkit.get_action', side_effect = [mock_user_show, mock_user_update]), patch('ckan.model.Session', side_effect=mock_user_create):
            # Prepare the claims data
            claims_map = {
                'id': '5f43883e-63a8-4dc6-a070-b27681a5d000',
                'email': 'mockuser@email.com',
                'given_name': 'Mock',
                'surname': 'User',
                'sysadmin': False
            }

            username = User.get_or_create_ad_user(claims_map)

            # Assert that 'user_show' was called once with user id
            mock_user_show.assert_called_once_with(data_dict={'id': 'ad-5f43883e-63a8-4dc6-a070-b27681a5d000'})
            
            # Assert that 'user_update' was not called
            mock_user_update.assert_called_once()

            # Assert that 'user_create' was not called
            mock_user_create.assert_not_called()

            assert username == 'muser10789'

    @pytest.mark.ckan_config("feature_flag.ad.update_user", 'True')
    def test_get_or_create_ad_user_existing_user_update(self):
        # Test the scenario where the user does exist and should be updated
        # Set up the mocks
        mock_user_show = MagicMock(side_effect=setup_mock_user_show)
        mock_user_update = MagicMock(side_effect=setup_mock_user_update)
        mock_user_create = MagicMock()

        with patch('ckan.plugins.toolkit.get_action', side_effect = [mock_user_show, mock_user_update]), patch('ckan.model.Session', side_effect=mock_user_create):

            # Prepare the claims data
            claims_map = {
                'id': '5f43883e-63a8-4dc6-a070-b27681a5d000',
                'email': 'mockuser@email.com',
                'given_name': 'Updated',
                'surname': 'User',
                'sysadmin': False
            }

            username = User.get_or_create_ad_user(claims_map)

            # Assert that 'user_show' was called once with user id
            mock_user_show.assert_called_once_with(data_dict={'id': 'ad-5f43883e-63a8-4dc6-a070-b27681a5d000'})

            # Assert that 'user_update' was called once with updated user data
            mock_user_update.assert_called_once_with(context={'ignore_auth': True}, data_dict={'id': 'ad-5f43883e-63a8-4dc6-a070-b27681a5d000', 'name': 'muser10789',
                                                                                                'fullname': 'Updated User', 'email': 'mockuser@email.com'})

            # Assert that 'user_create' was not called
            mock_user_create.assert_not_called()

            assert username == 'muser10789'

    def test_generate_username(self):
      # Test the username generation function
      fullname = 'Mock User'
      username = User.generate_username(fullname)
      assert len(username) == len(fullname.split()[0][0]) + len(fullname.split()[1]) + 5
