from __future__ import unicode_literals
import frappe
import subprocess, os
from frappe.model.document import Document
from frappe.core.doctype.user.user import get_total_users
from frappe.utils import flt, cint, now_datetime, getdate, get_site_path
from frappe.utils.file_manager import MaxFileSizeReachedError
from frappe.utils.data import formatdate
from frappe import _

class SiteExpiredError(frappe.ValidationError):
	pass


def has_expired():
	if not frappe.conf.get("stop_on_expiry") or frappe.session.user=="Administrator":
		return False

	expires_on = get_limits().get("expires_on")
	if not expires_on:
		return False

	if now_datetime().date() <= getdate(expires_on):
		return False

	return True

def check_if_expired():
	"""check if account is expired. If expired, do not allow login"""
	if not has_expired():
		return
	# if expired, stop user from logging in
	expires_on = formatdate(get_limits().get("expires_on"))
	
	frappe.throw("""Your subscription expired on <b>{}</b>.
		To extend please drop a mail at <b>support@erpnext.com</b>""".format(expires_on),
		SiteExpiredError)

@frappe.whitelist()
def get_limits():
	return frappe.get_conf().get("limits")


def set_limits(limits):
	from frappe.installer import update_site_config

	if not limits:
		#Remove 'limits' key
		frappe_limits = "None"
	else:
		# Add/Update current config options in site_config
		frappe_limits = get_limits() or {}
		for key in limits.keys():
			if key in frappe_limits:
				if limits[key] == "None":
					del frappe_limits[key]
			else:
				frappe_limits[key] = limits[key]

	update_site_config("limits", frappe_limits, validate=False)
