from __future__ import unicode_literals

from flask_dance.consumer import OAuth2ConsumerBlueprint
from functools import partial
from flask.globals import LocalProxy, _lookup_app_object
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


__maintainer__ = "Steven MARTINS <steven.martins.fr@gmail.com>"


def make_azure_blueprint(
        client_id=None, client_secret=None, scope=None, redirect_url=None,
        redirect_to=None, login_url=None, authorized_url=None,
        session_class=None, backend=None, tenant=None, resource=None):
    """
    Make a blueprint for authenticating with Azure AD using OAuth 2. This requires
    a client ID and client secret from Azure AD. You should either pass them to
    this constructor, or make sure that your Flask application config defines
    them, using the variables AZURE_OAUTH_CLIENT_ID and AZURE_OAUTH_CLIENT_SECRET.

    Args:
        client_id (str): The client ID for your application on Azure AD.
        client_secret (str): The client secret for your application on Azure AD
        scope (str, optional): comma-separated list of scopes for the OAuth token
        redirect_url (str): the URL to redirect to after the authentication
            dance is complete
        redirect_to (str): if ``redirect_url`` is not defined, the name of the
            view to redirect to after the authentication dance is complete.
            The actual URL will be determined by :func:`flask.url_for`
        login_url (str, optional): the URL path for the ``login`` view.
            Defaults to ``/azure``
        authorized_url (str, optional): the URL path for the ``authorized`` view.
            Defaults to ``/azure/authorized``.
        session_class (class, optional): The class to use for creating a
            Requests session. Defaults to
            :class:`~flask_dance.consumer.requests.OAuth2Session`.
        backend: A storage backend class, or an instance of a storage
                backend class, to use for this blueprint. Defaults to
                :class:`~flask_dance.consumer.backend.session.SessionBackend`.

    :rtype: :class:`~flask_dance.consumer.OAuth2ConsumerBlueprint`
    :returns: A :ref:`blueprint <flask:blueprints>` to attach to your Flask app.
    """
    if tenant is None:
        tenant = 'common'

    scope = scope or ["user.read"]
    authorization_url_params = {}
    if resource is not None:
        authorization_url_params['resource'] = resource
    azure_bp = OAuth2ConsumerBlueprint("azure", __name__,
        client_id=client_id,
        client_secret=client_secret,
        scope=scope,
        base_url="https://graph.microsoft.com/v1.0/",
        authorization_url="https://login.microsoftonline.com/{tenant}/oauth2/authorize".format(tenant=tenant),
        authorization_url_params=authorization_url_params,
        token_url="https://login.microsoftonline.com/{tenant}/oauth2/token".format(tenant=tenant),
        redirect_url=redirect_url,
        redirect_to=redirect_to,
        login_url=login_url,
        authorized_url=authorized_url,
        session_class=session_class,
        backend=backend,
    )
    azure_bp.from_config["client_id"] = "AZURE_OAUTH_CLIENT_ID"
    azure_bp.from_config["client_secret"] = "AZURE_OAUTH_CLIENT_SECRET"

    @azure_bp.before_app_request
    def set_applocal_session():
        ctx = stack.top
        ctx.azure_oauth = azure_bp.session

    return azure_bp

azure = LocalProxy(partial(_lookup_app_object, "azure_oauth"))
