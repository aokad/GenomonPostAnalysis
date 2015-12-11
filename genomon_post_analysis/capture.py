# -*- coding: utf-8 -*-
"""
Created on Wed Dec 02 17:43:52 2015

@author: okada

$Id: capture.py 89 2015-12-11 10:04:49Z aokada $
$Rev: 89 $
"""

def write_capture_bat(data_file, output_file, output_dir, ID, mode, yml, task_config):

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

    [data, colsname] = tools.resultfile_load_mini(data_file, mode, task_config)
    [bam_tumor, bam_normal] = tools.load_yaml(yml)
    
    use_pickup_bam = task_config.getboolean("capture", "use_pickup_bam")
    
    # case capture from picked bam
    if use_pickup_bam == True:
        pickup_bam_suffix = task_config.get("pickup", "pickup_bam_suffix")
        bam_t_name = os.path.basename(os.path.dirname(bam_tumor))
        bam_n_name = os.path.basename(os.path.dirname(bam_normal))        
        bam_normal_p = "%s/bam/%s/%s%s" % (output_dir, bam_t_name, bam_n_name, pickup_bam_suffix)
        bam_tumor_p = "%s/bam/%s/%s%s" % (output_dir, bam_t_name, bam_t_name, pickup_bam_suffix)
    else:
        bam_normal_p = bam_normal
        bam_tumor_p = bam_tumor

    out_tumor_name = "%s/capture/%s" % (output_dir, ID)
    
    capt_max = task_config.getint("capture", "capture_max")
    width = task_config.getint("capture", "capture_width")    

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

            if (long(end) - long(start)) < (width / 2):
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
    
  
def write_pickup_script(data_file, output_file, output_dir, ID, mode, yml, task_config, genomon_config):

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
    [data, colsname] = tools.resultfile_load_mini(data_file, mode, task_config)
    [bam_tumor, bam_normal] = tools.load_yaml(yml)
    
    width = task_config.getint("pickup", "pickup_width")
    markdup_bam_suffix = task_config.get("pickup", "markdup_bam_suffix")
    pickup_bam_suffix = task_config.get("pickup", "pickup_bam_suffix")
    pickup_bam_suffix = os.path.splitext(pickup_bam_suffix)[0]
    samtools = genomon_config.get("TOOLS", "samtools")
    bedtools = genomon_config.get("TOOLS", "bedtools")
    biobambam = genomon_config.get("TOOLS", "biobambam")
    ref_fa = genomon_config.get("REFERENCE", "ref_fasta")

    # output file name
    out_normal_name = output_dir + "/bam/" + ID + "/" + os.path.basename(bam_normal).replace(markdup_bam_suffix, "")
    out_tumor_name = output_dir + "/bam/" + ID + "/" + os.path.basename(bam_tumor).replace(markdup_bam_suffix, "")
    
    # create command text
    bed1_text = cmd_bed1.format(bedtools = bedtools, bed = out_tumor_name + ".bed")
    bed2_text = ""
    bed3_text = cmd_bed3.format(bedtools = bedtools, bed = out_tumor_name + ".bed")
    
    cmd_text = cmd_view.format(samtools = samtools, 
                                bed = out_tumor_name + ".bed",
                                bam = bam_tumor,
                                output_bam = out_tumor_name + pickup_bam_suffix,
                                biobambam = biobambam,
                                ref_fa = ref_fa)
    cmd_text += cmd_view.format(samtools = samtools, 
                                bed = out_tumor_name + ".bed",
                                bam = bam_normal,
                                output_bam = out_normal_name + pickup_bam_suffix,
                                biobambam = biobambam,
                                ref_fa = ref_fa)
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
        f_sh.write(cmd_header.format(log = output_dir +"/log")) 
        f_sh.write(bed1_text)
        f_sh.write(bed2_text)
        f_sh.write(bed3_text)
        f_sh.write(cmd_text)
        f_sh.close()

def hello(config_file):

    from genomon_post_analysis import tools
    
    print "******************************"
    print "hello genomon post analysis!!!"
    print "******************************"
    
    [config, config_file2] = tools.resultfile_load_mini(config_file)
    if config == None:
        print "config_file is not exists:%s" % config_file2
        return
        
    print "\nconfig file:%s" % config_file2
    
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
        data = tools.resultfile_load_all(result_file, ID, mode, task_config)

        if len(data) == 0:
            continue

        if first == True:
            data.to_csv(output_file, index = False, header = True, mode = "w")
            first = False
        else:
            data.to_csv(output_file, index = False, header = False, mode = "a")

