# -*- coding: utf-8 -*-
"""
Created on Wed Dec 02 17:43:52 2015

@author: okada
"""

import os
import genomon_post_analysis.subcode.tools as tools

def load_sample_conf(f, check):
    import genomon_post_analysis.sample_conf as sample_conf
    
    if os.path.exists(f) == False:
        print ("sample_sheet is none: %s" % (f))
        return None
    
    sample = sample_conf.sample_conf
    try:
        sample.parse_file(f, check)
    except Exception as e:
        print ("failure sample_conf: %s, %s" % (f, e.message))
        return None
    
    return sample
    
def sample_to_pair(sample, mode, tumor):
    
    if mode == "mutation":
        li = sample.mutation_call
    elif mode == "sv":
        li = sample.sv_detection
    else:
        return {}
        
    for pair in li:
        if (tumor in pair) == True:
            return pair[1]
                
    return None
    
def sample_to_result_file(sample_name, mode, genomon_root, suffix):

    if mode == "starqc":
        return genomon_root + "/star/" + sample_name + "/" + sample_name + suffix
        
    return genomon_root + "/" + mode + "/" + sample_name + "/" + sample_name + suffix

def sample_to_bam_file(sample_name, mode, genomon_root, suffix):
    return genomon_root + "/bam/" + sample_name + "/" + sample_name + suffix

def write_capture_bat(path_options, ID, sample_conf, mode, config):

#    cmd_header = """
#genome hg19
#
#"""
    cmd_header = """
"""

    cmd_new_tumor = """
new
load {tumor_bam}
"""
    cmd_new_normal = """
load {normal_bam}
"""
    cmd_capt = """
goto {chr}:{start}-{end}
snapshot {name}
"""

    [section_in, section_out] = tools.get_section(mode)
    
    # result file
    suffix_f = tools.config_getstr(config, section_in, "suffix_filt")
    data_file = sample_to_result_file(ID, mode, path_options["genomon_root"], suffix_f)

    # use bams
    bam_tumor = sample_to_bam_file(ID, mode, path_options["genomon_root"], tools.config_getstr(config, "bam", "input_bam_suffix"))
    normal = sample_to_pair(sample_conf, mode, ID)
    bam_normal = ""
    if normal != None:
        bam_normal = sample_to_bam_file(normal, mode, path_options["genomon_root"], tools.config_getstr(config, "bam", "input_bam_suffix"))

    # output file
    out_tumor_name = "%s/%s" % (path_options["output_igv_dir"], ID)
    
    # options
    width = config.getint("igv", "capture_width")    
    sept = tools.config_getstr(config, section_in, "sept").replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r")
    # read
    capt_list = []
    
    # write script 1
    f = open(path_options["output_file"] + ".tmp", "w")
    f.write(cmd_header)
    f.write(cmd_new_tumor.format(tumor_bam = bam_tumor))
    if len(bam_normal) > 0:
        f.write(cmd_new_normal.format(normal_bam = bam_normal))
            
    # read
    header = []
    capt_text = []
    lines_count = 0
    enable_data = False
    for line in open(data_file):
        if len(capt_list) >= config.getint("igv", "capture_max"):
            break
        
        line = line.rstrip()
        if len(line.replace(sept, "")) == 0:
            continue
        
        if line.find(tools.config_getstr(config, section_in, "comment")) == 0:
            continue
        
        if len(header) == 0:
            header = line.split(sept)
            col_chr1 = header.index(tools.config_getstr(config, section_in, "col_chr1"))
            col_chr2 = header.index(tools.config_getstr(config, section_in, "col_chr2"))
            col_start = header.index(tools.config_getstr(config, section_in, "col_start"))
            col_end = header.index(tools.config_getstr(config, section_in, "col_end"))
            continue
        
        data = line.split(sept)

        chr1 = data[col_chr1]
        start = int(data[col_start])
        chr2 = data[col_chr2]
        end = int(data[col_end])
        
        fname = "{0}_{1}_{2}_{3}_{4}".format(out_tumor_name, chr1, start, chr2, end)
        if (fname in capt_list) == True:
            continue
        
        capt_list.append(fname)
        
        if (chr1 == chr2) and ((float(end) - float(start)) < (width / 2)):
            capt_text.append(cmd_capt.format(chr = chr1, start = start - width, end = start + width, name = fname + ".png"))
            lines_count += 1
        else:
            start2 = start - width
            if start2 < 0:
                start2 = 0
            capt_text.append(cmd_capt.format(chr = chr1, start = start2, end = start + width, name = fname + "_1.png"))
            lines_count += 1
            
            start2 = end-width
            if start2 < 0:
                start2 = 0
            capt_text.append(cmd_capt.format(chr = chr2, start = start2, end = end + width, name = fname + "_2.png"))
            lines_count += 1

        enable_data = True
        
        if (lines_count > 10000):
            f.writelines(capt_text)
            capt_text = []
            lines_count = 0

    if (lines_count > 0):
        f.writelines(capt_text)                
    
    f.close()
    os.rename(path_options["output_file"] + ".tmp", path_options["output_file"])
    
    return enable_data

