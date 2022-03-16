import sys
import csv
import logging
from os import path
from glob import glob 

TCGHeaders = ["TCGplayer Id","Product Line","Set Name","Product Name","Title","Number","Rarity","Condition","TCG Market Price","TCG Direct Low","TCG Low Price With Shipping","TCG Low Price","Total Quantity","Add to Quantity","TCG Marketplace Price","My Store Reserve Quantity","My Store Price","Photo URL"]

def find_ext(dr, ext):
	return glob(path.join(dr,"*.{}".format(ext)))

class CSV_Writer:

	def __init__(self, filename, headers):
		try:
			print(f'CREATING {filename}')
			self.csv_file = open(filename, 'w', newline='')
			self.csv = csv.writer(self.csv_file)
			self.csv.writerow(headers)
		except Exception as exc:
			print(exc)


	def write_row(self, row_data):
		self.csv.writerow(row_data)


	def save(self):
		self.csv_file.close()

class CSV_Reader:

	def __init__(self, filename, required_headers):
		logging.getLogger(__name__)
		self.required_headers = required_headers
		try:
			csv_file = open(filename, 'r', encoding='ISO-8859-1')
			self.csv = csv.DictReader(csv_file)
			if not self.validate_file():
				raise Exception('CSVNotValid')
			self.rows = self.get_nonempty_csv_rows()
            		self.rows = self.get_Prices()
		except Exception as exc:
			logging.critical(exc)
			raise exc


	def get_headers(self):
		return self.clean_headers(self.csv.fieldnames)

	def clean_single_header(self, header):
		clean_header = header.encode('ascii',
									 errors='ignore').decode('utf-8')
		return clean_header

	def clean_headers(self, headers):
		clean_headers = []
		for header in headers:
			clean_header = header.encode('ascii',
										 errors='ignore').decode('utf-8')
			clean_headers.append(clean_header)
		return clean_headers


	def validate_file(self):
		"""Validates headers inside csv
		Returns:
			bool: True if headers are valid, False if not
		"""
		headers = self.clean_headers(self.csv.fieldnames)
		return set(self.required_headers).issubset(headers)


	def search_order_number(self, order_num):
		for row in self.rows:
			if order_num in row.values():
				return row.values()
		return None


	def get_nonempty_csv_rows(self):
		rows = []
		print("Parsing File",end="")
		for i,row in enumerate(self.csv):
			if not (i%1000):
				print(".",end="")
			row_dat = {}
			if row["Total Quantity"] == "0":
				continue
			for header in row.keys():
				clean_header = self.clean_single_header(header)
				row_dat[clean_header] = row[header]	
			rows.append(row_dat)
		print("")
		return rows
        
    def get_prices(self):
        rows = []
        price = cash = credit = 0
        print("Generating Prices",end="")
        for i,row in enumerate(self.csv):
            if not (i%1000):
                print(".",end="")
            row_dat = {}
            if row["TCGplayer Id"] == "TCGplayer Id":
                continue
            price = row["TCG Market Price"]
            cash = price*.55-1
            credit = price*.65-1
            for header in row.keys():
                clean_header = self.clean_single_header(header)
		row_dat[clean_header] = row[header]
            row_dat["Title"] = cash
            row_dat["Number"] = credit
            rows.append(row_dat)
        print("")
        return rows

		
def main():

	if len(sys.argv) > 1:
		print('Usage: ParseTCGInv.py')
		sys.exit()
	files = find_ext(".","csv")
	if len(files) != 1:
		print('Place single TCGPlayer pricing CSV in folder')
		sys.exit()
	file = files[0]
	reader = CSV_Reader(file,TCGHeaders)
	print(file)
	writer = CSV_Writer(file.split(".\\")[-1].split(".")[0]+"_output.csv",TCGHeaders)
	for row in reader.rows:
		writer.write_row(row.values())
	print("Fin")
	
if __name__ == '__main__':
	main()
