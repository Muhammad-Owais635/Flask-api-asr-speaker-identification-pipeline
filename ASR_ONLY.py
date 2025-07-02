import os
from flask import Flask, request, send_file
import subprocess
from asr_client import MyClient
app = Flask(__name__)

class CLE_ASR_APi:
    def __init__(self):
        self.app = Flask(__name__)
        self.current_dir ="/home/cl/ASR"
        self.recieved_wav_path = os.path.join(self.current_dir,'Audios')
        #self.app.route('/ClE_ASR', methods=['GET', 'POST'])(self.ClE_ASR)

    #def run(self):
        #self.app.run(debug=True)

    def ClE_ASR(self):
        if request.method == "POST":
            file = request.files["file"]
            if file and file.content_type == 'audio/wav':
                try:
                    f_name = file.filename
                    file_name = os.path.basename(f_name.replace('\\', os.sep))
                    wav_file_path = os.path.join(self.recieved_wav_path,file_name)
                    file.save(wav_file_path)
                    txt_file_path = wav_file_path[:-4] + '.txt'
                    dir_name = file_name[:-4]
                    file = open(txt_file_path, "w")
                    file.close()
                    print(wav_file_path,txt_file_path)
                    audiofile = open(wav_file_path, "rb")
                    ws = MyClient(audiofile, txt_file_path,dir_name, 'ws://localhost:9999/client/ws/speech', byterate=16777216)

                    ws.connect()
                    try:
                        result = ws.get_status()
                        print(result)
                        while result != 0:
                            result = ws.get_status()
                        print("eeeeeeeeeeeeeeeeeeee",result)
                    except Exception as e:
                        print(e, "Passsssssssssssssssssssssss")
                        pass
                    ws.close()
                    audiofile.close()

                    #fin_file = self.Speaker_Recognition(wav_file_path, txt_file_path, dir_name)
                    return send_file(txt_file_path, as_attachment=True)
                except Exception as e:
                    print(e)
                    return "something wents wrong"
            else:
                return "Check your file again. It must be audio/wav"
        else:
            return "Please check your file and sent again"
            
api = CLE_ASR_APi()
@app.route('/ASR', methods=["GET", "POST"])
def ClE_ASR():
    return api.ClE_ASR()
    
if __name__ == '__main__':
    app.run(debug=True)
