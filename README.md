# Home Assistant Pion Power EV Charger Integration

This integration adds support for [Pion Power](https://www.pionpowertech.com/)
EV chargers that connect to WiFi and send their data to the Internet.

If you can sign in and see your charger and its data in the
[Pion Power Web UI](https://evcharger.pionpower.ca/PionPowerCustomer/#/login),
then this integration should work.

## Caution

This integration uses the same APIs as the web UI, and the web
UI only allows one session at a time for a given email address. If you
want to be able to use the web UI and this integration, create a second
Pion Power account using a different email, then share your charger
with the new account. Use one account for this integration and the other
when accessing the web UI.

# Installation

This code is still a work-in-progress, so for now, you need to manually
add this repo to the Home Assistant Community Store (HACS) add-on. Once
that has been done, HACS should keep this component up to date.
