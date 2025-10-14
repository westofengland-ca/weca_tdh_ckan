"""
Tests for user.py
"""

from ckan.logic import NotFound
from ckanext.weca_tdh.platform.auth.user import User
from unittest.mock import MagicMock, patch
import pytest, unittest


user_data = {
    'id': 'ad-5f43883e-63a8-4dc6-a070-b27681a5d000',
    'name': 'mock_user-test', 
    'fullname': 'Mock User'
}

def setup_mock_user_show(data_dict) -> dict:
    # Helper function to set up the mock for user_show action
    return user_data

def setup_mock_user_update(context, data_dict) -> dict:
    # Helper function to set up the mock for user_update action
    user_data['fullname'] = 'Updated User'
    return user_data


class ADUser(unittest.TestCase):

    def test_get_or_create_ad_user_new_user(self) -> None:
        # Test the scenario where the user does not exist and should be created
        # Set up the mocks
        mock_user_show = MagicMock(side_effect=NotFound)
        mock_user_update = MagicMock(side_effect=setup_mock_user_update)

        with patch('ckan.plugins.toolkit.get_action', side_effect = [mock_user_show, mock_user_update]), patch('ckan.model.Session', autospec=True):
            # Prepare the claims data
            claims_map = {
                'id': '5f43883e-63a8-4dc6-a070-b27681a5d000',
                'email': 'mockuser@test.com',
                'fullname': 'Mock User',
                'sysadmin': False
            }

            username = User.get_or_create_ad_user(claims_map)

            # Assert that 'user_show' was called once with user id
            mock_user_show.assert_called_once_with(data_dict={'id': 'ad-5f43883e-63a8-4dc6-a070-b27681a5d000'})

            # Assert that 'user_update' was not called
            mock_user_update.assert_not_called()

            # Assert a user was created
            assert username == 'mock_user-test'

    @pytest.mark.ckan_config("feature_flag.ad.update_user", 'True')
    def test_get_or_create_ad_user_existing_user(self) -> None:
        # Test the scenario where the user does exist and should not be updated
        # Set up the mocks
        mock_user_show = MagicMock(side_effect=setup_mock_user_show)
        mock_user_update = MagicMock(side_effect=setup_mock_user_update)
        mock_user_create = MagicMock()

        with patch('ckan.plugins.toolkit.get_action', side_effect = [mock_user_show, mock_user_update]), patch('ckan.model.Session', side_effect=mock_user_create):
            # Prepare the claims data
            claims_map = {
                'id': '5f43883e-63a8-4dc6-a070-b27681a5d000',
                'email': 'mockuser@test.com',
                'fullname': 'Mock User',
                'sysadmin': False
            }

            User.get_or_create_ad_user(claims_map)

            # Assert that 'user_show' was called once with user id
            mock_user_show.assert_called_once_with(data_dict={'id': 'ad-5f43883e-63a8-4dc6-a070-b27681a5d000'})
            
            # Assert that 'user_update' was not called
            mock_user_update.assert_called_once()

            # Assert that 'user_create' was not called
            mock_user_create.assert_not_called()

    @pytest.mark.ckan_config("feature_flag.ad.update_user", 'True')
    def test_get_or_create_ad_user_existing_user_update(self) -> None:
        # Test the scenario where the user does exist and should be updated
        # Set up the mocks
        mock_user_show = MagicMock(side_effect=setup_mock_user_show)
        mock_user_update = MagicMock(side_effect=setup_mock_user_update)
        mock_user_create = MagicMock()

        with patch('ckan.plugins.toolkit.get_action', side_effect = [mock_user_show, mock_user_update]), patch('ckan.model.Session', side_effect=mock_user_create):

            # Prepare the claims data
            claims_map = {
                'id': '5f43883e-63a8-4dc6-a070-b27681a5d000',
                'email': 'mockuser@test.com',
                'fullname': 'Updated User',
                'sysadmin': False
            }

            User.get_or_create_ad_user(claims_map)

            # Assert that 'user_show' was called once with user id
            mock_user_show.assert_called_once_with(data_dict={'id': f"ad-{claims_map['id']}"})

            # Assert that 'user_update' was called once with updated user data
            mock_user_update.assert_called_once_with(context={'ignore_auth': True}, data_dict={'id': f"ad-{claims_map['id']}", 'name': 'mock_user-test',
                                                                                                'fullname': 'Updated User', 'email': 'mockuser@test.com', 
                                                                                                'plugin_extras': {'ad_id': claims_map['id'], 'ad_groups': []}})

            # Assert that 'user_create' was not called
            mock_user_create.assert_not_called()
    
    @pytest.mark.ckan_config("feature_flag.ad.update_user", 'True')
    def test_get_or_create_ad_user_missing_claims(self) -> None:
        # Test the scenario where mandatory user claims are missing
        # Set up the mocks
        mock_user_show = MagicMock(side_effect=setup_mock_user_show)
        mock_user_update = MagicMock(side_effect=setup_mock_user_update)
        mock_user_create = MagicMock()

        with patch('ckan.plugins.toolkit.get_action', side_effect = [mock_user_show, mock_user_update]), patch('ckan.model.Session', side_effect=mock_user_create):
            # missing id
            with pytest.raises(Exception):
                User.get_or_create_ad_user({
                    'email': 'mockuser@test.com',
                    'fullname': 'Updated User 2',
                    'sysadmin': False
                  })

            # missing email
            with pytest.raises(Exception):
                User.get_or_create_ad_user({
                      'id': '5f43883e-63a8-4dc6-a070-b27681a5d000',
                      'fullname': 'Updated User 2',
                      'sysadmin': False
                    })

            # missing display name
            with pytest.raises(Exception):
                User.get_or_create_ad_user({
                      'id': '5f43883e-63a8-4dc6-a070-b27681a5d000',
                      'email': 'mockuser@test.com',
                      'sysadmin': False
                    })

            mock_user_show.assert_not_called()
            mock_user_update.assert_not_called()
            mock_user_create.assert_not_called()

    def test_generate_username(self) -> None:
        fullname = "Mock User"
        email = "mockemail@mockdomain.com"

        validation_results = [True, False, True, False, False, True]

        with patch.object(User, '_validate_username', side_effect = validation_results):
            # test fullname + domain
            username = User._generate_username(fullname, email)
            assert username == "mock_user-mockdomain"

            # test email username + domain
            username = User._generate_username(fullname, email)
            assert username == "mockemail-mockdomain"

            # test fullname + counter + domain
            username = User._generate_username(fullname, email)
            assert username == "mock_user2-mockdomain"

        # test username generation failure
        with patch.object(User, '_validate_username', return_value = False):
            with pytest.raises(Exception, match="invalid username constraints"):
                username = User._generate_username(fullname, email)
