# Einführung
Wir haben eine Android-App entwickelt, mit der man Radios über das Internet hören kann. Das besondere ist hier, dass die Werbungen dieser Radios von der App blockiert werden. Im Falle, dass auf einem Radiosender die Werbung anfängt, wird automatisch auf ein vorher festgelegtes Radio gewechselt.  

Die unterstützten Radios sind im Folgenden aufgelistet: Antenne AC, Radio RST, BAYERN 1, 100.5 Das Hitradio, BremenNext, 1Live, WDR2

Die App ist so gestaltet, dass man sich nirgendwo anmelden muss und so wenig wie möglich Daten mit dem Server teilt. Daten, die mit dem Server geteilt werden müssen, werden sobald wie möglich wieder gelöscht.  

# Die App
Die App wurde in Flutter geschrieben. Den Source Code findet man im GitLab unter dem Repository “Frontend”.  

In der App gibt es drei Seiten. Im Folgenden werden diese näher erläutert.  

# Radioliste
Hier werden alle verfügbaren Radios aufgelistet. Die Liste der Radios enthält Livedaten und wird laufend aktualisiert. Jeder Eintrag hat einen Indikator (Icon), ob dort gerade Musik oder Werbung läuft. Falls dort Musik abgespielt wird, wird außerdem der Songtitel angezeigt.  

Zum Abspielen eines Radios muss dieses angetippt werden. Falls dieses gerade Werbung abspielt, so wird auf ein anderes Radio ausgewichen. Es wird jedoch vermerkt, dass das ausgewählte Radio eine Präferenz ist.  

Radios können durch Berühren des Herzsymbols favorisiert werden. Favorisierte Radios werden dann zu einem “Fluchtradio”. Um sich alle Fluchtradios anzusehen, kann man dazu den Filter “Fluchtradio” aktivieren. Dort ist es nun möglich, eine Priorität festzulegen. Falls auf ein Radio ausgewichen werden muss, wird versucht ein Radio auszuwählen, was möglichst weit oben steht. Falls keines der Fluchtradios Musik abspielt, wird vom Server ein zufälliges ausgewählt.  
# Radio Ansicht
Hier wird das aktuell gespielte Radio angezeigt. Die Menü-Icons sollten von Musikstreaming-Diensten bekannt sein. Die Buttons mit den Pfeilen nach links und rechts wählen ein anderes Radio aus.

# Der Server
Um der App die Arbeit abzunehmen, haben wir uns dafür entschieden, die Werbungserkennung nicht auf der App, sondern extern auf einem Server vorzunehmen.

Wir haben uns für einen Root-Server von Netcup entschieden (RS 1000 G9.5 a1 12M mit dedizierten Kernen und 8 GB RAM).

Dort haben wir zwei Docker-Umgebungen aufgesetzt: Ein Stable-Server für die App und ein Development-Server, auf der man ungestört neue Versionen testen kann, ohne die App zu behindern.

Den Source Code dazu findet man im Repository “Backend”.

Die App verbindet sich mit dem Server (Websocket Verbindung) und kann eine Radioliste anfordern. Der Server sendet nun die Radioliste. Ändert sich die Radioliste, sendet der Server unaufgefordert erneut eine Radioliste mit dem aktuellen Inhalt.

Die App kann als zweiten Befehl sagen, dass sie jetzt ein bestimmtes Radio hören möchte, und gibt zusätzlich noch weitere Fluchtradios an, auf die gewechselt werden sollen, falls beim aktuellen Radiowerbung läuft.

Der Server sendet nun ein Radio, das die App hören soll. Sobald auf dieser Radiowerbung ertönt, sendet der Server unaufgefordert eine Nachricht, auf welches Radio nun ausgewichen werden soll.

Ändert sich der Song, der auf dem Radio abgespielt wird, wird diese Änderung ebenfalls direkt mitgeteilt.

# Erkennung
Für die erste Version haben wir uns von den öffentlich rechtlichen Radiosendern (WDR) die Werbezeiten herausgesucht und die Werbung nur durch statistische Zeitangaben erkannt.

