import sys, json, config
import datetime as dt
from influxdb import InfluxDBClient, SeriesHelper


class HubEntry(SeriesHelper):
    class Meta:
        series_name = '{destination}'
        fields = ['time', 'loss', 'snt', 'last', 'avg', 'best', 'wrst', 'stdev']
        tags = ['destination', 'hop']


def main():
    db_client = InfluxDBClient(host=config.host, port=config.port, database=config.db)
    db_client.create_database(config.db)
    HubEntry.Meta.client = db_client
    mtr_result = json.load(sys.stdin)
    destination = mtr_result['report']['mtr']['dst']
    report_time = dt.datetime.utcnow()
    for hub in mtr_result['report']['hubs']:
        # Modifying data so it can be sorted in the event of more than 9 hops
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
