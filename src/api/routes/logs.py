
def route_adtime_logs():
    with open("/logs/adtime.csv") as f:
        csv = f.read()
    rows = csv.split('\n')
    out = rows[-100:]
    out.reverse()
    nl = "\n"
    return f"""
    <html>
        <head>
            <title> Radio Adblocker </title>
            <meta charset='utf-8' />
        </head>
        <body>
            <a href="/logs/adtimes">Aktualisieren</a><br />
            <a href="/logs/backend">Backend Logs</a><br />
            <a href="/">Radio Liste</a><br />
            <pre>{rows[0]}{nl.join(out)}</pre>
        </body>
    </html>
    """


def route_backend_logs():
    with open("/logs/backend.log") as f:
        text = f.read()
    rows = text.split('\n')
    out = rows[-100:]
    out.reverse()
    nl = "\n"
    return f"""
    <html>
        <head>
            <title> Radio Adblocker </title>
            <meta charset='utf-8' />
        </head>
        <body>
            <a href="/logs/backend">Aktualisieren</a><br />
            <a href="/logs/adtimes">Adtime Logs</a><br />
            <a href="/">Radio Liste</a><br />
            <pre>{nl.join(out)}</pre>
        </body>
    </html>
    """