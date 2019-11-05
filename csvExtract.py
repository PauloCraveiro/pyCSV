import csv

with open('20081026094426.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    print("{:<15s}{:<15s}{:<6s}{:<12s}{:<20s}{:<15s}{:<12s}".format("Latitude", "Longitude", "N", "Altitude",
                                                                    "Date_nDays", "Date", "Time"))
    for row in csv_reader:
        if line_count >= 6:
            print("{:<15s}{:<15s}{:<6s}{:<12s}{:<20s}{:<15s}{:<12s}".format(row[0], row[1], row[2], row[3], row[4],
                                                                            row[5], row[6]))
        line_count += 1
    print(f'Processed {line_count} lines.')

