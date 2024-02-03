from src.db.database_functions import get_radio_by_query
from src.db.db_helpers import NewTransaction


def route_radio_list():
    with NewTransaction():
        radios = get_radio_by_query()
    radios = [f"""
        <tr>
            <td>{radio['name']}</td>
            <td>{radio['status_label']}</td>
            <td>{radio['currently_playing']}</td>
            <td>{radio['current_interpret']}</td>
        </tr>
    """ for radio in radios]
    radios = "\n".join(radios)

    html = f"""
    <html>
        <head>
            <title> Radio Adblocker </title>
            <meta charset='utf-8' />
            <style>
                table {{
                  font-family: arial, sans-serif;
                  border-collapse: collapse;
                  width: 100%;
                }}

                td, th {{
                  border: 1px solid #dddddd;
                  text-align: left;
                  padding: 8px;
                }}

                tr:nth-child(even) {{
                  background-color: #dddddd;
                }}
                </style>
        </head>
        <body>
            <p>Die API findet man unter /api</p>
            <table>
                <tr>
                    <th>Radio</th>
                    <th>Status</th>
                    <th>Songname</th>
                    <th>Interpret</th>
                </tr>
                {radios}
            </table>
            <a href="/">Aktualisieren</a><br />
        </body>
    </html>
    """
    return html