def write_capture_bat_from_merged(path_options, data_file, sample_conf, mode, config):

#    cmd_header = """
#genome hg19
#
#"""
    cmd_header = """
"""

    cmd_new_tumor = """
new
load {tumor_bam}
"""
    cmd_new_normal = """
load {normal_bam}
"""
    cmd_capt = """
goto {chr}:{start}-{end}
snapshot {name}
"""

    [section_in, section_out] = tools.get_section(mode)

    # options
    width = config.getint("igv", "capture_width")    
    sept = tools.config_getstr(config, section_in, "sept").replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r")
    # read
    capt_list = []
    
    # write script 1
    f = open(path_options["output_file"] + ".tmp", "w")
    f.write(cmd_header)
    
    # read
    header = []
    capt_text = []
    lines_count = 0
    enable_data = False
    last_id = ""
    for line in open(data_file):
        if len(capt_list) >= config.getint("igv", "capture_max"):
            break
        
        line = line.rstrip()
        if len(line.replace(sept, "")) == 0:
            continue
        
        if line.find(tools.config_getstr(config, section_in, "comment")) == 0:
            continue
        
        if len(header) == 0:
            header = line.split(sept)
            col_chr1 = header.index(tools.config_getstr(config, section_in, "col_chr1"))
            col_chr2 = header.index(tools.config_getstr(config, section_in, "col_chr2"))
            col_start = header.index(tools.config_getstr(config, section_in, "col_start"))
            col_end = header.index(tools.config_getstr(config, section_in, "col_end"))
            col_id = header.index(tools.config_getstr(config, section_in, "col_id"))
            continue
        
        data = line.split(sept)

        chr1 = data[col_chr1]
        start = int(data[col_start])
        chr2 = data[col_chr2]
        end = int(data[col_end])
        ID = data[col_id]

        if ID != last_id:
            # use bams
            bam_tumor = sample_to_bam_file(ID, mode, path_options["genomon_root"], tools.config_getstr(config, "bam", "input_bam_suffix"))
            normal = sample_to_pair(sample_conf, mode, ID)
            bam_normal = ""
            if normal != None:
                bam_normal = sample_to_bam_file(normal, mode, path_options["genomon_root"], tools.config_getstr(config, "bam", "input_bam_suffix"))

            # output file
            out_tumor_name = "%s/%s" % (path_options["output_igv_dir"], ID)
            capt_text.append(cmd_new_tumor.format(tumor_bam = bam_tumor))
            lines_count += 1
            if len(bam_normal) > 0:
                capt_text.append(cmd_new_normal.format(normal_bam = bam_normal))
                lines_count += 1

            last_id = ID

        fname = "{0}_{1}_{2}_{3}_{4}".format(out_tumor_name, chr1, start, chr2, end)
        if (fname in capt_list) == True:
            continue
        
        capt_list.append(fname)
        
        if (chr1 == chr2) and ((float(end) - float(start)) < (width / 2)):
            capt_text.append(cmd_capt.format(chr = chr1, start = start - width, end = start + width, name = fname + ".png"))
            lines_count += 1
        else:
            start2 = start - width
            if start2 < 0:
                start2 = 0
            capt_text.append(cmd_capt.format(chr = chr1, start = start2, end = start + width, name = fname + "_1.png"))
            lines_count += 1
            
            start2 = end-width
            if start2 < 0:
                start2 = 0
            capt_text.append(cmd_capt.format(chr = chr2, start = start2, end = end + width, name = fname + "_2.png"))
            lines_count += 1

        enable_data = True
        
        if (lines_count > 10000):
            f.writelines(capt_text)
            capt_text = []
            lines_count = 0

    if (lines_count > 0):
        f.writelines(capt_text)                
    
    f.close()
    os.rename(path_options["output_file"] + ".tmp", path_options["output_file"])
    
    return enable_data

