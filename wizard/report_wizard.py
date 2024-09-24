from odoo import fields, models, api


class PrintWizard(models.TransientModel):
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

    def action_print_pdf(self, data):
        return self.env.ref('material_request.pdf_report_action_button').report_action(self, data=data)

    def action_print_excel(self, data):
        return self.env.ref('material_request.excel_report_action').report_action(self, data=data)

    def action_print(self):
        material_requests = self.env['material.request'].search_read([
            ('request_date', '>=', self.from_date),
            ('request_date', '<=', self.to_date)
        ], ['ref', 'request_date', 'department_id', 'vendor_id', 'material_request_line_ids'])
        material_request_data = []

        for request in material_requests:
            lines = self.env['material.request.line'].browse(request['material_request_line_ids']).read(['product_id', 'quantity'])

            material_request_data.append({
                'ref': request['ref'],
                'request_date': request['request_date'],
                'department_id': request['department_id'][1] if request['department_id'] else '',
                'vendor_id': request['vendor_id'][1] if request['vendor_id'] else '',
                'material_request_line_ids': lines,
            })

        data = {
            'material_request': material_request_data,
        }

        if (self.type == 'pdf'):
            return self.action_print_pdf(data)
        else:
            return self.action_print_excel(data)
