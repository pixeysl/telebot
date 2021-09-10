import jsonutil
from datetime import date


past_url_list = jsonutil.readLastUrl('ss')

flat_list = [
                "https://www.fairprice.com.sg/wp-content/uploads/2021/09/Online-Digital_CR11681_H215576_P418618_Q321_SUP_DPS_ST_2-Sep2021_R11-1_PATH-01-weekly-saver-3.jpg",
                "https://www.fairprice.com.sg/wp-content/uploads/2021/09/Online-Digital_CR11681_H215576_P418618_Q321_SUP_DPS_ST_2-Sep2021_R11-1_PATH-01-weekly-saver-4.jpg",
                "https://www.fairprice.com.sg/wp-content/uploads/2021/09/Online-Digital_CR11681_H215576_P418618_Q321_SUP_DPS_ST_2-Sep2021_R11-1_PATH-01-weekly-saver-5.jpg",
                "https://www.fairprice.com.sg/wp-content/uploads/2021/09/Online-Digital_CR11681_H215576_P418618_Q321_SUP_DPS_ST_2-Sep2021_R11-1_PATH-01-weekly-saver-6.jpg",
                "https://www.fairprice.com.sg/wp-content/uploads/2021/09/Online-Digital_CR11681_H215576_P418618_Q321_SUP_DPS_ST_2-Sep2021_R11-1_PATH-01-weekly-saver-7.jpg"
                ]
jsonutil.saveTodayUrl(date.today(), 'ss', flat_list)

