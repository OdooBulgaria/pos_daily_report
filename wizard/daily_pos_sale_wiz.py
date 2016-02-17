from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime ,timedelta
from dateutil.relativedelta import relativedelta
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import base64
import tempfile

class daily_pos_sale_wiz_view(osv.osv_memory):
	_name = 'daily.pos.sale.wiz.view'
	_columns= {
        'date_from': fields.datetime('From Date'),
        'date_to': fields.datetime('To Date'),
    }

	def download_sale_report_txt_file(self, cr, uid, ids, context):
		if context is None:
			context = {}
		data = self.read(cr, uid, ids, [])[0]
		context.update({'datas': data})
		return {
			'name': _('Sale Report'),
			'view_type': 'form',
			"view_mode": 'form',
			'res_model': 'binary.sale.report.text.file.wizard',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': context,
		}
daily_pos_sale_wiz_view()
class binary_sale_report_text_file_wizard(osv.osv_memory):
    _name = 'binary.sale.report.text.file.wizard'

    def _generate_sale_report_file(self, cr, uid, context=None):
        if context is None:
            context = {}
        # employee_obj = self.pool.get('hr.employee')
        # payslip_obj = self.pool.get('hr.payslip')
        # period_data = self.pool.get('account.period').browse(cr, uid, context.get('datas')['period_id'][0], context=context)
        # start_date = period_data.date_start
        # end_date = period_data.date_stop
        # emp_ids = employee_obj.search(cr, uid, [('bank_account_id', '!=', False)], order="name", context = context)
        # print"emp_ids::::::::",emp_ids,start_date,end_date
        # payslip_ids = payslip_obj.search(cr, uid, [('employee_id', 'in', emp_ids), ('cheque_number','=',False), ('date_from', '>=', start_date), ('date_from', '<=', end_date), ('state', 'in', ['draft', 'done', 'verify'])], order="employee_name")
        # print"payslip_ids::::::::::",payslip_ids
        # if not payslip_ids:
        #     raise osv.except_osv(_('Error'), _('There is no payslip found to generate text file.'))
        tgz_tmp_filename = tempfile.mktemp('.' + "txt")
        tmp_file = False
        try:
            tmp_file = open(tgz_tmp_filename, "wr")
            net_amount_total=0.0
            detail_record = 'Deatil Report sdfhsjfhsdjfhj'
            
            # tmp_file.write(header_record)
            tmp_file.write(detail_record)
        finally:
            if tmp_file:
                tmp_file.close()
        file = open(tgz_tmp_filename, "rb")
        out = file.read()
        file.close()
        return base64.b64encode(out)

    _columns = {
        'name': fields.char('Name', size=64),
        'sale_report_txt_file': fields.binary('Click On Download Link To Download File', readonly=True),
    }

    _defaults = {
         'name': 'Sale Report.txt',
         'sale_report_txt_file': _generate_sale_report_file,
    }

binary_sale_report_text_file_wizard()