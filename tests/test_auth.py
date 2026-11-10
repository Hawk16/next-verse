"""Demo login checks using Flask's in-process test client."""

import unittest
import struct
import zlib

from app import server


class DemoLoginTests(unittest.TestCase):
    def setUp(self):
        server.config["TESTING"] = True
        self.client = server.test_client()

    def token(self):
        with self.client.session_transaction() as session:
            return session["csrf_token"]

    def sign_in(self):
        self.client.get("/")
        return self.client.post("/", data={"csrf_token": self.token()})

    def test_welcome_buttons_open_their_respective_pages(self):
        for action, destination in [("login", "/"), ("get-started", "/help")]:
            with self.subTest(action=action):
                client = server.test_client()
                client.get("/")
                with client.session_transaction() as session:
                    token = session["csrf_token"]
                response = client.post("/", data={"csrf_token": token, "action": action})
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.location, destination)
                self.assertEqual(client.get(destination).status_code, 200)
                self.assertEqual(client.get("/_dash-layout").status_code, 200)

    def test_home_has_button_without_credential_fields(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b">Log in</button>", response.data)
        self.assertIn(b'value="get-started">Get Started</button>', response.data)
        self.assertNotIn(b'name="username"', response.data)
        self.assertNotIn(b'name="password"', response.data)
        self.assertIn(b'class="welcome-page"', response.data)
        self.assertIn(b"<h1>Welcome to your next verse</h1>", response.data)
        self.assertIn(b"Your finances. Shared support. Your choice.", response.data)
        self.assertIn(b'class="visually-hidden"', response.data)
        self.assertNotIn(b'class="welcome-message"', response.data)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        with self.client.get("/assets/style.css") as stylesheet:
            self.assertEqual(stylesheet.status_code, 200)

    def test_logo_is_available_before_login(self):
        with self.client.get("/assets/next-verse.png") as response:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, "image/png")
            data = response.data
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            width, height, depth, color, _, _, _ = struct.unpack(">IIBBBBB", data[16:29])
            self.assertEqual((depth, color), (8, 6))
            compressed = b""
            pos = 8
            while pos < len(data):
                length = struct.unpack(">I", data[pos:pos + 4])[0]
                if data[pos + 4:pos + 8] == b"IDAT":
                    compressed += data[pos + 8:pos + 8 + length]
                pos += length + 12
            raw = zlib.decompress(compressed)
            alphas = []
            for y in range(height):
                start = y * (width * 4 + 1)
                self.assertEqual(raw[start], 0)
                alphas.extend(raw[start + 4:start + 1 + width * 4:4])
            self.assertEqual(alphas[0], 0)
            self.assertIn(255, alphas)
            self.assertGreater(alphas.count(0) / len(alphas), 0.5)

    def test_welcome_photo_is_available_before_login(self):
        response = self.client.get("/")
        self.assertIn(b'src="/assets/welcome-photo.png"', response.data)
        self.assertIn(b'class="welcome-logo"', response.data)
        with self.client.get("/assets/welcome-photo.png") as photo:
            self.assertEqual(photo.status_code, 200)
            self.assertEqual(photo.mimetype, "image/png")
            self.assertEqual(photo.data[:8], b"\x89PNG\r\n\x1a\n")

    def test_pages_and_dash_endpoints_wait_for_demo_login(self):
        self.assertEqual(self.client.get("/resources").location, "/")
        self.assertEqual(self.client.get("/help").location, "/")
        self.assertEqual(self.client.get("/who-are-you").location, "/")
        for path in ["/_dash-layout", "/_dash-dependencies"]:
            self.assertEqual(self.client.get(path).status_code, 401)
        self.assertEqual(
            self.client.post("/_dash-update-component", json={}).status_code, 401
        )

    def test_shared_footer_includes_logo_only_on_dashboard_pages(self):
        from app import dashboard_layout
        from pages.overview import layout

        footer = dashboard_layout().children[-1]
        self.assertEqual(footer.to_plotly_json()["type"], "Footer")
        logo = footer.children[0]
        self.assertEqual(
            footer.children[1].children, "Navigate what comes next, together"
        )
        self.assertEqual(logo.to_plotly_json()["type"], "Img")
        self.assertEqual(logo.src, "/assets/next-verse.png")
        self.assertEqual(logo.alt, "Next Verse")
        self.assertFalse(any(child.to_plotly_json()["type"] == "Img" for child in layout.children))
        welcome = self.client.get("/")
        self.assertNotIn(b'<footer class="site-footer">', welcome.data)
        self.assertNotIn(b'class="footer-logo"', welcome.data)
        self.sign_in()
        self.assertIn(b"footer-logo", self.client.get("/_dash-layout").data)
        with self.client.get(logo.src) as response:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, "image/png")

    def test_login_retains_form_token_validation(self):
        self.assertEqual(self.client.post("/", data={}).status_code, 400)
        self.client.get("/")
        response = self.client.post("/", data={"csrf_token": "\N{SNOWMAN}"})
        self.assertEqual(response.status_code, 400)

    def test_home_lists_contact_names_titles_and_roles(self):
        from pages.overview import CONTACTS, layout

        table = layout.children[2].children
        self.assertEqual(table.id, "contacts-table")
        headings = table.children[1].children.children
        self.assertEqual(
            [heading.children for heading in headings],
            ["Name", "Title", "Role", "Connect", "Video call"],
        )
        rows = table.children[2].children
        self.assertEqual(len(rows), len(CONTACTS))
        self.assertEqual(
            [cell.children for cell in rows[0].children[:3]],
            ["Mr. Jones", "Attorney", "Power of Attorney"],
        )
        for index, (row, contact) in enumerate(zip(rows, CONTACTS)):
            self.assertEqual(
                [cell.children for cell in row.children[:3]],
                [contact["name"], contact["title"], contact["role"]],
            )
            button = row.children[3].children
            self.assertEqual(button.children, "Connect")
            self.assertEqual(button.id, {"type": "connect-contact", "index": index})
            video = row.children[4].children
            self.assertEqual(video.id, {"type": "video-contact", "index": index})
            self.assertEqual(video.children[1], "Video call")
            self.assertEqual(video.children[0].className, "video-icon")
        self.sign_in()
        dependencies = self.client.get("/_dash-dependencies").get_json()
        self.assertNotIn("category-chart.figure", [item["output"] for item in dependencies])
        response = self.client.get("/_dash-layout")
        self.assertNotIn(b"Your next verse", response.data)
        self.assertNotIn(b"Sales dashboard", response.data)

    def test_connect_buttons_select_each_contact_without_sending_a_message(self):
        import json
        from pages.overview import CONTACTS

        self.sign_in()
        pattern = '{"index":["ALL"],"type":"connect-contact"}'
        for index, contact in enumerate(CONTACTS):
            button_id = json.dumps(
                {"index": index, "type": "connect-contact"}, separators=(",", ":")
            )
            response = self.client.post(
                "/_dash-update-component",
                json={
                    "output": "connect-status.children",
                    "outputs": {"id": "connect-status", "property": "children"},
                    "inputs": [
                        {
                            "id": pattern,
                            "property": "n_clicks",
                            "value": [1 if i == index else 0 for i in range(len(CONTACTS))],
                        }
                    ],
                    "state": [{"id": "contacts-data", "property": "data", "value": CONTACTS}],
                    "changedPropIds": [f"{button_id}.n_clicks"],
                },
            )
            self.assertEqual(response.status_code, 200)
            card = response.get_json()["response"]["connect-status"]["children"]
            children = card["props"]["children"]
            self.assertEqual(children[1]["props"]["children"], contact["name"])
            self.assertEqual(children[2]["props"]["children"], contact["title"])
            self.assertEqual(
                children[4]["props"]["children"][1]["props"]["children"], contact["role"]
            )
            details = children[4]["props"]["children"]
            for offset, (label, key) in enumerate([
                ("Role", "role"),
                ("Phone", "phone"),
                ("Email", "email"),
                ("Organization", "organization"),
                ("Address", "address"),
                ("Availability", "availability"),
            ]):
                self.assertEqual(details[offset * 2]["props"]["children"], label)
                self.assertEqual(details[offset * 2 + 1]["props"]["children"], contact[key])
            self.assertTrue(contact["email"].endswith("@example.com"))
            self.assertRegex(contact["phone"], r"^\(202\) 555-01\d{2}$")
            self.assertEqual(
                children[5]["props"]["children"],
                "Demo only: no message was sent.",
            )

    def test_contact_modal_has_native_close_and_accessible_label(self):
        from pages.overview import layout

        modal = layout.children[3]
        self.assertEqual(modal.to_plotly_json()["type"], "Dialog")
        self.assertEqual(modal.id, "contact-modal")
        self.assertEqual(modal.to_plotly_json()["props"]["aria-labelledby"], "contact-card-name")
        self.assertEqual(modal.children[1].method, "dialog")
        self.assertEqual(modal.children[1].children.children, "Close")

    def test_video_action_has_inline_status_without_modal(self):
        from pages.overview import layout

        ids = [getattr(child, "id", None) for child in layout.children]
        self.assertNotIn("video-modal", ids)
        self.assertNotIn("video-modal-state", ids)
        status = next(child for child in layout.children if getattr(child, "id", None) == "video-status")
        self.assertEqual(status.to_plotly_json()["type"], "P")
        self.assertEqual(status.role, "status")

    def test_video_call_selects_each_contact_including_added_contacts(self):
        import json
        from pages.overview import CONTACTS

        contacts = CONTACTS + [{**CONTACTS[0], "name": "Ms. Smith"}]
        self.sign_in()
        for index, contact in enumerate(contacts):
            button_id = json.dumps(
                {"index": index, "type": "video-contact"}, separators=(",", ":")
            )
            response = self.client.post(
                "/_dash-update-component",
                json={
                    "output": "video-status.children",
                    "outputs": {"id": "video-status", "property": "children"},
                    "inputs": [{
                        "id": '{"index":["ALL"],"type":"video-contact"}',
                        "property": "n_clicks",
                        "value": [int(i == index) for i in range(len(contacts))],
                    }],
                    "state": [{"id": "contacts-data", "property": "data", "value": contacts}],
                    "changedPropIds": [f"{button_id}.n_clicks"],
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.get_json()["response"]["video-status"]["children"],
                f"Video call with {contact['name']}: demo only, no call was started.",
            )

    def test_add_contact_validates_and_updates_rows(self):
        from dash import no_update
        from pages.overview import CONTACTS, contact_rows, save_contact

        values = [" Ms. Smith ", "Attorney", "Power of Attorney", "", "smith@example.com", "", "", ""]
        result = save_contact(1, CONTACTS, *values)
        contacts = result[0]
        self.assertEqual(len(contacts), len(CONTACTS) + 1)
        self.assertEqual(contacts[-1]["name"], "Ms. Smith")
        self.assertEqual(len(CONTACTS), 4)
        self.assertEqual(result[1], "")
        self.assertEqual(result[3:], ("",) * 8)
        row = contact_rows(contacts)[-1]
        self.assertEqual(row.children[3].children.id["index"], 4)
        for invalid_values, expected in [
            ([""] * 8, "Please enter: Name, Title, Role."),
            (values[:4] + ["invalid-email"] + values[5:], "valid email"),
        ]:
            invalid = save_contact(1, CONTACTS, *invalid_values)
            self.assertIs(invalid[0], no_update)
            self.assertIn(expected, invalid[1])

    def test_contacts_store_persists_locally(self):
        from pages.overview import layout

        store = layout.children[5]
        self.assertEqual(store.id, "contacts-data")
        self.assertEqual(store.storage_type, "local")

    def test_add_contact_callback_updates_browser_store(self):
        from app import app
        from pages.overview import CONTACTS, FIELDS

        self.sign_in()
        output = next(key for key in app.callback_map if "contacts-data.data" in key)
        outputs = [
            {"id": "contacts-data", "property": "data"},
            {"id": "add-contact-error", "property": "children"},
            {"id": "add-contact-success", "property": "children"},
        ] + [{"id": f"contact-{key}", "property": "value"} for _, key, _ in FIELDS]
        values = ["Ms. Smith", "Attorney", "Trusted Contact", "", "", "", "", ""]
        response = self.client.post(
            "/_dash-update-component",
            json={
                "output": output,
                "outputs": outputs,
                "inputs": [{"id": "save-contact", "property": "n_clicks", "value": 1}],
                "state": [
                    {"id": "contacts-data", "property": "data", "value": CONTACTS}
                ] + [
                    {"id": f"contact-{key}", "property": "value", "value": value}
                    for (_, key, _), value in zip(FIELDS, values)
                ],
                "changedPropIds": ["save-contact.n_clicks"],
            },
        )
        self.assertEqual(response.status_code, 200)
        contacts = response.get_json()["response"]["contacts-data"]["data"]
        self.assertEqual(contacts[-1]["name"], "Ms. Smith")
        self.assertEqual(len(contacts), 5)

    def test_click_login_opens_both_pages_without_credentials(self):
        response = self.sign_in()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/")
        for path in ["/", "/resources", "/help", "/who-are-you", "/_dash-layout", "/_dash-dependencies"]:
            self.assertEqual(self.client.get(path).status_code, 200)

    def test_who_are_you_page_has_all_seven_roles(self):
        from pages.who_are_you import layout

        self.assertEqual(layout.children[0].children, "Who are you?")
        selector = layout.children[2]
        self.assertEqual(
            [option["label"] for option in selector.options],
            ["Individual seeking help", "Family Member", "Friend",
             "Healthcare provider", "Attorney", "Accountant", "Other"],
        )
        self.assertEqual(len({option["value"] for option in selector.options}), 7)
        self.assertIsNone(selector.value)
        self.assertTrue(selector.persistence)
        self.assertEqual(selector.persistence_type, "session")

    def test_help_menu_options_provide_guidance_and_resources_link(self):
        from pages.help import OPTIONS, layout

        self.assertEqual(len(layout.children[2].options), 5)
        self.sign_in()
        for key, label, steps in OPTIONS:
            response = self.client.post(
                "/_dash-update-component",
                json={
                    "output": "help-guidance.children",
                    "outputs": {"id": "help-guidance", "property": "children"},
                    "inputs": [{"id": "help-choice", "property": "value", "value": key}],
                    "state": [],
                    "changedPropIds": ["help-choice.value"],
                },
            )
            self.assertEqual(response.status_code, 200)
            children = response.get_json()["response"]["help-guidance"]["children"]["props"]["children"]
            self.assertEqual(children[0]["props"]["children"], label)
            self.assertEqual(
                [item["props"]["children"] for item in children[1]["props"]["children"]],
                steps,
            )
            links = children[2]["props"]["children"]
            self.assertEqual(links[0]["props"]["href"], "/resources")
            self.assertEqual(links[1]["props"]["href"], "/who-are-you")
            self.assertEqual(links[1]["props"]["children"], "Who are you?")

    def test_resources_table_contains_all_seven_categories(self):
        from pages.resources import layout

        table = layout.children[2].children
        self.assertEqual(table.id, "resources-table")
        rows = table.children[2].children
        self.assertEqual(
            [row.children[1].children[1].children for row in rows],
            ["Caregiver support", "Government Benefits", "Community Programs",
             "Transportation", "Meal programs", "Financial Planning", "Estate Planning"],
        )
        self.assertEqual([row.children[0].children for row in rows], [1, 2, 3, 4, 5, 6, 7])
        self.assertTrue(all(row.children[2].children for row in rows))
        from pages.resources import RESOURCE_ICONS

        self.assertEqual(
            [row.children[1].children[0].children for row in rows], RESOURCE_ICONS
        )
        self.assertEqual(len(set(RESOURCE_ICONS)), 7)
        self.assertTrue(all(
            row.children[1].children[0].to_plotly_json()["props"]["aria-hidden"] == "true"
            for row in rows
        ))
        self.sign_in()
        self.assertEqual(self.client.get("/trends").location, "/resources")
        dependencies = self.client.get("/_dash-dependencies").get_json()
        self.assertNotIn("trend-chart.figure", [item["output"] for item in dependencies])

    def test_explore_opens_relevant_mock_resource_details(self):
        import json
        from pages.resources import MOCK_PROGRAMS, RESOURCES, layout

        rows = layout.children[2].children.children[2].children
        modal = layout.children[3]
        self.assertEqual(modal.to_plotly_json()["type"], "Dialog")
        self.assertEqual(modal.children[1].method, "dialog")
        self.sign_in()
        for index, program in enumerate(MOCK_PROGRAMS):
            button = rows[index].children[3].children
            self.assertEqual(button.children, "Explore")
            self.assertEqual(button.id, {"type": "explore-resource", "index": index})
            button_id = json.dumps(
                {"index": index, "type": "explore-resource"}, separators=(",", ":")
            )
            response = self.client.post(
                "/_dash-update-component",
                json={
                    "output": "resource-details.children",
                    "outputs": {"id": "resource-details", "property": "children"},
                    "inputs": [{
                        "id": '{"index":["ALL"],"type":"explore-resource"}',
                        "property": "n_clicks",
                        "value": [int(i == index) for i in range(len(RESOURCES))],
                    }],
                    "state": [],
                    "changedPropIds": [f"{button_id}.n_clicks"],
                },
            )
            self.assertEqual(response.status_code, 200)
            children = response.get_json()["response"]["resource-details"]["children"]["props"]["children"]
            self.assertEqual(children[0]["props"]["children"], RESOURCES[index][0])
            self.assertIn("fictional", children[1]["props"]["children"])
            self.assertEqual(children[2]["props"]["children"], program["name"])
            details = children[3]["props"]["children"]
            for offset, key in enumerate(["services", "eligibility", "schedule", "cost", "phone", "email"]):
                self.assertEqual(details[offset * 2 + 1]["props"]["children"], program[key])

    def test_logout_returns_to_welcome_screen(self):
        self.sign_in()
        self.assertEqual(self.client.post("/logout").status_code, 400)
        self.assertEqual(self.client.get("/_dash-layout").status_code, 200)
        response = self.client.post("/logout", data={"csrf_token": self.token()})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get("/_dash-layout").status_code, 401)
        self.assertIn(b">Log in</button>", self.client.get("/").data)

    def test_financial_checklist_is_removed(self):
        from dash import page_registry
        from app import dashboard_layout

        self.assertNotIn("/checklist", [page["path"] for page in page_registry.values()])
        navigation = dashboard_layout().children[0].children[0]
        self.assertNotIn("/checklist", [link.href for link in navigation.children])

    def test_planning_pages_have_simple_bulleted_suggestions(self):
        from pages.financial_checklist import layout as financial
        from pages.estate_planning_checklist import layout as estate

        for path, title, layout in [
            ("/financial-checklist", "Financial Checklist", financial),
            ("/estate-planning-checklist", "Estate Planning Checklist", estate),
        ]:
            with self.subTest(path=path):
                client = server.test_client()
                self.assertEqual(client.get(path).location, "/")
                self.assertEqual(layout.children[0].children, title)
                bullets = layout.children[2]
                self.assertEqual(bullets.to_plotly_json()["type"], "Ul")
                self.assertEqual(len(bullets.children), 12)
                self.assertTrue(all(item.to_plotly_json()["type"] == "Li" for item in bullets.children))
                self.assertEqual(layout.children[-1].href, "/resources")
                client.get("/")
                with client.session_transaction() as session:
                    token = session["csrf_token"]
                client.post("/", data={"csrf_token": token})
                self.assertEqual(client.get(path).status_code, 200)

    def test_elder_abuse_page_is_navigable_and_has_prevention_guidance(self):
        from dash import page_registry
        from app import dashboard_layout
        from pages.elder_abuse import TIPS, layout

        self.assertIn("/elder-abuse", [page["path"] for page in page_registry.values()])
        navigation = dashboard_layout().children[0].children[0]
        self.assertIn("/elder-abuse", [link.href for link in navigation.children])
        self.assertEqual(layout.children[0].children, "Preventing Elder Abuse")
        self.assertEqual(len(layout.children[2].children), len(TIPS))
        self.assertTrue(any("financial" in tip.lower() for tip in TIPS))
        self.assertTrue(any("immediate danger" in tip.lower() for tip in TIPS))

        client = server.test_client()
        self.assertEqual(client.get("/elder-abuse").location, "/")
        client.get("/")
        with client.session_transaction() as session:
            token = session["csrf_token"]
        client.post("/", data={"csrf_token": token})
        self.assertEqual(client.get("/elder-abuse").status_code, 200)

    def test_scams_page_is_navigable_and_has_prevention_guidance(self):
        from dash import page_registry
        from app import dashboard_layout
        from pages.scams import TIPS, layout

        self.assertIn("/scams", [page["path"] for page in page_registry.values()])
        navigation = dashboard_layout().children[0].children[0]
        self.assertIn("/scams", [link.href for link in navigation.children])
        self.assertEqual(layout.children[0].children, "Tips for Avoiding Scams")
        self.assertEqual(len(layout.children[2].children), len(TIPS))
        self.assertTrue(any("verification codes" in tip for tip in TIPS))
        self.assertTrue(any("financial institution" in tip for tip in TIPS))

        client = server.test_client()
        self.assertEqual(client.get("/scams").location, "/")
        client.get("/")
        with client.session_transaction() as session:
            token = session["csrf_token"]
        client.post("/", data={"csrf_token": token})
        self.assertEqual(client.get("/scams").status_code, 200)


if __name__ == "__main__":
    unittest.main()
