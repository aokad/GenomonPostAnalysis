# -*- coding: utf-8 -*-
"""
Created on Wed Dec 02 17:43:52 2015

@author: okada

$Id: capture.py 129 2016-02-03 01:14:46Z aokada $
$Rev: 129 $
"""

def write_capture_bat(data_file, output_file, output_igv_dir, bam_dir, ID, mode, yml, task_config):

    from genomon_post_analysis import tools
    import os
    
    cmd_header = """
genome hg19

"""
    cmd_new = """
new
load {tumor_bam}
load {normal_bam}
"""
    cmd_capt = """
goto {chr}:{start}-{end}
snapshot {name}
"""

    [data, colsname] = tools.load_data_range(data_file, mode, task_config)
    if len(data) == 0:
        return False
        
    [bam_tumor, bam_normal] = tools.load_yaml(yml)
    
    if len(bam_tumor) == 0:
        return False

    # case capture from picked bam
    if len(bam_dir) > 0:
        pickup_bam_suffix = task_config.get("bam", "output_bam_suffix")
        bam_t_name = os.path.basename(os.path.dirname(bam_tumor))
        bam_n_name = os.path.basename(os.path.dirname(bam_normal))        
        bam_normal_p = "%s/%s/%s%s" % (bam_dir, bam_t_name, bam_n_name, pickup_bam_suffix)
        bam_tumor_p = "%s/%s/%s%s" % (bam_dir, bam_t_name, bam_t_name, pickup_bam_suffix)
    else:
        bam_normal_p = bam_normal
        bam_tumor_p = bam_tumor

    out_tumor_name = "%s/%s" % (output_igv_dir, ID)
    
    capt_max = task_config.getint("igv", "capture_max")
    width = task_config.getint("igv", "capture_width")    

    capt_list = []
    capt_text = ""
    
    for i in range(len(data)):
        
        if len(capt_list) >= capt_max:
            continue

        chr1 = data[colsname[0]][i]
        start = data[colsname[1]][i]
        chr2 = data[colsname[2]][i]
        end = data[colsname[3]][i]
        
        fname = "{0}_{1}_{2}_{3}_{4}".format(out_tumor_name, chr1, start, chr2, end)
        if (fname in capt_list) == False:
            capt_list.append(fname)
            
            if (chr1 == chr2) and ((long(end) - long(start)) < (width / 2)):
                capt_text += cmd_capt.format(chr = chr1, start = start - width, end = start + width, name = fname + ".png")
            else:
                start2 = start - width
                if start2 < 0:
                    start2 = 0
                capt_text += cmd_capt.format(chr = chr1, start = start2, end = start + width, name = fname + "_1.png")
                start2 = end-width
                if start2 < 0:
                    start2 = 0
                capt_text += cmd_capt.format(chr = chr2, start = start2, end = end + width, name = fname + "_2.png")
    
    if len(capt_text) > 0:
        cmd = cmd_header
        cmd += cmd_new.format(tumor_bam = bam_tumor_p, normal_bam = bam_normal_p)   
        cmd += capt_text
        
        f = open(output_file, "w")
        f.write(cmd)   
        f.close()
    
        return True
    else:
        return False
  
