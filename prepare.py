import csv
import sys

data_file_name = 'data.csv'


def main():
    if len(sys.argv) < 2:
        print("usage: %s <source-filename>" % sys.argv[0])
        exit(1)

    with open(sys.argv[1], mode='r') as source:
        with open(data_file_name, 'w', newline='') as data:
            csv_reader = csv.reader(source, delimiter=';')
            next(csv_reader)
            data_writer = csv.writer(data, delimiter=';')
            data_writer.writerow(["First and Last Name", "Position", "Company"])
            rows, persons = 0, 0
            for row in csv_reader:
                rows += 1
                name, position, company = ("%s %s" % (row[0], row[1])).strip(), row[4].strip(), row[5].strip()
                if name == "" or (position == "" and company == ""):
                    continue
                persons += 1
                data_writer.writerow([name, position, company])

    print("Prepared %d persons from %d rows" % (persons, rows))


if __name__ == '__main__':
    main()
