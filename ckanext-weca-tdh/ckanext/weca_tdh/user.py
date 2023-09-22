import logging
import uuid
import random
import string
from ckan.common import session
from ckan import model
from ckan.logic import NotFound
import ckan.plugins.toolkit as toolkit
import ckanext.weca_tdh.config as C

log = logging.getLogger(__name__)

class User(object):

    def login(username: str):
        userobj = model.User.get(username)
        toolkit.login_user(userobj)

    def get_or_create_ad_user(claims: dict):
        ad_id = claims[C.CKAN_USER_ID]
        if not ad_id:
            log.error(f"Error in user claims. Missing 'id'")
            raise PermissionError

        ckan_id = f'ad-{ad_id}'
        email = claims[C.CKAN_USER_EMAIL]
        fullname = f'{claims[C.CKAN_USER_GIVEN_NAME]} {claims[C.CKAN_USER_SURNAME]}'
        is_sysadmin = claims.get(C.CKAN_ROLE_SYSADMIN, False)

        try:
            user = toolkit.get_action('user_show')(data_dict = {C.CKAN_USER_ID: ckan_id})

            if C.FF_AD_UPDATE_USER == 'True':
                # update user records. Only email and fullname can be updated
                log.info(f"Updating user records on login for user: {user}.")
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
                new_user.name = User.generate_username(fullname) # generate unique username
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
                raise Exception(f"Failed to create user: {e}")

        except KeyError as e:
            raise Exception(f"Key error in claims: {e}")

    def create_session(username: str):
        session['user'] = username
        session.save()

    def generate_username(fullname: str):
        '''
        Generates a unique username from given fullname
        ''' 
        fullname = fullname.lower().split()
        rnd_suffix = ''.join(random.choices(string.digits, k=5))
        username = f"{fullname[0][0]}{fullname[1]}{rnd_suffix}"
        return username