def write_pickup_script(data_file, output_file, output_bam_dir, output_log_dir, ID, mode, yml, task_config):

    from genomon_post_analysis import tools
    import os
    
    cmd_header = """#!/bin/bash
#
#$ -S /bin/bash
#$ -cwd
#$ -e {log}
#$ -o {log}
"""
    
    cmd_bed1 = """
if [ -e {bed} ]; then
    rm {bed}
fi
"""
    cmd_bed2 = "echo '{chr}\t{start}\t{end}' >> {bed}\n"
    cmd_bed3 = """
{bedtools} sort -i {bed} > {bed}.sort.bed
{bedtools} merge -i {bed}.sort.bed > {bed}.merge.bed
rm {bed} {bed}.sort.bed 
mv {bed}.merge.bed {bed}
    
"""
    cmd_view = """
{samtools} view -h -L {bed} {bam} > {output_bam}.temp.bam
{samtools} sort {output_bam}.temp.bam {output_bam}
{samtools} index {output_bam}.bam
rm {output_bam}.temp.bam
    
"""
    cmd_rm_bed = """
rm {bed}
"""
    [data, colsname] = tools.load_data_range(data_file, mode, task_config)
    if len(data) == 0:
        return False
        
    [bam_tumor, bam_normal] = tools.load_yaml(yml)
    
    if len(bam_tumor) == 0:
        return False
        
    width = task_config.getint("bam", "pickup_width")
    input_bam_suffix = task_config.get("bam", "input_bam_suffix")
    output_bam_suffix = os.path.splitext(task_config.get("bam", "output_bam_suffix"))[0]
    samtools = task_config.get("SOFTWARE", "samtools")
    bedtools = task_config.get("SOFTWARE", "bedtools")

    # output file name
    if os.path.exists(output_bam_dir + "/" + ID) == False:
        os.mkdir(output_bam_dir + "/" + ID)

    out_normal_name = output_bam_dir + "/" + ID + "/" + os.path.basename(bam_normal).replace(input_bam_suffix, "")
    out_tumor_name = output_bam_dir + "/" + ID + "/" + os.path.basename(bam_tumor).replace(input_bam_suffix, "")
    
    # create command text
    bed1_text = cmd_bed1.format(bedtools = bedtools, bed = out_tumor_name + ".bed")
    bed2_text = ""
    bed3_text = cmd_bed3.format(bedtools = bedtools, bed = out_tumor_name + ".bed")
    
    cmd_text = cmd_view.format(samtools = samtools, 
                                bed = out_tumor_name + ".bed",
                                bam = bam_tumor,
                                output_bam = out_tumor_name + output_bam_suffix)
    cmd_text += cmd_view.format(samtools = samtools, 
                                bed = out_tumor_name + ".bed",
                                bam = bam_normal,
                                output_bam = out_normal_name + output_bam_suffix)
    cmd_text += cmd_rm_bed.format(bed = out_tumor_name + ".bed")

    for i in range(len(data)):

        start = data[colsname[1]][i] - width
        if start < 0:
            start = 0
        bed2_text += cmd_bed2.format(chr = data[colsname[0]][i], 
                           start = start,
                           end = data[colsname[1]][i] + width,
                           bed = out_tumor_name + ".bed"
                           )
        start = data[colsname[3]][i] - width
        if start < 0:
            start = 0
        bed2_text += cmd_bed2.format(chr = data[colsname[2]][i], 
                           start = start,
                           end = data[colsname[3]][i] + width,
                           bed = out_tumor_name + ".bed"
                           )
    
    if len(bed2_text) > 0 :
        f_sh = open(output_file, "w")
        f_sh.write(cmd_header.format(log = output_log_dir)) 
        f_sh.write(bed1_text)
        f_sh.write(bed2_text)
        f_sh.write(bed3_text)
        f_sh.write(cmd_text)
        f_sh.close()
        
        return True
    else:
        return False
        
def print_conf(config, conf_file):
    print "******************************"
    print "hello genomon post analysis!!!"
    print "******************************"
    print "\nconfig file:%s" % conf_file
    
    for section in config.sections():
        print "[%s]" % section
        for item in config.items(section):
            print item

def merge_capture_bat(files, output_file, delete_flg):

    import os
    
    write_text = ""
    
    for bat_file in files:
        if os.path.exists(bat_file) == False:
            print "[WARNING] file is not exist. %s" % bat_file
            continue
        
        f = open(bat_file)
        data = f.read()
        f.close()
        
        write_text += data
        
        if delete_flg == True:
            os.remove(bat_file)
    
    f = open(output_file, "w")
    f.write(write_text)
    f.close()

def merge_pickup_script(files, output_file):

    import os
    
    write_text = """#!/bin/bash
#
"""

    for bat_file in files:
        if os.path.exists(bat_file) == False:
            print "[WARNING] file is not exist. %s" % bat_file
            continue
        
        write_text += "qsub %s\nsleep 1s\n" % bat_file
    
    f = open(output_file, "w")
    f.write(write_text)
    f.close()
    
    os.chmod(output_file, 0744)

def merge_result(files, output_file, mode, task_config):

    from genomon_post_analysis import tools
    import os
    
    first = True
    
    for result_file in files:
        if os.path.exists(result_file) == False:
            print "[WARNING] file is not exist. %s" % result_file
            continue

        ID = tools.getID(result_file, mode, task_config) 
        data = tools.load_data_all(result_file, ID, mode, task_config)

        if len(data) == 0:
            continue

        if first == True:
            data.to_csv(output_file, index = False, header = True, mode = "w")
            first = False
        else:
            data.to_csv(output_file, index = False, header = False, mode = "a")

