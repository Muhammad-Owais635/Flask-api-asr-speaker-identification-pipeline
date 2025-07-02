import glob
import sys
# All files ending with .txt
print(sys.argv[1])
address_list=glob.glob(sys.argv[1]+'/*.wav')
file_out=sys.argv[1]
#utt2spk="/home/cle-190/Previous_laptop_data/Speaker_diarization_identification/experimentation/mubashir/utt2spk"
utterence_list=[]
for s in address_list:
	uttname=s.split("/")
	for U in uttname:
	   if U.endswith(".wav"):
	   	utt_id=U.split(".wav")[0]
	   	spk_id=utt_id.split("_")[0]
	   	utterence_list.append(utt_id)
	with open(file_out+'/'+"wav.scp",'a') as f:
	   	f.write(utt_id+"\t"+s+"\n")
	with open(file_out+'/'+"utt2spk",'a') as f:
	   	f.write(utt_id+"\t"+spk_id+"\n")
	with open(file_out+'/'+"target_reference",'a') as f:
	   	f.write(spk_id+"\t"+utt_id+"\t"+"target"+"\n")
#print(utterence_list)
