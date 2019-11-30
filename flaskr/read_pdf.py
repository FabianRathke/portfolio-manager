import re
from os import listdir
from datetime import datetime
import hashlib

import PyPDF2

from flaskr import db
from flaskr.models import Transactions


def read_pdf(folder, filename):
    m = hashlib.sha256()
    m.update(str.encode(filename))
    
    def extract_float(string):
        return float(string.replace('.', '').replace(',', '.'))

    # check if file was already read into the database
    hashval = m.hexdigest()
    if Transactions.query.filter_by(filename=hashval).count() > 0:
        print("Already in database")
        return

    pdf_obj = open(folder + filename, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_obj)
    page_obj = pdf_reader.getPage(0)
    text = page_obj.extractText()

    # type of buy_order
    if text.find("WertpapierabrechnungKauf") != -1:
        type_ = 'buy_order'
    elif text.find("WertpapierabrechnungVerkauf") != -1:
        type_ = 'sell_order'
    elif text.find("Rückzahlung") != -1:
        type_ = 'warrant_closure'  # a call or put was hold till its final day

    dividend_tax = church_tax = soli_tax = 0
    provision = courtage = exchange_provision = 0

    wkn = re.findall(r'\(WKN\)[\d\w]+ \(([\d\w]{6})\)', text)[0]
    if type_ == 'warrant_closure':
        amount = -int(extract_float(re.findall(r'([\d,.]+) Stück', text)[0]))
        due_date = re.findall(r'Fälligkeit(\d{2}.\d{2}.\d{4})', text)[0]
        date = datetime.strptime(due_date + '00:00:00', '%d.%m.%Y%H:%M:%S')
        
        total = 0
        name = re.findall(r'Wertpapierbezeichnung(.+)Nominale', text)[0]
        price = 0
        order_number = '0'
    else:
        order_number = re.findall(r'Ordernummer([\d\.]+)', text)[0]
        date = re.findall(r'(\d{2}.\d{2}.\d{4})um (\d{2}:\d{2}:\d{2})', text)
        date = datetime.strptime(date[0][0]+date[0][1], '%d.%m.%Y%H:%M:%S')
        # Optionsschein
        if re.findall(r'Wertpapierbezeichnung.+((?:Put|Call)[ \d\w.]+)Fälligkeit', text):
            name = re.findall(r'Wertpapierbezeichnung.+((?:Put|Call)[ \d\w.]+)Fälligkeit', text)[0]
            due_date = re.findall(r'Fälligkeit(\d{2}.\d{2}.\d{4})', text)[0]
            due_date = datetime.strptime(due_date, '%d.%m.%Y').date()
        else:
            name = re.findall(r'Wertpapierbezeichnung(.+)Nominale', text)[0]
            due_date = None

        amount = int(extract_float(re.findall(r'Stück([\d,.]+)', text)[0]))
        if type_ == 'sell_order':
            amount = -amount

        price = extract_float(re.findall(r'KursEUR([\d,]+)', text)[0])
        # any provisions payed
        if re.findall(r'ProvisionEUR([\d,]+)', text):
            provision = extract_float(re.findall(r'ProvisionEUR([\d,]+)', text)[0])

        if re.findall(r'CourtageEUR([\d,]+)', text):
            courtage = extract_float(re.findall(r'CourtageEUR([\d,]+)', text)[0])

        if re.findall(r'HandelsplatzgebührEUR([\d,]+)', text):
            exchange_provision = extract_float(re.findall(r'HandelsplatzgebührEUR([\d,]+)', text)[0])

        if type_ == 'sell_order':
            # taxes
            if re.findall(r'Kapitalertragsteuer[\d,\% ]+EUR([\d,]+)', text):
                dividend_tax = extract_float(re.findall(r'Kapitalertragsteuer[\d,\% ]+EUR([\d,]+)', text)[0])
                church_tax = extract_float(re.findall(r'Kirchensteuer[\d,\% ]+EUR([\d,]+)', text)[0])
                soli_tax = extract_float(re.findall(r'Solidaritätszuschlag[\d,\% ]+EUR([\d,]+)', text)[0])

            total = -extract_float(re.findall(r'GunstenEUR([\d,.]+)', text)[0])
        else:
            # total costs or total return
            total = extract_float(re.findall(r'LastenEUR([\d,.]+)', text)[0])

    transaction = Transactions(stock_name=name,
                               order_number=order_number,
                               filename=hashval,
                               date=date,
                               WKN=wkn,
                               amount=amount,
                               price=price,
                               provision=provision,
                               total=total,
                               courtage=courtage,
                               exchange_provision=exchange_provision,
                               dividend_tax=dividend_tax,
                               church_tax=church_tax,
                               soli_tax=soli_tax)
    db.session.add(transaction)
    # if due_date is not None:
    #     rowid = db.cursor.lastrowid
    #     db.cursor.execute("UPDATE transactions SET due_date = '{}' WHERE id = {}".format(due_date, rowid))


def read_all_pdfs(folder):
    files = listdir(folder)
    for file in files:
        if re.findall(r'Direkt_Depot_\d+_Abrechnung', file) or re.findall(r'Direkt_Depot_\d+_Rueckzahlung', file):
            print("Read file {}".format(file))
            read_pdf(folder, file)

    db.session.commit()
