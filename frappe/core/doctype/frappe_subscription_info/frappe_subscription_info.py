# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class FrappeSubscriptionInfo(Document):
	pass
	# def validate(self):
	# 	if not self.flags.save_subscription:
	# 		frappe.throw(_('You are not allowed to edit Frappe Subscription'))


