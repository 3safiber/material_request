from odoo import models


class PartnerXlsx(models.AbstractModel):
    _name = 'report.material_request.excel_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, material_requests):
        card_format = workbook.add_format({
            'border': 1,
            'border_color': '#000000',
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#f0f0f0',
            'font_size': 12
        })
        product_header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'bg_color': '#d9e1d0',
            'border_color': '#000000',
            'font_size': 18,
        })
        product_sub_header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#d9e1f2',
            'border_color': '#000000',
            'font_size': 16,
        })

        for rec in data['material_request']:
            sheet = workbook.add_worksheet(rec['ref'])
            row = 1
            sheet.merge_range(row, 1, row, 2, f"Material Request: {rec['ref']}", product_header_format)

            # Request Details
            row += 1
            sheet.write(row, 1, "Request Date:", product_sub_header_format)
            sheet.write(row, 2, rec['request_date'], card_format)

            row += 1
            sheet.write(row, 1, "Department:", product_sub_header_format)
            sheet.write(row, 2, rec['department_id'] or 'N/A', card_format)

            row += 1
            sheet.write(row, 1, "Vendor:", product_sub_header_format)
            sheet.write(row, 2, rec['vendor_id'] or 'N/A', card_format)

            row += 1
            row += 1
            sheet.merge_range(row, 1, row, 2, "Products:", product_header_format)
            row += 1
            # Product Table Header
            sheet.write(row, 1, "Products", product_sub_header_format)
            sheet.write(row, 2, "Quantity", product_sub_header_format)
            row += 1

            # Write product lines
            for line in rec['material_request_line_ids']:
                sheet.write(row, 1, line['product_id'][1], card_format)  # Product Name
                sheet.write(row, 2, line['quantity'], card_format)       # Quantity
                row += 1
            sheet.set_column(1, 1, 20)
            sheet.set_column(2, 2, 20)
