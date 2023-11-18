from keycloak import KeycloakAdmin, KeycloakOpenID
from app.settings import AppSettings

keycloak_admin = KeycloakAdmin(
    server_url=AppSettings.KEYCLOAK_URL,
    realm_name=AppSettings.KEYCLOAK_REALM,
    client_id=AppSettings.KEYCLOAK_CLIENT_ID,
    client_secret_key=AppSettings.KEYCLOAK_CLIENT_SECRET,
    verify=True,
)

keycloak_openid = KeycloakOpenID(
    server_url=AppSettings.KEYCLOAK_URL,
    realm_name=AppSettings.KEYCLOAK_REALM,
    client_id=AppSettings.KEYCLOAK_CLIENT_ID,
    client_secret_key=AppSettings.KEYCLOAK_CLIENT_SECRET,
    verify=True,
)