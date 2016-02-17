from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime ,timedelta
from dateutil.relativedelta import relativedelta
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import base64
import tempfile
import math

class daily_pos_sale_wiz_view(osv.osv_memory):
	_name = 'daily.pos.sale.wiz.view'
	_columns= {
        'date_from': fields.date('From Date'),
        'date_to': fields.date('To Date'),
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
        print context
        print context.get('datas')
        DATETIME_FORMAT = "%Y-%m-%d"
        pos_order_obj = self.pool.get('pos.order')
        start_date = context.get('datas')['date_from']
        end_date = context.get('datas')['date_to']

        start_date = datetime.strptime(start_date, DATETIME_FORMAT)
        end_date = datetime.strptime(end_date, DATETIME_FORMAT)

        from_date = datetime.strptime((start_date.strftime('%Y-%m-%d')),"%Y-%m-%d").date()
        to_date = datetime.strptime((end_date.strftime('%Y-%m-%d')),"%Y-%m-%d").date()
        
        time_diff = to_date - from_date
        diff_day = time_diff.days + (float(time_diff.seconds) / 86400)
        diff_day = round(math.ceil(diff_day))

        tgz_tmp_filename = tempfile.mktemp('.' + "txt")
        tmp_file = False
        try:
            tmp_file = open(tgz_tmp_filename, "wr")
            net_amount_total=0.0
            detail_record = ''
            next_date = from_date
            for day in range(0, int(diff_day)):
                detail_record = detail_record  + str(next_date) + '\n'
                next_hr = next_date
                time =   datetime.strftime(next_date,'%Y-%m-%d %H:%M:%S')
                time = datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
                for hour in range(0,24):
                    print "time",time
                    detail_record = detail_record + '\t' + str(time) + '\n'
                    time += timedelta(hours=1)
                next_date +=  timedelta(days=1)
            
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