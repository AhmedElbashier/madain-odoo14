
from odoo import api, fields, models

class budget_line(models.Model):
	_inherit = 'crossovered.budget.lines'


	balance_amount = fields.Monetary(
		compute='_compute_balance_amount', string='Balance Amount', help="Amount really earned/spent.")
	

	@api.multi
	def _compute_balance_amount(self):
		for line in self:
			line.balance_amount = line.planned_amount - line.practical_amount