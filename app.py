from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello():
     params = urls.quote_plus(
        'Driver={ODBC Driver 17 for SQL Server};' +
        'Server=tcp:%s,%s;' % (server, port) +
        'Database=%s;' % db +
        'Uid=%s@%s;' % (user, internal_server) +
        'Pwd={%s};' % urls.quote_plus(password) +
        'Encrypt=yes;' +
        'TrustServerCertificate=no;' +
        'Connection Timeout=30;')

    not_azure_conn = 'mssql+pymssql://{}:{}@{}:{}/{}'.format(user, urls.quote_plus(password), server, port, db)
    azure_conn = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
    connn = not_azure_conn if is_azure_database == 0 else azure_conn

    print('connection')
    print(connn)
    engine = create_engine(connn)
    print('Engine created')

    # db table pulls
    pops_query = '''SELECT *
    FROM (SELECT fracs.cluster_id,
                pops.year,
                fracs.sa1_id,
                fracs.sub_id,
                round(sa1_frac * sub_frac * pops.proj_enr, 8) as adj_pop
        FROM pop_fracs fracs
                INNER JOIN sa1_projections pops ON fracs.sa1_id = pops.sa1_code AND pops.c_type = fracs.c_type) t01
    WHERE cluster_id = {}
    AND year BETWEEN {} AND {};'''.format(cluster_code, year_start, year_end)

    caps_query = '''select sss.code as school_code, temp.year_t as year, temp2.seats FROM (SELECT year as year_t from generate_series({}, {}) as year) temp
                                                                        join (select * from schools where schools.scenario_id = {}) sss on 1 = 1
                                                                        CROSS APPLY (
        select cluster_id, code, name, non_selective_seats + isnull(intervention_seats, 0) as seats
        from schools s
                left join (
            select school_id, sum(spaces_delta) as intervention_seats
            from interventions
            where intervention_year <= year_t
            group by school_id
        ) as iseats on s.id = iseats.school_id
        where scenario_id = {} and s.id = sss.id
    ) temp2
    where scenario_id = {}'''.format(year_start, year_end, scenario_id, scenario_id, scenario_id)

    return "Hello World!"

if __name__ == '__main__':
    app.run()
