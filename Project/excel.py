import xlsxwriter


class Excel:
    def __init__(self):
        self.xls=xlsxwriter

    def excel_writer(filename,worksheet,headings,data):
        headers=len(headings)
        data_key_len=len(data.keys())
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet(worksheet)
        bold = workbook.add_format({'bold': 1})
        worksheet.write_row('A1', headings, bold)
        tickets=''
        row = 1
        for k,v in data.items():
            worksheet.write(row, 0, k)
            worksheet.write_string(row, 1, data[k][0])
            worksheet.write_string(row, 2, data[k][1])
            worksheet.write_string(row, 3, str(data[k][2]))
            worksheet.write_string(row, 4, data[k][3]['Nomad'])
            worksheet.write_string(row, 5, data[k][3]['reach'])
            worksheet.write_string(row, 6, data[k][3]['fqdn'])
            worksheet.write_string(row, 7, data[k][3]['new_hostname'])


            row += 1
        workbook.close()
        return True

    def create_report(self,patching,cb,projects,total_patching):
        workbook = self.xls.Workbook('report.xlsx')
        #worksheets
        worksheet = workbook.add_worksheet('Patching')
        worksheet2 = workbook.add_worksheet('B&C in SLA')
        worksheet3 = workbook.add_worksheet('Demand')
        worksheet3.set_zoom(200)
        # here we create bold format object .
        bold = workbook.add_format({'bold': 1})
        headings = ['Category', 'Total']
        # create a data list .
        #patching
        headings = ['Category', 'Values']
        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', patching[0])
        worksheet.write_column('B2', patching[1])
        #CP
        worksheet2.write_row('A1', headings, bold)
        worksheet2.write_column('A2', cb[0])
        worksheet2.write_column('B2', cb[1])
        #Demand
        worksheet3.write_row('A1', headings, bold)
        worksheet3.write_column('A2', projects.keys())
        worksheet3.write_column('B2', projects.values())
        x_len=len(projects.keys())
        # here we create a bar chart object .
        patching_chart = workbook.add_chart({'type': 'pie'})
        cb_chart = workbook.add_chart({'type': 'pie'})
        deman_sign = workbook.add_chart({'type': 'column'})

        patching_chart.add_series({
            'name':       'Patching Team vs. service owner and APF',
            'categories': ['Patching', 1, 0, 3, 0],
            'values':     ['Patching', 1, 1, 3, 1],
            'points': [
                {'fill': {'color': '#0033cc'}},
                {'fill': {'color': '#99ff66'}},
            ],
        })
        cb_chart.add_series({
            'name':       'All Blocker & Critical closed Infra Vuln tickets within SLA and not',
            'categories': ['B&C in SLA', 1, 0, 3, 0],
            'values':     ['B&C in SLA', 1, 1, 3, 1],
            'points': [
                {'fill': {'color': '#00b300'}},
                {'fill': {'color': '#ff0000'}},
            ],
        })
        end_len=x_len+1
        category_len='=Demand!$A$2:A$'+str(end_len)
        value_len='=Demand!$B$2:B$'+str(end_len)
        deman_sign.add_series({
            'Name':       f'{category_len}',
            'categories': f'{category_len}',
            'values':     f'{value_len}',
            'line':       {'color': 'red'},
        })
        # Add a chart title
        patching_chart.set_title ({'name': 'Patching Team vs. Service Owner and APF'})
        cb_chart.set_title ({'name': 'Blocker & Critical closed within SLA and closed not in SLA'})
        deman_sign.set_title ({'name': 'Projects has been done by patching Team '})
        deman_sign.set_y_axis({'name': 'Number of tickets'})
        deman_sign.set_x_axis({'name': 'Service Owner'})

        patching_chart.set_style(10)
        cb_chart.set_style(10)
        deman_sign.set_style(10)

        worksheet.insert_chart('C2', patching_chart, {'x_offset': 50, 'y_offset': 20})
        worksheet2.insert_chart('C2', cb_chart, {'x_offset': 50, 'y_offset': 20})
        worksheet3.insert_chart('C2', deman_sign, {'x_offset': 50, 'y_offset': 20})
        workbook.close()
