import plaid

from plaid.api import plaid_api
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products

from rich import print
import httpx


def create_client(clientId: str, secret: str) -> plaid_api.PlaidApi:
    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox, api_key={"clientId": clientId, "secret": secret}
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


def create_link_token(client: plaid_api.PlaidApi) -> str:

    request = LinkTokenCreateRequest(
        client_name="Plaid Test App",
        country_codes=[CountryCode("US")],
        language="en",
        user=LinkTokenCreateRequestUser(client_user_id="almond-user-id-0"),
        products=[Products("transactions"), Products("auth")],
    )
    response = client.link_token_create(request)
    print(response.to_dict())
    return response.link_token


def do_link(link_token: str):
    # open in a browser
    index = (
        r"""<script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
        <script>
          (function ($) {
            var linkToken = """
        + f"{link_token}"
        + """;
            var handler = Plaid.create({
              token: linkToken,
              receivedRedirectUri: window.location.href,
              onSuccess: function (public_token) {
                console.log(public_token);
              },
            });
            handler.open();
          })(jQuery);
        </script>
        """
    )
    with open("index.html", "w") as f:
        f.write(index)
