import PyPDF2
import re
from db import DB
from os import listdir
import ipdb
from datetime import datetime


def readPDF(folder, filename):
    def extract_float(string):
        return float(string.replace('.', '').replace(',','.'))

    pdfObj = open(folder + filename, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfObj)
    pageObj = pdfReader.getPage(0)
    text = pageObj.extractText()

    # type of buy_order
    if text.find("WertpapierabrechnungKauf") != -1:
        type_ = 'buy_order'
    elif text.find("WertpapierabrechnungVerkauf") != -1:
        type_ = 'sell_order'
    elif text.find("Rückzahlung") != -1:
        type_ = 'warrant_closure'  # a call or put was hold till its final day

    dividend_tax = church_tax = soli_tax = 0
    provision = courtage = exchange_provision = 0

    WKN = re.findall(r'\(WKN\)[\d\w]+ \(([\d\w]{6})\)', text)[0]
    if type_ == 'warrant_closure':
        amount = -int(extract_float(re.findall(r'([\d,.]+) Stück', text)[0]))
        due_date = re.findall(r'Fälligkeit(\d{2}.\d{2}.\d{4})', text)[0]
        date = datetime.strptime(due_date+'00:00:00', '%d.%m.%Y%H:%M:%S')
        #total = extract_float(re.findall(r'Endbetrag([\d,.]+)', text)[0])
        total = 0
        name = re.findall(r'Wertpapierbezeichnung(.+)Nominale', text)[0]
        price = 0
    else:
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

    # store in mysql database
    db = DB()
    db.connect()

    db.cursor.execute("""INSERT INTO transactions
                        (WKN, date, stock_name, amount, price, provision, total, courtage, exchange_provision, 
                        dividend_tax, church_tax, soli_tax, users)
                        VALUES('{}', '{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}, {},'F')""".format(WKN, date, name, 
                        amount, price, provision, total, courtage, exchange_provision, dividend_tax, church_tax, 
                        soli_tax))
    if due_date is not None:
        rowid = db.cursor.lastrowid
        db.cursor.execute("UPDATE transactions SET due_date = '{}' WHERE id = {}".format(due_date, rowid))

    db.cnx.commit()
    db.close()


def readAllPDFs(folder='/home/fabian/Documents/Privat/Depot/'):
    files = listdir(folder)
    for file in files:
        if re.findall(r'Direkt_Depot_\d+_Abrechnung', file) or re.findall(r'Direkt_Depot_\d+_Rueckzahlung', file):
            print("Read file {}".format(file))
            readPDF(folder, file)


def makeStats(account, saldos, user):
    saldo_list = sorted([x for t in saldos[user] for x in saldos[user][t]], key = lambda x: x['date'])
    total_saldo = 0
    for year in set([t['date'].year for t in saldo_list]):
        saldo = sum([t['saldo'] for t in saldo_list if t['date'].year == year])
        total_saldo += saldo
        print("The saldo for {} is {:.2f} EUR.".format(year,saldo))

    print("Total saldo is {:.2f} EUR".format(total_saldo))
