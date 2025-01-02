import logging
import re
import uuid

import ckan.plugins.toolkit as toolkit
from ckan import model
from ckan.logic import NotFound

import ckanext.weca_tdh.config as C

log = logging.getLogger(__name__)


class User(object):
    
    @classmethod
    def get_or_create_ad_user(cls, claims: dict) -> str:
        try:
            ad_id = claims[C.CKAN_USER_ID]
            ckan_id = f'ad-{ad_id}'
            email = claims[C.CKAN_USER_EMAIL]
            fullname = claims[C.CKAN_USER_FULLNAME]
            is_sysadmin = claims.get(C.CKAN_ROLE_SYSADMIN, False)

            user = toolkit.get_action('user_show')(data_dict = {C.CKAN_USER_ID: ckan_id})

            if user.get(C.CKAN_USER_STATE) == 'deleted':
                log.error(f"failed to authenticate user {ad_id}. Account deleted.")
                raise Exception(f"account for {user[C.CKAN_USER_NAME]} deleted.")

            if C.FF_AD_UPDATE_USER == 'True':
                # update user records. Only email and fullname can be updated
                user[C.CKAN_USER_EMAIL] = email # email cannot be retrieved, but must be set on update
                user[C.CKAN_USER_FULLNAME] = fullname 
                user = toolkit.get_action('user_update')(context = {'ignore_auth': True}, data_dict = user)

            return user[C.CKAN_USER_NAME]

        except NotFound:
            log.debug("Creating new user...")
            try:
                # Create new ckan user obj
                new_user = model.User()
                new_user.id = ckan_id
                new_user.name = cls._generate_username(fullname, email) # generate unique username
                new_user.password = str(uuid.uuid4())  # generate unique password
                new_user.fullname = fullname
                new_user.email = email
                new_user.sysadmin = is_sysadmin
                new_user.plugin_extras = {
                    'ad_id': ad_id
                }
                
                # Add the user to the database session
                model.Session.add(new_user)

                # Commit the changes to the database
                model.Session.commit()

                log.info(f"No user record found for user: {new_user.name}. New user record created.")
                return new_user.name

            except Exception as e:
                model.Session.rollback()
                raise Exception(f"failed to create user: {e}.")

        except KeyError as e:
            log.error(f"failed to authenticate user {claims.get(C.CKAN_USER_ID, '')}. The claims received from Azure AD are missing the {e} claim.")
            raise Exception(f"{e} is missing from account details")

    @classmethod
    def _generate_username(cls, fullname: str, email: str) -> str:
        '''
        Generates a unique username from given fullname and email
        ''' 
        # sanitise fullname
        ckname = re.sub(r'[^\w]', '_', fullname).lower()

        # sanitise email username
        email_username, email_domain = email.split('@')
        ckemail = re.sub(r'[^\w]', '_', email_username).lower()

        # sanitise email domain
        email_domain = email_domain.split('.')[0]
        ckdomain = re.sub(r'[^\w-]', '_', email_domain).lower()

        # try fullname + domain
        username = f"{ckname}-{ckdomain}"
        if cls._validate_username(username):
            return username
        
        # try email + domain
        username = f"{ckemail}-{ckdomain}"
        if cls._validate_username(username):
            return username

        max_name_creation_attempts = 100

        # else iterate fullname + domain
        for n in range(2, max_name_creation_attempts):
            username = f"{ckname}{n}-{ckdomain}"
            if cls._validate_username(username):
                return username

        # would only occur if CKAN enforce new constaints
        raise Exception("invalid username constraints")

    @staticmethod
    def _validate_username(username: str) -> bool:
        return model.User.check_name_valid(username) and model.User.check_name_available(username)