Das Problem hier ist nur, dass der Zeitpunkt bei den öffentlich-rechtlichen immer um ein paar Minuten herum schwankt und bei den privaten Sendern überhaupt nicht vorhersagbar ist.

In der zweiten Version (die aktuelle) wurde der Server dann intelligenter und hörte jeden Radiostream selbst mit. Anhand von Jingles, die Werbung ankündigen, erkennt der Server dann, dass als nächstes Werbung abgespielt wird. Da es meistens keinen Jingle gibt, der das Ende der Werbung ankündigt, wird nach einer festgelegten Zeit von 3 Minuten gesagt, dass nun die Werbung zu Ende ist.

In einer dritten Version müsste man sich einer Erkennung mittels KI auseinandersetzen, um auch das Ende der Werbung präzise vorhersagen zu können. Zudem würde eine solche Analyse den Aufwand für das Hinzufügen von Radios erheblich reduzieren.

Die Metadaten, welcher Song gerade abgespielt wird, holen wir uns von der nicht öffentlichen API von Radio.de.

# Getting Started:
## Server starten
* Installation von Docker
* Projekt von GitLab klonen
* In das geklonte Verzeichnis hineingehen
* Den Server über Docker starten:
*        $ docker compose up -d
* Der Server wird dann auf dem Port 8080 gehostet.

## Server konfigurieren
Im Projektverzeichnis befindet sich eine .env Datei. Dort gibt es viele Konfigurationsmöglichkeiten, die auch jeweils mit einem Kommentar erklärt werden. Für die Vollständigkeit ist hier der Dateiinhalt:

### External port exposed by docker itself
PORT=8080


### Fingerprinting takes approx. 2 seconds per cpu thread/core.We figured that count should be approximately = cpu cores
FINGERPRINT_WORKER_THREAD_COUNT=4


### At least x of all given fingerprints need to match
FINGERPRINT_CONFIDENCE_THRESHOLD=20


### Length of one recorded piece thrown into the fingerprinter
FINGERPRINT_PIECE_DURATION=5s


### How much delay the client needs to not hear any ads
CLIENT_BUFFER=10s


### Overlap between recordings (to prevent that ads can be intersecting)
FINGERPRINT_PIECE_OVERLAP=1s


### It's quite often that ads get detected twice because of the overlapping. To prevent that we want it to skip
FINGERPRINT_SKIP_TIME_AFTER_AD_START=10s


### To prevent that an end jingle doesn't toggle status back to status 'ad' after the fallback timer hit (AD_FALLBACK_TIMEOUT)
FINGERPRINT_SKIP_TIME_AFTER_ARTIFICIAL_AD_END=5min


### The minimum size that is required for recording a piece. If an audio stream doesn't provide that, it will restart
FINGERPRINT_PIECE_MIN_SIZE=10kb


### Timeout for retrieving the audio stream
STREAM_TIMEOUT=10s


### Some radios stop working after like 6 hours. We want to restart those streams beforehand
STREAM_AUTO_RESTART=5h 50min


### Some radios have an end jingle. But if that's not happening somehow, we fallback after this given time:
AD_FALLBACK_TIMEOUT=6min


### Any details about radios and their stats are stored in postgres. Here are the connection details
##### Amount of idle connections to the database that are held by the python server
POOL_SIZE=5        
##### The maximum of connections that may access the database simultaneously. If it's full theres a 'waiting list'  
MAX_CONNECTIONS=50 

### Used by docker, so there's nothing to worry about:
CORE_POSTGRES_HOST=core-db 

&nbsp;
CORE_POSTGRES_USER=postgres

&nbsp;
CORE_POSTGRES_PASSWORD=postgres

&nbsp;
CORE_POSTGRES_DB=adblock_radio


### Fingerprints are stored in mysql. Here are the connection details used by docker, so there's nothing to worry about:
FINGERPRINT_MYSQL_HOST=fingerprint-db

&nbsp;
FINGERPRINT_MYSQL_USER=root

&nbsp;
FINGERPRINT_MYSQL_PASSWORD=root

&nbsp;
FINGERPRINT_MYSQL_DB=fingerprint