def write_pickup_script(path_options, ID, sample_conf, mode, config):

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
    
    # options read
    [section_in, section_out] = tools.get_section(mode)
    suffix_f = tools.config_getstr(config, section_in, "suffix_filt")
    data_file = sample_to_result_file(ID, mode, path_options["genomon_root"], suffix_f)

    # output file name
    if os.path.exists(path_options["output_bam_dir"] + "/" + ID) == False:
        os.mkdir(path_options["output_bam_dir"] + "/" + ID)

    bam_tumor = sample_to_bam_file(ID, mode, path_options["genomon_root"], tools.config_getstr(config, "bam", "input_bam_suffix"))
    out_tumor_name = path_options["output_bam_dir"] + "/" + ID + "/" + ID
    
    normal = sample_to_pair(sample_conf, mode, ID)
    bam_normal = ""
    out_normal_name = ""
    if normal != None:
        bam_normal = sample_to_bam_file(normal, mode, path_options["genomon_root"], tools.config_getstr(config, "bam", "input_bam_suffix"))
        out_normal_name = path_options["output_bam_dir"] + "/" + ID + "/" + normal
        
    # read config
    width = config.getint("bam", "pickup_width")
    output_bam_suffix = os.path.splitext(config.get("bam", "output_bam_suffix"))[0]
    samtools = path_options["samtools"]
    bedtools = path_options["bedtools"]
    sept = tools.config_getstr(config, section_in, "sept").replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r")
    
    # create command text
    bed1_text = cmd_bed1.format(bedtools = bedtools, bed = out_tumor_name + ".bed")
    #bed2_text = ""
    bed3_text = cmd_bed3.format(bedtools = bedtools, bed = out_tumor_name + ".bed")
    
    cmd_text = cmd_view.format(samtools = samtools, 
                                bed = out_tumor_name + ".bed",
                                bam = bam_tumor,
                                output_bam = out_tumor_name + output_bam_suffix)
    if bam_normal != "":
        cmd_text += cmd_view.format(samtools = samtools, 
                                bed = out_tumor_name + ".bed",
                                bam = bam_normal,
                                output_bam = out_normal_name + output_bam_suffix)
    cmd_text += cmd_rm_bed.format(bed = out_tumor_name + ".bed")

    # write script 1
    f_sh = open(path_options["output_file"] + ".tmp", "w")
    f_sh.write(cmd_header.format(log = path_options["output_log_dir"])) 
    f_sh.write(bed1_text)
        
    # read
    header = []
    bed2_text = []
    lines_count = 0
    enable_data = False
    for line in open(data_file):
        line = line.rstrip()
        if len(line.replace(sept, "")) == 0:
            continue
        
        if line.find(tools.config_getstr(config, section_in, "comment")) == 0:
            continue
        
        if len(header) == 0:
            header = line.split(sept)
            col_chr1 = header.index(tools.config_getstr(config, section_in, "col_chr1"))
            col_chr2 = header.index(tools.config_getstr(config, section_in, "col_chr2"))
            col_start = header.index(tools.config_getstr(config, section_in, "col_start"))
            col_end = header.index(tools.config_getstr(config, section_in, "col_end"))
            continue
        
        data = line.split(sept)

        start = int(data[col_start]) - width
        if start < 0:
            start = 0
        bed2_text.append(cmd_bed2.format(chr = data[col_chr1], 
                           start = start,
                           end = int(data[col_start]) + width,
                           bed = out_tumor_name + ".bed"
                           ))
        lines_count += 1
        
        start = int(data[col_end]) - width
        if start < 0:
            start = 0
        bed2_text.append(cmd_bed2.format(chr = data[col_chr2], 
                           start = start,
                           end = int(data[col_end]) + width,
                           bed = out_tumor_name + ".bed"
                           ))
        lines_count += 1
        
        enable_data = True
        
        if (lines_count > 10000):
            f_sh.writelines(bed2_text)
            bed2_text = []
            lines_count = 0

    if (lines_count > 0):
        f_sh.writelines(bed2_text)
            
    # write script 3
    f_sh.write(bed3_text)
    f_sh.write(cmd_text)
    f_sh.close()
    os.rename(path_options["output_file"] + ".tmp", path_options["output_file"])
    
    return enable_data
        
def merge_capture_bat(files, output_file, delete_flg):

    f_out = open(output_file + ".tmp", "w")
    
    for bat_file in files:
        if os.path.exists(bat_file) == False:
            print ("[WARNING] file is not exist. %s" % (bat_file))
            continue
        
        f_in = open(bat_file)
        f_out.write(f_in.read()) 
        f_in.close()

    f_out.close()
    os.rename(output_file + ".tmp", output_file)
    
    if delete_flg == True:
        for bat_file in files:
            os.remove(bat_file)
            
def merge_pickup_script(files, output_file):

    header = """#!/bin/bash
#
"""
    f = open(output_file + ".tmp", "w")
    write_lines = [header]
    lines_counter = 0
    for bat_file in files:
        if os.path.exists(bat_file) == False:
            print ("[WARNING] file is not exist. %s" % (bat_file))
            continue
        
        write_lines.append("qsub %s\nsleep 1s\n" % bat_file)
        lines_counter += 1
        if lines_counter > 10000:
            f.writelines(write_lines)
            write_lines = []
            lines_counter = 0
    
    if lines_counter > 0:
        f.writelines(write_lines)

    f.close()
    os.rename(output_file + ".tmp", output_file)
    
    #os.chmod(output_file, 0744)
