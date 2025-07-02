#!/bin/bash
# Copyright 2013   Daniel Povey
#      2014-2016   David Snyder
# Apache 2.0.
######################################################################
#MODIFIED FOR SIMPLE SPEAKER IDENTIFICATION BY MUHAMMAD UMAR FAROOQ
######################################################################
# See README.txt for more info on data required.
# Results (EERs) are inline in comments below.

# This example script is still a bit of a mess, and needs to be
# cleaned up, but it shows you all the basic ingredients.

#. cmd.sh
#. path.sh

. ./path.sh || exit 1
. ./cmd.sh || exit 1

set -e

train_dir=train
test_dir_name_path=$1

readarray -d / -t strarr <<< "$test_dir_name_path"
test_dir=${strarr[-1]}
test_dir=${test_dir: 0:-1}
echo $test_dir
#test_dir='i_test'

dir_path=$1 # audio segments path
path_dir=/home/cl/kaldi/egs/SRe_V1.0_API 


k=128
d=600
ft=mfcc
mfccdir=$ft
vaddir=$ft
stage=1
nj=1
train_ivec_dir=ivectors_Training_8test_spk_meetings_128_600_mfcc
train_ubm_ivec_dir=ivectors_train_ubm_128_600_mfcc





echo	"===========  Usage: This script take one argument target audios path =============="

#Fix_data_directory

DIRECTORY=/data/$test_dir

if [  -d "$DIRECTORY" ]; then
	rm -r $DIRECTORY
fi
mkdir -p data/$test_dir


if [ $stage -eq 1 ]; then


		wav=data/$test_dir/wav.scp
		cp $dir_path/wav.scp  $path_dir/$wav

		utt=data/$test_dir/utt2spk
		cp $dir_path/utt2spk  $path_dir/$utt

		t_ref=data/$test_dir/target_reference
		cp $dir_path/target_reference  $path_dir/$t_ref
		
		#t_ref_unkn=data/$test_dir/target_reference_unkn
		#cp $dir_path/target_reference_unkn  $path_dir/$t_ref_unkn
		
		cp trial_tst.py  data/$test_dir/trial_tst.py
		python3 data/$test_dir/trial_tst.py data/$test_dir 
		
		cp target_unkn_generator.py  data/$test_dir/target_unkn_generator.py
		cp used_ids  data/$test_dir/used_ids

		python3 data/$test_dir/target_unkn_generator.py data/$test_dir/target_reference data/$test_dir/used_ids data/$test_dir/target_reference_unkn

		uttspk=data/$test_dir/spk2utt
		$path_dir/utils/utt2spk_to_spk2utt.pl  $path_dir/$utt >$path_dir/$uttspk
		$path_dir/utils/fix_data_dir.sh $path_dir/data/$test_dir
		
		echo "-----------------------------Stage: $stage----------------------"
		
		stage=$[ stage+1 ]

fi

if [ $stage -eq 2 ]; then
		
		echo "Making MFCCs"
		$path_dir/steps/make_mfcc.sh --mfcc-config $path_dir/conf/mfcc.conf --nj $nj --cmd run.pl $path_dir/data/$test_dir $path_dir/exp/make_mfcc_$test_dir $mfccdir

	  	echo "Computing VADs"
		$path_dir/sid/compute_vad_decision.sh  --vad-config $path_dir/conf/vad.conf  --nj $nj --cmd run.pl $path_dir/data/$test_dir $path_dir/exp/make_vad_$test_dir $vaddir

		echo "Making PLPs:"
		steps/make_plp.sh --nj $nj --cmd run.pl --plp-config conf/plp.conf $path_dir/data/$test_dir exp/make_mfcc_$test_dir $mfccdir

		echo "Making FBANKS:"
		steps/make_fbank.sh --nj $nj --cmd run.pl $path_dir/data/$test_dir exp/make_mfcc_$test_dir $mfccdir


		echo "-----------------------------Stage: $stage----------------------"
		
		stage=$[ stage+1 ]
fi

if [ $stage -eq 3 ]; then
		
		#Extract iVectors
		
		#$path_dir/sid/extract_ivectors.sh --cmd run.pl --nj $nj $path_dir/exp/extractor_128_600_mfcc $path_dir/data/test $path_dir/exp/ivectors_test
		
		#*****************************( HARD CODE ALERT)******************************( exp/xvector_nnet_1a_data_lfcc )**************#
		
		#$path_dir/sid/nnet3/xvector/extract_xvectors.sh --cmd run.pl --nj $nj $path_dir/exp/xvector_nnet_1a_data_mfcc $path_dir/data/$test_dir $path_dir/exp/xvectors_$test_dir
    
    echo "Extracting iVectors:"
    
    $path_dir/sid/extract_ivectors.sh --cmd run.pl --nj $nj $path_dir/exp/extractor_128_600_mfcc $path_dir/data/$test_dir $path_dir/exp/ivectors_$test_dir
		
		echo "-----------------------------Stage: $stage----------------------"
		
		stage=$[ stage+1 ]
fi

#This stage is used to assign the speakers to utterences having highest scores
if [ $stage -eq 4 ]; then
		spk=$path_dir/exp/$train_ivec_dir/spk_ivector.scp
		chmod +x $spk

		xvec=$path_dir/exp/ivectors_$test_dir/ivector.scp
		target=$path_dir/data/$test_dir/target
		python3 $path_dir/local/target.py $spk  $xvec $target
		trials=$path_dir/data/$test_dir/target

		cat $trials | awk '{print $1, $2}' | \
			ivector-compute-dot-products - \
		  scp:$spk \
		  "ark:ivector-normalize-length scp:$path_dir/exp/ivectors_$test_dir/ivector.1.scp ark:- |" \
		  $path_dir/mfcc_cosine_$test_dir'_'1


		echo "8888888888888888888888888888888 {Stage: $stage} 88888888888888888888888888888888888"
		stage=$[ stage+1 ]
fi




if [ $stage -eq 5 ]; then
  
  
  python3 score_eval.py mfcc_cosine_$test_dir'_'1
  
  #python3 spk_lvl_acc.py exp/foo_plda_$test_dir/plda_scores_Predicted data/$test_dir/target_reference
  

  echo "-----------------------------Stage: $stage----------------------"
  stage=$[ stage+1 ]
fi


if [ $stage -eq 6 ]; then
  
  # score evaluation: max score assignment
  
  echo "Speaker Outformater:"
  
  #python3 score_eval2.py exp/foo_plda_$test_dir/plda_scores data/$test_dir/target_reference_unkn
  
  # output_formater: if score >= -3 then same name
				# if score <-3 and  >-19 then name + *
				 # if score < -19 then unknown

  python3 output_formater_thr.py mfcc_cosine_$test_dir'_'1_pred Output_$test_dir
  
  echo "-----------------------------Stage: $stage----------------------"
  
  stage=$[ stage+1 ]

fi



# Removing residual dataset
if [ $stage -eq 7 ]; then
	rm -r $path_dir/data/$test_dir
	rm -r $path_dir/exp/make_mfcc_$test_dir
	rm -r $path_dir/exp/make_vad_$test_dir
	rm -r $path_dir/exp/ivectors_$test_dir
	#rm -r mfcc_cosine_$test_dir'_'1
	#rm -r mfcc_cosine_$test_dir'_'1_pred
	echo "Done"
	
	echo "-----------------------------Stage: $stage----------------------"
	
fi


