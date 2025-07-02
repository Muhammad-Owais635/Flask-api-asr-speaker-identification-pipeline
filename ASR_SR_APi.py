import os
from flask import Flask, request, send_file
import subprocess
from asr_client import MyClient
import time 
app = Flask(__name__)

class CL_ASR_APi:
    def __init__(self):
        self.app = Flask(__name__)
        self.current_dir ="/home/cl/ASR"
        self.script_directory = "/home/cl/kaldi/egs/SRe_V1.0_API"
        self.recieved_wav_path = os.path.join(self.current_dir,'Audios')
        self.script_path = os.path.join(self.current_dir,'Api_Sre_ivec_make_predictions.sh')
        self.segmentor_path = os.path.join(self.current_dir,'segmentor.py')
        self.generator_path = os.path.join(self.current_dir,'generator.py')
        #self.app.route('/ClE_ASR', methods=['GET', 'POST'])(self.ClE_ASR)

    #def run(self):
        #self.app.run(debug=True)

    def read_speaker_segment_names(self,filename):
        speaker_segment_names = {}
        #print("All ok 3")
        with open(filename, 'r') as file:
            for line in file:
                speaker, segment = line.strip().split('\t')
                speaker_segment_names[segment] = speaker
        #print(speaker_segment_names)
        return speaker_segment_names

    def replace_speaker_ids(self,pred_file_path, txt_file_path, dir_name):
        speaker_segment_names = self.read_speaker_segment_names(pred_file_path)
        output_lines = []
        trans_response = {}
        with open(txt_file_path, 'r') as file:
            for line in file:
                #print(line)
                segment, speaker_id, start_time, end_time, text = line.strip().split('\t')
                if segment in speaker_segment_names:
                    speaker_name = speaker_segment_names[segment]
                    trans_response[segment] = {}
                    trans_response[segment]['speakername'] = speaker_name
                    trans_response[segment]['startTime'] = str(start_time)
                    trans_response[segment]['endTime'] = str(end_time)
                    trans_response[segment]['text'] = text
                    output_line = '\t'.join([segment, speaker_name, start_time, end_time, text])
                    output_lines.append(output_line)
        upd_trans_path = os.path.join(self.script_directory,dir_name + '_updated.txt')
        with open(upd_trans_path, 'w') as file:
            file.write(str(trans_response))
        return upd_trans_path

    def Speaker_Recognition(self,wav_file_path, txt_file_path, dir_name):
        subprocess.call(["python3", self.segmentor_path, wav_file_path, txt_file_path])
        seg_dir_path = wav_file_path[:-4]
        print("Deeeeeeeeeeees",seg_dir_path)
        subprocess.call(["python3", self.generator_path, seg_dir_path])
        os.chdir(self.script_directory)
        subprocess.run(["bash", self.script_path, seg_dir_path])
        os.chdir(self.current_dir)
        print("All ok")
        pred_file_path = os.path.join(self.script_directory, "Output_" + dir_name)
        #print(pred_file_path)
        fin_fil_path = self.replace_speaker_ids(pred_file_path, txt_file_path, dir_name)
        return fin_fil_path

    def Cl_ASR(self):
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
                    start_time = time.perf_counter()
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

                    fin_file = self.Speaker_Recognition(wav_file_path, txt_file_path, dir_name)
                    end_time = time.perf_counter()
                    print(f"Time taken by ASR : {end_time - start_time}")
                    return send_file(fin_file, as_attachment=True)
                except Exception as e:
                    print(e)
                    return "something wents wrong"
            else:
                return "Check your file again. It must be audio/wav"
        else:
            return "Please check your file and sent again"
api = CL_ASR_APi()
@app.route('/ASR', methods=["GET", "POST"])
def Cl_ASR():
    return api.Cl_ASR()
    
if __name__ == '__main__':
    app.run(debug=True)

