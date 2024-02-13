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
