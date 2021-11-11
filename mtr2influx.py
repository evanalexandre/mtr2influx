import sys, json
import datetime as dt
from influxdb import InfluxDBClient, SeriesHelper


host = 'localhost'
db = 'mtr'
port = 8086

class HubEntry(SeriesHelper):
    class Meta:
        series_name = '{destination}'
        fields = ['time', 'loss', 'snt', 'last', 'avg', 'best', 'wrst', 'stdev']
        tags = ['destination', 'hop']


def main():
    db_client = InfluxDBClient(host=host, port=port, database=db)
    db_client.create_database(db)
    HubEntry.Meta.client = db_client

    mtr_result = json.load(sys.stdin)
    destination = mtr_result['report']['mtr']['dst']
    report_time = dt.datetime.utcnow()
    for hub in mtr_result['report']['hubs']:
        # persist the hub entry
        # Modifying the data if needed so that is can be easily sorted in the event of more than 9 hops.
        if len(hub['count']) < 2:
            hop = "0" + hub['count'] + "-" + hub['host']
        else:
            hop = hub['count'] + "-" + hub['host']
        HubEntry(
            time=report_time,
            destination=destination,
            hop=hop,
            loss=hub['Loss%'],
            snt=hub['Snt'],
            last=hub['Last'],
            avg=hub['Avg'],
            best=hub['Best'],
            wrst=hub['Wrst'],
            stdev=hub['StDev']
        )
    HubEntry.commit()


if __name__ == '__main__':
    main()
