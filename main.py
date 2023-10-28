import vlc
import time

def play():
    url = 'https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de'
    url2 = 'https://wdr-wdr2-rheinruhr.icecastssl.wdr.de/wdr/wdr2/rheinruhr/mp3/56/stream.mp3?aggregator=surfmusik-de&1697723004'

    instance = vlc.Instance('--input-repeat=-1', '--fullscreen')
    instance2 = vlc.Instance('--input-repeat=-1', '--fullscreen')

    player = instance.media_player_new()
    player2 = instance2.media_player_new()

    media = instance.media_new(url)
    media2 = instance2.media_new(url2)

    player.set_media(media)
    player2.set_media(media2)

    player.play()
    aktellerPlayer = player



    while 1:
        if time.strftime("%H:%M:%S", time.localtime()) >= "11:28:00":
            if aktellerPlayer == player:
                player.stop()
                aktellerPlayer = player2
                time.sleep(5)
                player2.play()
            else:
                player2.stop()
                aktellerPlayer = player
                time.sleep(5)
                player.play()


if __name__ == '__main__':
    play()


