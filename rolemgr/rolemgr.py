import os
import reflex as rx
import discordoauth2
import requests
import json
from typing import Dict


class State(rx.State):
    """The app state."""
    acct_user: str = rx.LocalStorage(name="acct_user")
    acct_id: str = rx.LocalStorage(name="acct_id")
    acct_auth_good: bool = False
    discord_client_id = os.environ.get("CLIENT_ID")
    discord_client_secret = os.environ.get("CLIENT_SECRET")
    discord_callback_url = os.environ.get("CALLBACK_URL")
    discord_app_token = os.environ.get("APP_TOKEN")

    @rx.event
    def discord_auth_status(self):
        self.auth_status = not (self.auth_status)

    @rx.event
    def auth_redir(self):
        client = discordoauth2.Client(self.discord_client_id,
                                      self.discord_client_secret,
                                      self.discord_callback_url)
        return rx.redirect(client.generate_uri(scope=["identify"]))

    @rx.event
    def change_acct_auth(self):
        self.acct_auth_good = not (self.acct_auth_good)

    @rx.event
    def process_callback(self):
        auth_code = self.router.page.params['code']
        client = discordoauth2.Client(self.discord_client_id,
                                      self.discord_client_secret,
                                      self.discord_callback_url)
        access = client.exchange_code(auth_code)

        identity = access.fetch_identify()

        self.set_acct_user(identity['username'])
        self.set_acct_id(identity['id'])
        self.change_acct_auth()

        return rx.redirect("/usercfg")

    roles: Dict[str, str] = {"Strawberry": "722481631591399484",
                             "Magma": "722480272204890113",
                             "Saturn": "921573908845588480",
                             "Lemon": "722463939933503551",
                             "Kiwi": "722460654019280998",
                             "Green Apple": "722464058590363669",
                             "Sauropod": "722474287801303040",
                             "Ocean": "722476867919020102",
                             "Blueberry": "722476184012587088",
                             "Yinmn": "956594507263148032",
                             "Grape": "722467658792042567",
                             "Magenta": "722464493187104768",
                             "Pink": "722506272968147034"}

    curr_roles: Dict[str, str] = {}

    @rx.event
    def get_user_roles(self):

        user_profile_header = {"Authorization": "Bot "
                               + self.discord_app_token}
        user_profile_req = requests.get(
            'https://discord.com/api/guilds/71992212115697664/members/'
            + self.acct_id, headers=user_profile_header)
        user_profile = json.loads(user_profile_req.text)

        user_roles = user_profile['roles']

        self.curr_roles.clear()

        for x in user_roles:
            for key, value in self.roles.items():
                if x == value:
                    self.curr_roles.update({key: value})

    @rx.event
    def set_role(self, role: str):
        for key, value in self.roles.items():
            if role == key:
                user_profile_header = {"Authorization": "Bot "
                                       + self.discord_app_token}
                old_role = list(self.curr_roles.values())[0]
                requests.delete('https://discord.com/api/guilds/71992212115697664/members/'
                                + self.acct_id + '/roles/'
                                + old_role, headers=user_profile_header)
                requests.put('https://discord.com/api/guilds/71992212115697664/members/'
                             + self.acct_id + '/roles/'
                             + value, headers=user_profile_header)

        return rx.redirect("/usercfg")


def draw_roles_box(role: str):
    return rx.box(rx.text(role))


def draw_roles_buttons(role: str):
    return rx.button(role, on_click=State.set_role(role))


def navbar_link(text: str, url: str) -> rx.Component:
    """A link in the navbar."""
    return rx.link(rx.text(text), href=url, size="4", margin="0 10px")


def navbar() -> rx.Component:
    return rx.box(
        rx.desktop_only(
            rx.hstack(
                rx.hstack(
                    rx.heading(
                        "Lyokocord", size="7", weight="bold"
                    ),
                    align_items="center"
                ),
                rx.hstack(
                    navbar_link("Home", "/"),
                    navbar_link("Rules", "/rules"),
                    navbar_link("User Settings", "/usercfg"),
                    justify="end",
                    spacing="5",
                ),
                justify="between",
                align_items="center",
            )
        ),
        rx.mobile_and_tablet(
            rx.hstack(
                rx.hstack(
                    rx.heading(
                        "Lyokocord", size="6", weight="bold"
                    ),
                    align_items="center",
                ),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.icon("menu", size=30)
                    ),
                    rx.menu.content(
                        rx.menu.item("Home"),
                        rx.menu.item("Rules"),
                        rx.menu.item("User Settings"),
                    ),
                    justify="end",
                ),
                justify="between",
                align_items="center",
            ),
        ),
        bg=rx.color("accent", 3),
        padding="1em",
        # position="fixed",
        # top="0px",
        # z_index="5",
        width="100%",
    )


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        navbar(),
        rx.vstack(
            rx.heading("Welcome to the Code Lyoko Discord!", size="8"),
            rx.link(
                rx.button("Check out our server!"),
                href="https://discord.gg/jqppQx6n",
                is_external=True,
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
    )


def rules() -> rx.Component:
    # Rules Page
    return rx.container(
        navbar(),
        rx.vstack(
            rx.heading("Rules", size="8"),
            rx.heading("Report all spam and unsolicited DMs to a moderator", size="6"),
            rx.text("If you get a spam message or any other unwanted message from a user in this server, please message a 🛡️Modérateur right away. And do not click any unsolicited links sent to you via direct message."),
            rx.heading("Use channels for their intended purpose", size="6"),
            rx.text("Especially, keep political discussions confined to the dedicated politics channel. Brief, respectful political mentions elsewhere are acceptable, but extended debates should move to the ⁠📰Political Column channel."),
            rx.heading("Chill out & be respectful", size="6"),
            rx.markdown(
                r"""
                We pride ourselves on being a small, self-regulating community, with little moderator involvement required. (We'd rather use our `?warn` command as a joke rather than for real.) Help us maintain this atmosphere by using common sense and being considerate of others. To keep this vibe:
                * Be considerate of others’ opinions, feelings, and boundaries.
                * Avoid escalating disagreements into arguments.
                * Treat everyone with respect, regardless of their background, beliefs, or identity.
                """
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        )
    )


@rx.page(on_load=State.auth_redir())
def auth() -> rx.Component:
    return rx.container(
    )


@rx.page(on_load=State.process_callback())
def callback() -> rx.Component:
    return rx.container(
    )


@rx.page(on_load=State.get_user_roles())
def usercfg() -> rx.Component:
    return rx.container(
        navbar(),
        rx.cond(
            State.acct_auth_good,
            rx.vstack(
                rx.heading("User Settings", size="8"),
                rx.text(f"User: {State.acct_user}"),
                rx.heading("Your Current Color:", size="6"),
                rx.grid(
                    rx.foreach(State.curr_roles.keys(), draw_roles_box),
                ),
                rx.heading("Choose your new color:", size="6"),
                rx.grid(
                    rx.foreach(State.roles.keys(), draw_roles_buttons),
                ),

            ),
            rx.vstack(
                rx.heading("Access Denied.", size="8"),
                rx.text("You must be logged in to access this page."),
                rx.button("Login with Discord", on_click=State.auth_redir)
            ),
        ),
        spacing="5",
        justify="center",
        min_height="85vh",
    )


app = rx.App()
app.add_page(index, title="Home")
app.add_page(rules, route="/rules", title="Rules")
app.add_page(auth, route="/auth")
app.add_page(callback, route="/callback")
app.add_page(usercfg, route="/usercfg", title="User Settings")
