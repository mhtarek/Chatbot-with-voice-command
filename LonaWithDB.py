from gui import Ui_MainWindow
from PyQt4 import QtCore, QtGui
import sqlite3
import urllib.request
import urllib.parse
import re
import speech_recognition as sr
import pyglet
from gtts import gTTS
from tinytag import TinyTag
import sys
import webbrowser as wb



r = sr.Recognizer()
language = 'en'
main_url = 'https://en.wikipedia.org/wiki/'

#url = 'https://www.google.com/search?q='
wiki_url = 'https://en.wikipedia.org/wiki/'
r.energy_threshold = 4000
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
    class main_class(Ui_MainWindow, QtGui.QMainWindow):
        def textToVoice(self,speech):

            myobj = gTTS(text=speech, lang=language, slow=False)
            myobj.save("welcome.mp3")

            tag = TinyTag.get('welcome.mp3')
            try:
                music = pyglet.resource.media('welcome.mp3')
                music.play()
                pyglet.clock.schedule_once(exit, tag.duration)

                pyglet.app.run()
            except:
                pass

        def a(self,test_str):
            ret = ''
            skip1c = 0
            skip2c = 0
            for i in test_str:
                if i == '[':
                    skip1c += 1
                elif i == '(':
                    skip2c += 1
                elif i == ']' and skip1c > 0:
                    skip1c -= 1
                elif i == ')' and skip2c > 0:
                    skip2c -= 1
                elif skip1c == 0 and skip2c == 0:
                    ret += i
            return ret

        def voiceToVoice(self):
            with sr.Microphone() as source:
                self.textToVoice("Say something!")

                ## creating the db file
                conn = sqlite3.connect("DB.db")
                c = conn.cursor()

                try:
                    audio = r.listen(source, timeout=None)
                    speech = r.recognize_google(audio)

                   # "SELECT distinct command from server WHERE command = ?",

                    vals = c.execute("SELECT command, description FROM SERVER WHERE command=?",(speech,)).fetchone()
                    if vals:
                        command, description = vals
                        #print(description)
                        self.textToVoice(description)
                    elif speech=='time':
                        self.textToVoice('You asked for time')

                    else:
                        url = main_url + speech
                        try:
                            values = {'s': 'basics',
                                      'submit': 'search'}
                            data = urllib.parse.urlencode(values)
                            data = data.encode('utf-8')
                            req = urllib.request.Request(url, data)
                            resp = urllib.request.urlopen(req)
                            respData = resp.read()

                            paragraphs = re.findall(r'<p>(.*?)</p>', str(respData))

                            sent_str = ""
                            for i in paragraphs:
                                sent_str += str(i) + "-"
                            sent_str = sent_str[:-1]

                            newStr = re.sub('<.*?>', '', sent_str)

                            result = repr(self.a(newStr))
                            res = result[:100]
                            self.textToVoice(res)

                            conn = sqlite3.connect("DB.db")
                            c = conn.cursor()
                            c.execute("INSERT INTO server(command, description)VALUES(?, ?)",(speech,res))
                            conn.commit()
                            c.close()
                            conn.close()

                            ## print
                            # conn = sqlite3.connect("DB.db")
                            # c = conn.cursor()
                            # c.execute(
                            #     "SELECT distinct command from server WHERE command = ?",
                            #     (speech,))
                            #
                            # x = ""
                            #
                            # for row in c.fetchall():
                            #     x = row[0]
                            #     print(row)
                            # print(x)
                            #
                            # conn.commit()
                            # c.close()
                            # conn.close()
                            # myobj = gTTS(text=speech, lang=language, slow=False)
                            # myobj.save("welcome.mp3")
                            # tag = TinyTag.get('welcome.mp3')
                            #
                            # music = pyglet.resource.media('welcome.mp3')
                            # music.play()
                            # pyglet.clock.schedule_once(exit, tag.duration)
                            #
                            # pyglet.app.run()

                        except urllib.error.HTTPError as err:
                            if err.code == 404:
                                url = 'https://www.google.com/search?q='
                                wb.open_new_tab(url + speech)
                            else:
                                raise

                except sr.UnknownValueError:
                    self.textToVoice("Fuck you")
                except:
                    pass

        def __init__(self):
            super(main_class, self).__init__()
            self.setupUi(self)

            conn = sqlite3.connect("DB.db")
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS SERVER(command TEXT, description TEXT)')
            c.close()
            conn.close()

            self.startBtn.clicked.connect(self.voiceToVoice)


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Ui_MainWindow = main_class()
    Ui_MainWindow.show()
    sys.exit(app.exec_())

