from odoo import fields, models


class BookCategoryWizard(models.TransientModel):
    _name = "material.request.report.wizard"

    from_date = fields.Date(
        string='From',
        required=True
    )
    to_date = fields.Date(
        string='To',
        required=True
    )

    type = fields.Selection(
        string='Type',
        selection=[('excel', 'Excel'), ('pdf', 'PDF')],
        default='pdf'
    )

    def action_print(self):
        req = self.env['material.request'].search(
            [('request_date', '>=', self.from_date),
             ('request_date', '<=', self.to_date)])
        print(req)
