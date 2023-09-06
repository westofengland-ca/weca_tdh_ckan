from flask import render_template

class RouteController():
    def render_contact_page():
        return render_template('contact.html')
    
    def render_policy_page():
        return render_template('policy.html')
    
    def render_license_page():
        return render_template('license.html')
