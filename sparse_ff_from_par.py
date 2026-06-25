#python script for sparsing Dexela ff-HEDM data based on .par file saved during do_ff_scan_layers_array
#will run sparsing on every scan listed as type "ff" in the specified .par file
#currently requires hard-coding omestart and omeend after looking these up in the spec.log file - future upgrade would pull directly from spec.log
#tested in environment hexrdgui-060526-pr in KS anaconda build
#activate that build by typing:
#source /nfs/chess/sw/anaconda3_ksg52/bin/activate

import json
import os
import preprocess_dexela_dualpanel
import glob
import numpy as np
from hexrd.imageseries import omega
import pp_dexela
from IPython import embed

############### user input - edit these to match your dataset

#path to raw data
fpath="/nfs/chess/raw/2026-1/id3a/" 
#BTR ID
btrid="shanks-4838-b"
#sample name:
samplename="ti7-19-0314-1"
#omega start - verify from SPEC log:
omestart=0
#omega end - verify from SPEC log:
omeend=359.69
#number of junk frames to skip
fstart=0
#number of good frames
keepframes=1441
#threshold to apply
thresh=25
#where to write the output files
outputdir="/nfs/chess/aux/cycles/2026-1/id3a/shanks-4838-b/reduced_data/" + samplename
#ff .json filename
fname_json = "id3a-rams2_ff_scan_layers-dexela-" + samplename + ".json"
#ff .par filename
fname_par = "id3a-rams2_ff_scan_layers-dexela-" + samplename + ".par"

############### only change the next lines if you really know what you are doing

# panel keys to MATCH INSTRUMENT FILE
panel_keys = ['FF1', 'FF2']
panel_opts = dict.fromkeys(panel_keys)

# !!!: hard coded options for each dexela for April 2017
panel_opts['FF1'] = [('add-row', 1944), ('add-column', 1296),('flip', 'v'), ]
panel_opts['FF2'] = [('add-row', 1944), ('add-column', 1296),('flip', 'h'), ]

############### end of user input

ostep = (omeend-omestart)/float(keepframes)

def process_dexelas(file_names, samp_name, scan_number,
                    ostart, ostep, num_frames,
                    panel_opts, threshold, output_dir):
    """
    wrapper for 3A dexela setup
    """
    ostop = ostart + num_frames*ostep
    omw = omega.OmegaWedges(num_frames)
    omw.addwedge(ostart, ostop, num_frames)

    for file_name in file_names:
        for key in panel_keys:
            if key.lower() in file_name:
                ppd = pp_dexela.PP_Dexela(
                    file_name,
                    omw,
                    panel_opts[key],
                    panel_id=key,
                    frame_start=fstart)
#                embed()
#                ppd=add_missing_pixel_gap(ppd)

                output_name = output_dir + '/' + samp_name + '_' + \
                    str(scan_number) + '_' + \
                    file_name.split('/')[-1].split('.')[0]
                ppd.save_processed(output_name, threshold)
                


raw_data_dir = os.path.join(fpath, btrid, samplename)
print("raw data directory: " + raw_data_dir)

fname_json = os.path.join(raw_data_dir, fname_json)
fname_par = os.path.join(raw_data_dir, fname_par)

with open(fname_json, 'r') as file:
    data = json.load(file)
 
#syntax to print out json contents   
#print(json.dumps(data, indent=4))

#find the column with the scan number in it
for i in data:
    #print(i)
    #print(data[i])
    if data[i] == 'SCAN_N':
        scan_num_col = i
        break
        
        
print("the .par file column listing the scan number is: " + str(scan_num_col))

#open the .par file and pull out the scan numbers    
with open(fname_par, 'r') as file:
    par_dta = file.read().split('\n')

par_dta = [i.split(' ') for i in par_dta[0:]]
ff_scans = []

for line in par_dta:
    #does it contain 'ff' as an entry (signifies x-ray data)
    if 'ff' in line:
        #print(line)
        #print(line[int(scan_num_col)])
        ff_scans.append(line[int(scan_num_col)])
        
print('scans containing ff data:')
print(ff_scans)

for scann in ff_scans:
    print('processing scan ' + str(scann) + '...')
    
    file_names = glob.glob(
        os.path.join(
            fpath,
            btrid,
            samplename,
            str(scann),
            'ff',
            '*.h5')
    )
    check_files_exist = [os.path.exists(file_name) for file_name in file_names]
    if not np.all(check_files_exist):
        raise RuntimeError("files don't exist!")

    process_dexelas(file_names, samplename, scann,
                    omestart, ostep, keepframes,
                    panel_opts, thresh, outputdir)
    #process_dexelas(file_names, samp_name, scan_number, ostart, ostep, num_frames, panel_opts, threshold, output_dir)
    
    print("all done.")
    

