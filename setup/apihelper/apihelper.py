"""
API helper functions and classes - including retries, exception handling,
and a Base URL session object to simplify requests made from the calling
script.

Previous incarnation was class-based, this extracts relevant methods
and is function-based to just return objects when necessary...
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests_toolbelt import sessions
import urllib3.exceptions

# Default request timeout
REQUEST_TIMEOUT = 5


# Decorator function to catch HTTP exceptions
def http_exceptions(func):
    """
    Used as a wrapper to raise an HTTP request for status and catch/display
    common error types

    :param func: Function to wrap inside this decorator
    :return: Executed function result
    """
    def wrapper(*args, **kwargs):
        # Set a result first so it's not eaten in the event of exception
        wrapper_result = False
        try:
            wrapper_result = func(*args, **kwargs)
        except requests.exceptions.HTTPError as err:
            print(f"Http Error: {err}")
        except requests.exceptions.ConnectionError as err:
            print(f"Error Connecting: {err}")
        except requests.exceptions.Timeout as err:
            print(f"Timeout Error: {err}")
        except requests.exceptions.RequestException as err:
            print(f"Generic Request Exception: {err}")
        except requests.exceptions.RequestsWarning as err:
            print(f"HTTP: Request warning encountered: {err}")
        except urllib3.exceptions.MaxRetryError as err:
            print(f"HTTP: Max retries reached, request failed: {err}")
        return wrapper_result
    return wrapper


default_retry_strategy = Retry(
    total=3,
    redirect=16,
    backoff_factor=0.3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=[
        "HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS", "TRACE"
    ],
    respect_retry_after_header=True
)


# pylint: disable-next=too-few-public-methods
class BearerAuth(requests.auth.AuthBase):
    """
    Generic BearerAuth class for HTTP authentication.  Given a token, adds a
    header dict of "Authorization: Bearer (token)" to the HTTP request.
    """
    def __init__(self, token):
        """
        Class initialization
        :param token:
            String - the token argument will be used when creating the
            "Authorization" HTTP header upon instantiation.
        """
        # Assign the token to a class variable
        self.token = token

    def __call__(self, r):
        """
        When the BearerAuth class is called as a function (e.g. passed to a
        requests object), this function is executed and will set the
        "Authorization" HTTP header for the passed requests object
        :param r:
            Requests object which will have the "Authorization" header set
        :return:
            The passed requests object
        """
        r.headers["Authorization"] = "Bearer " + self.token
        return r


class TimeoutHTTPAdapter(HTTPAdapter):
    """
    Extends the HTTPAdapter class to set a timeout for requests Session
    objects.  When used for a session, set the timeout to the value of
    REQUEST_TIMEOUT by default.  This will be overridden if the
    'timeout' argument is supplied.
    """
    def __init__(self, *args, **kwargs):
        self.timeout = REQUEST_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, *args, **kwargs):
        timeout = kwargs.get('timeout')
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, *args, **kwargs)


def init_http_session(baseurl=None, auth=None):
    """
    Create an HTTP session object - either BaseUrl if specified or a generic
    session if the baseurl is not provided.  The advantage of an HTTP session
    object is that parameters can be set one time and reused for every request.
    For example, headers and TLS verification can be set in the request object
    and then will not need to be passed for every request inside a script.

    If a BaseUrlSession is created, all URLs can be specified as relative
    to the baseurl during requests.

    :param baseurl: (Optional) If specified, creates a BaseUrlSession object
        and subsequent requests may be made with relative paths
    :param auth: (Optional) Reference to a requests.auth.AuthBase object to
        initialize authentication for the requests session

    :return: Python requests Session object which can be used to perform
        requests by the calling script
    """
    # pylint: disable-next=unused-argument
    def http_assert_status_hook(response, *args, **kwargs):
        return response.raise_for_status()

    if baseurl:
        http_session = sessions.BaseUrlSession(base_url=baseurl)
    else:
        http_session = requests.Session()

    http_session.mount("https://", TimeoutHTTPAdapter(max_retries=default_retry_strategy))
    http_session.mount("http://", TimeoutHTTPAdapter(max_retries=default_retry_strategy))

    http_session.hooks['response'] = [http_assert_status_hook]

    if auth:
        http_session.auth = auth

    return http_session


def close_http_session(http_session):
    """
    Close the HTTP session

    :param http_session: Request Session object reference to close

    :return: None (no return)
    """
    http_session.close()
