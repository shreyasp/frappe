# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import frappe, unittest

from frappe.model.delete_doc import delete_doc

test_records = frappe.get_test_records('User')

class TestUser(unittest.TestCase):
	def test_delete(self):
		frappe.get_doc("User", "test@example.com").add_roles("_Test Role 2")
		self.assertRaises(frappe.LinkExistsError, delete_doc, "Role", "_Test Role 2")
		frappe.db.sql("""delete from tabUserRole where role='_Test Role 2'""")
		delete_doc("Role","_Test Role 2")

		if frappe.db.exists("User", "_test@example.com"):
			delete_doc("User", "_test@example.com")

		user = frappe.copy_doc(test_records[1])
		user.email = "_test@example.com"
		user.insert()

		frappe.get_doc({"doctype": "ToDo", "description": "_Test"}).insert()

		delete_doc("User", "_test@example.com")

		self.assertTrue(not frappe.db.sql("""select * from `tabToDo` where owner=%s""",
			("_test@example.com",)))

		from frappe.core.doctype.role.test_role import test_records as role_records
		frappe.copy_doc(role_records[1]).insert()

	def test_get_value(self):
		self.assertEquals(frappe.db.get_value("User", "test@example.com"), "test@example.com")
		self.assertEquals(frappe.db.get_value("User", {"email":"test@example.com"}), "test@example.com")
		self.assertEquals(frappe.db.get_value("User", {"email":"test@example.com"}, "email"), "test@example.com")
		self.assertEquals(frappe.db.get_value("User", {"email":"test@example.com"}, ["first_name", "email"]),
			("_Test", "test@example.com"))
		self.assertEquals(frappe.db.get_value("User",
			{"email":"test@example.com", "first_name": "_Test"},
			["first_name", "email"]),
				("_Test", "test@example.com"))

		test_user = frappe.db.sql("select * from tabUser where name='test@example.com'",
			as_dict=True)[0]
		self.assertEquals(frappe.db.get_value("User", {"email":"test@example.com"}, "*", as_dict=True),
			test_user)

		self.assertEquals(frappe.db.get_value("User", "xxxtest@example.com"), None)

		frappe.db.set_value("Website Settings", "Website Settings", "_test", "_test_val")
		self.assertEquals(frappe.db.get_value("Website Settings", None, "_test"), "_test_val")
		self.assertEquals(frappe.db.get_value("Website Settings", "Website Settings", "_test"), "_test_val")

	def test_high_permlevel_validations(self):
		user = frappe.get_meta("User")
		self.assertTrue("user_roles" in [d.fieldname for d in user.get_high_permlevel_fields()])

		me = frappe.get_doc("User", "testperm@example.com")
		me.remove_roles("System Manager")

		frappe.set_user("testperm@example.com")

		me = frappe.get_doc("User", "testperm@example.com")
		self.assertRaises(frappe.PermissionError, me.add_roles, "System Manager")

		frappe.set_user("Administrator")

		me = frappe.get_doc("User", "testperm@example.com")
		me.add_roles("System Manager")

		self.assertTrue("System Manager" in [d.role for d in me.get("user_roles")])

	def test_max_users_for_site(self):
		from frappe.limits import set_limits
		from frappe.core.doctype.user.user import get_total_users

		set_limits({'max_users': get_total_users()})

		# reload site config
		from frappe import _dict
		frappe.local.conf = _dict(frappe.get_site_config())

		# Create a new user
		user = frappe.new_doc('User')
		user.email = 'test_max_users@example.com'
		user.first_name = 'Test_max_user'

		self.assertRaises(frappe.utils.user.MaxUsersReachedError, user.add_roles, 'System Manager')

		if frappe.db.exists('User', 'test_max_users@example.com'):
			frappe.delete_doc('User', 'test_max_users@example.com')

		# Clear the site config
		set_limits(None)
