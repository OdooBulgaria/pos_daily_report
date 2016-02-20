from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime ,timedelta
from dateutil.relativedelta import relativedelta
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import base64
import tempfile
import math
import time
import pysftp
import os.path

class daily_pos_sale_wiz_view(osv.osv_memory):
	_name = 'daily.pos.sale.wiz.view'
	_columns= {
        'date': fields.date('Date'),
        'config_id' : fields.many2one('pos.config', 'Point of Sale')
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

    def pos_daily_report_cron(self, cr, uid, context=None):
        pos_order_obj = self.pool.get('pos.order')
        pos_order_line = self.pool.get('pos.order.line')

        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        current_date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        date = datetime.strptime(current_date, '%Y-%m-%d')
        date = date - timedelta(days=1)
        date_prev = date - timedelta(days=1)
        date = datetime.strptime((date.strftime('%Y-%m-%d')),"%Y-%m-%d").date()
        tgz_tmp_filename = tempfile.mktemp('.' + "txt")
        tmp_file = False
        try:
            tmp_file = open(tgz_tmp_filename, "wr")
            net_amount_total=0.0
            detail_record = ''
            next_date = date
            prev_date = date_prev
            for day in range(0, int(1)):
                next_hr = next_date
                time_new =   datetime.strftime(next_date,'%Y-%m-%d %H:%M:%S')
                time_new = datetime.strptime(time_new,'%Y-%m-%d %H:%M:%S')
                time_prev =   datetime.strftime(prev_date,'%Y-%m-%d %H:%M:%S')
                time_prev = datetime.strptime(time_prev,'%Y-%m-%d %H:%M:%S')
                for hour in range(0,24):
                    pos_order_ids = []
                    recipt_count = 0
                    gto_sale = 0
                    amount_gst=0
                    amount_discount = 0
                    service_charge = 0
                    number_of_pax = 0
                    cash_amount = 0.0
                    nets_amount = 0.0
                    chque_amount = 0.0
                    visa_amount = 0.0
                    mastercard_amount = 0.0
                    amax_amount = 0.0
                    voucher_amount = 0.0
                    other_amount = 0.0
                    gst = 0.0
                    batch_id = 0
                    time_from = time_new - timedelta(hours=5,minutes=30)
                    time_to = time_new - timedelta(hours=4,minutes=30)

                    time_from_prev = time_prev - timedelta(hours=5,minutes=30)
                    time_to_prev = time_prev - timedelta(hours=4,minutes=30)

                    time_from = datetime.strptime(str(time_from),'%Y-%m-%d %H:%M:%S')
                    time_to = datetime.strptime(str(time_to),'%Y-%m-%d %H:%M:%S')

                    time_from_prev = datetime.strptime(str(time_from_prev),'%Y-%m-%d %H:%M:%S')
                    time_to_prev = datetime.strptime(str(time_to_prev),'%Y-%m-%d %H:%M:%S')

                    last_order_id = pos_order_obj.search(cr,uid,[('create_date','>',str(time_from_prev)),('create_date','<',str(time_to_prev))])
                    print last_order_id
                    if last_order_id: 
                        last_batch_id = pos_order_obj.browse(cr,uid,last_order_id[0]).batch_id
                    else:
                        last_batch_id = 0
                    new_batch_id = last_batch_id + 1
                    batch_id = new_batch_id
                    print "time",time_from,time_to,time_from_prev,time_to_prev
                    
                    pos_order_ids = pos_order_obj.search(cr,uid,[('create_date','>',str(time_from)),('create_date','<',str(time_to))])

                    # batch_id = pos_order_obj.write(cr,uid,pos_order_ids,{'batch_id':})
                    if pos_order_ids:
                        for each in pos_order_obj.browse(cr,uid,pos_order_ids):
                            self.pool.get('pos.order').write(cr,uid,each.id,{'batch_id':batch_id})
                            recipt_count +=1
                            amount_gst += each.amount_tax
                            gst += each.amount_total
                            line_sale = 0.0
                            line_subtotal = 0.0
                            line_discount=0.0
                            for line in each.lines:
                                line_sale += line.price_subtotal
                                line_subtotal +=  line.price_subtotal
                                line_discount += (line.qty*line.price_unit) - line.price_subtotal
                            gto_sale += line_sale
                            amount_discount += line_discount
                            for statement in each.statement_ids:
                                if statement.journal_id.name == 'Cash':
                                    cash_amount += statement.amount
                                if statement.journal_id.name == 'NETS':
                                    nets_amount += statement.amount
                                if statement.journal_id.name == 'CHQUE':
                                    chque_amount += statement.amount
                                if statement.journal_id.name == 'VISA':
                                    visa_amount += statement.amount
                                if statement.journal_id.name == 'MasterCard':
                                    mastercard_amount += statement.amount
                                if statement.journal_id.name == 'Amex':
                                    amax_amount += statement.amount
                                if statement.journal_id.name == 'Voucher':
                                    voucher_amount += statement.amount
                                if statement.journal_id.name == 'Other':
                                    other_amount += statement.amount
                        detail_record = detail_record  +'MachineID'+'|'+str(batch_id)+'|'+str(datetime.strftime(next_date, "%Y%m%d"))+'|'+str(hour)+'|'+str(recipt_count)+'|'+str(gto_sale)+'|'+str(amount_gst)+'|'+str(amount_discount)+'|'+str(service_charge)+'|'+str(number_of_pax)+'|'+str(cash_amount)+'|'+str(nets_amount)+'|'+str(visa_amount)+'|'+str(mastercard_amount)+'|'+str(amax_amount)+'|'+str(voucher_amount)+'|'+str(other_amount)+'|'+'N'+'\r\n'
                    else:
                        detail_record = detail_record  +'MachineID'+'|'+str(batch_id)+'|'+str(datetime.strftime(next_date, "%Y%m%d"))+'|'+str(hour)+'|'+str(recipt_count)+'|'+str(gto_sale)+'|'+str(amount_gst)+'|'+str(amount_discount)+'|'+str(service_charge)+'|'+str(number_of_pax)+'|'+str(cash_amount)+'|'+str(nets_amount)+'|'+str(visa_amount)+'|'+str(mastercard_amount)+'|'+str(amax_amount)+'|'+str(voucher_amount)+'|'+str(other_amount)+'|'+'N'+'\r\n'
                    time_new += timedelta(hours=1)
                    time_prev += timedelta(hours=1)
                next_date +=  timedelta(days=1)
            
            tmp_file.write(detail_record)
        finally:
            if tmp_file:
                tmp_file.close()
        file = open(tgz_tmp_filename, "rb")
        out = file.read()
        file.close()
        
        save_path = '/home/ubuntu'
        file_name = str(datetime.strftime(date, "%Y%m%d"))+'.txt'
        print file_name
        completeName = os.path.join(save_path,file_name)         
        file1 = open(completeName, "w")
        file1.write(out)
        file1.close()
        try:
            srv = pysftp.Connection('hostname', username='username', password='******')
            remotepath = '/'
            localpath = '/'+file_name
            srv.put(localpath, remotepath)  
            srv.close()
        except Exception, e:
            print str(e)
        return True
    def _generate_sale_report_file(self, cr, uid, context=None):
        if context is None:
            context = {}
        print context
        print context.get('datas')
        DATETIME_FORMAT = "%Y-%m-%d"
        pos_order_obj = self.pool.get('pos.order')
        pos_order_line = self.pool.get('pos.order.line')
        date = context.get('datas')['date']
        config_id = context.get('datas')['config_id']
        date = datetime.strptime(date, DATETIME_FORMAT)
        date = datetime.strptime((date.strftime('%Y-%m-%d')),"%Y-%m-%d").date()

        tgz_tmp_filename = tempfile.mktemp('.' + "txt")
        tmp_file = False
        try:
            tmp_file = open(tgz_tmp_filename, "wr")
            net_amount_total=0.0
            detail_record = ''
            next_date = date
            for day in range(0, int(1)):
                next_hr = next_date
                time =   datetime.strftime(next_date,'%Y-%m-%d %H:%M:%S')
                time = datetime.strptime(time,'%Y-%m-%d %H:%M:%S')

                time_prev =   datetime.strftime(next_date,'%Y-%m-%d %H:%M:%S')
                time_prev = datetime.strptime(time_prev,'%Y-%m-%d %H:%M:%S')
                time_prev = time_prev - timedelta(days=1)

                for hour in range(0,24):
                    pos_order_ids = []
                    recipt_count = 0
                    gto_sale = 0
                    amount_gst=0
                    amount_discount = 0
                    service_charge = 0
                    number_of_pax = 0
                    cash_amount = 0.0
                    nets_amount = 0.0
                    chque_amount = 0.0
                    visa_amount = 0.0
                    mastercard_amount = 0.0
                    amax_amount = 0.0
                    voucher_amount = 0.0
                    other_amount = 0.0
                    batch_id = 0
                    gst = 0.0
                    time_from = time - timedelta(hours=5,minutes=30)
                    time_to = time - timedelta(hours=4,minutes=30)

                    time_from_prev = time_prev - timedelta(hours=5,minutes=30)
                    time_to_prev = time_prev + timedelta(hours=23,minutes=30)

                    time_from = datetime.strptime(str(time_from),'%Y-%m-%d %H:%M:%S')
                    time_to = datetime.strptime(str(time_to),'%Y-%m-%d %H:%M:%S')

                    time_from_prev = datetime.strptime(str(time_from_prev),'%Y-%m-%d %H:%M:%S')
                    time_to_prev = datetime.strptime(str(time_to_prev),'%Y-%m-%d %H:%M:%S')
                    print "time",time_from,time_to,time_from_prev,time_to_prev

                    last_order_id = pos_order_obj.search(cr,uid,[('create_date','>',str(time_from_prev)),('create_date','<',str(time_to_prev))])
                    print last_order_id
                    if last_order_id: 
                        last_batch_id = pos_order_obj.browse(cr,uid,last_order_id[0]).batch_id
                    else:
                        last_batch_id = 0
                    new_batch_id = last_batch_id + 1
                    batch_id = new_batch_id

                    session_ids = self.pool.get('pos.session').search(cr,uid,[('config_id','=',config_id[0])])
                    pos_order_ids = pos_order_obj.search(cr,uid,[('create_date','>',str(time_from)),('create_date','<',str(time_to)),('session_id','in',session_ids)])
                    if pos_order_ids:
                        for each in pos_order_obj.browse(cr,uid,pos_order_ids): 
							self.pool.get('pos.order').write(cr,uid,each.id,{'batch_id':batch_id})
							recipt_count +=1
							amount_gst += each.amount_tax
							gst += each.amount_total
							line_sale = 0.0
							line_subtotal = 0.0
							line_discount=0.0
							for line in each.lines:
								line_sale += line.price_subtotal
								line_subtotal +=  line.price_subtotal
								line_discount += (line.qty*line.price_unit) - line.price_subtotal
							gto_sale += line_sale
							amount_discount += line_discount
														
							for statement in each.statement_ids:
								if statement.journal_id.name == 'Cash':
									cash_amount += statement.amount
								if statement.journal_id.name == 'NETS':
								    nets_amount += statement.amount
								if statement.journal_id.name == 'CHQUE':
								    chque_amount += statement.amount
								if statement.journal_id.name == 'VISA':
								    visa_amount += statement.amount
								if statement.journal_id.name == 'MasterCard':
								    mastercard_amount += statement.amount
								if statement.journal_id.name == 'Amex':
								    amax_amount += statement.amount
								if statement.journal_id.name == 'Voucher':
								    voucher_amount += statement.amount
								if statement.journal_id.name == 'Other':
								    other_amount += statement.amount
                                    
                    	detail_record = detail_record  +'12345678'+'|'+str(batch_id)+'|'+str(datetime.strftime(next_date, "%Y%m%d"))+'|'+str(hour)+'|'+str(recipt_count)+'|'+str(gto_sale)+'|'+str(amount_gst)+'|'+str(amount_discount)+'|'+str(service_charge)+'|'+str(number_of_pax)+'|'+str(cash_amount)+'|'+str(nets_amount)+'|'+str(visa_amount)+'|'+str(mastercard_amount)+'|'+str(amax_amount)+'|'+str(voucher_amount)+'|'+str(other_amount)+'|'+'N'+'\r\n'
                    else:
                    	detail_record = detail_record  +'12345678'+'|'+str(batch_id)+'|'+str(datetime.strftime(next_date, "%Y%m%d"))+'|'+str(hour)+'|'+str(recipt_count)+'|'+str(gto_sale)+'|'+str(amount_gst)+'|'+str(amount_discount)+'|'+str(service_charge)+'|'+str(number_of_pax)+'|'+str(cash_amount)+'|'+str(nets_amount)+'|'+str(visa_amount)+'|'+str(mastercard_amount)+'|'+str(amax_amount)+'|'+str(voucher_amount)+'|'+str(other_amount)+'|'+'N'+'\r\n'
                    time += timedelta(hours=1)
                    # time_prev += timedelta(hours=1)
                next_date +=  timedelta(days=1)
            
            tmp_file.write(detail_record)
        finally:
            if tmp_file:
                tmp_file.close()
        file = open(tgz_tmp_filename, "rb")
        out = file.read()
        file.close()
        
        save_path = '/home/ubuntu'
        completeName = os.path.join(save_path,"gaurav.txt")         
        file1 = open(completeName, "w")
        file1.write(out)
        file1.close()
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