## Im Sourcecode zurechtfinden

| Pfad | Erklärung |
| ------ | ------ |
|   /src/api     |    Hier sind die Codedateien, die sich mit der Kommunikation mit dem Client beschäftigen    |
|   /src/api/routes     |   Hier werden die URLs definiert, die ein Client besuchen kann. Unter anderem aber auch der Websocket-Endpoint     |
|/src/backend|Hier ist der wesentliche Code, der sich um die Analyse der Radios beschäftigt: Fingerprinting; zeitbasiertes Umschalten (wird nicht mehr verwendet) und Metadaten aus verschiedenen APIs zusammentragen|
|/src/db|Hier sind alle möglichen Codedateien, die sich mit der Datenbank beschäftigen|
|/src/db/inserts|Hier stehen die Daten, die beim aller ersten Start in die Datenbank geschrieben werden|
|/src/error_handling|Hier sind generische Funktionen, um Fehler abzufangen und Anfragen des Clients zu verifizieren|
|/src/main.py|Hier ist der Einstiegspunkt. Diese Datei wird ausgeführt|
|/simple_client/Client.py|Ein Client-Programm, das im Terminal läuft. Wir haben das benutzt, um nicht vom Frontend-Team abhängig zu sein|
|/logs/backend.log|Alle Logs, die der Server produziert|
|/logs/adtime.csv|Eine Logdatei, die mitschreibt, wann sich der Status eines Radios ändert. Daraus könnte man später statistische Auswertungen produzieren.|
|/logs/metadata.csv|Eine Logdatei, die mitschreibt, welcher Song auf welchem Radio gerade gespielt wird. Hieraus kann man ebenfalls statistische Auswertungen produzieren und ggf. sogar Spotify Playlisten für bestimmte Radios erstellen|
|/fingerprint_audio_files|Hier sind die händisch extrahierten Werbejingles abgespeichert. Neben den Werbejingles gibt es hier auch News Jingles, die bisher aber noch keine Verwendung im Projekt gefunden haben|


## Ein neues Radio hinzufügen

1. Besorgen der URL für den Radiostream
    -  Wichtig: Es sollte im mp3-Format sein.
2. Besorgen der URL für das Logo des Radios

3. Falls es ein NRW Lokalradio ist:
    - `metadata_api = 2`
    - Auf die Webseite des Radios gehen und in den Entwicklertools > Netzwerkanalyse und den API-Call finden, bei dem die Metadaten abgerufen werden.
    - Dort steht eine entsprechende Id für das Radio:
`station_id = <id>`
4. Falls es ein Radio ist, dessen Metadaten auf Radio.de angezeigt werden können:
    - `metadata_api = 1`
    - Auf die Webseite von radio.de gehen und in den Entwicklertools > Netzwerkanalyse und den API-Call finden, bei dem die Metadaten abgerufen werden.
    - Dort steht eine entsprechende Id für das Radio:
`station_id = <id>`
5. Falls es einen Endjingle gibt
    - `ad_duration = 0`
6. Falls es keinen Endjingle gibt
    - Überlegen, wie lange auf dem Radio durchschnittlich Werbung läuft
    - `ad_duration = <Anzahl Minuten>`
7. Werbejingle aufnehmen
    - Der Werbejingle muss auf 1 Sekunde gekürzt werden
    - Als Datei in den Ordner fingerprint_audio_files/AD_SameLenghtJingles ablegen
8. Eintrag in src/db/inserts/radios.json hinzufügen:
```
{
	"id": <Neue Id>,
	"name": <Name des Radios>,
	"status_id": 2,
	"currently_playing": null,
	"current_interpret": null,
	"stream_url": <URL des Radiostreams>,
	"logo_url": <URL des Logos>,
	"station_id": <station_id>,
	"ad_duration": <ad_duration>,
	"ad_until": null,
	"metadata_api": <metadata_api>
}
```
9. Gegebenenfalls die Anzahl der Fingerprint Workers in der .env Datei erhöhen:
`FINGERPRINT_WORKER_THREAD_COUNT = <Anzahl>`

