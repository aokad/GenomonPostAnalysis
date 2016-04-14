# -*- coding: utf-8 -*-
"""
Created on Wed Dec 02 17:43:52 2015

@author: okada

$Id: capture.py 140 2016-04-13 07:25:15Z aokada $
$Rev: 140 $
"""

def load_sample_conf(f):
    import sample_conf
    import os
    
    if os.path.exists(f) == False:
        print ("sample_sheet is none: %s" % (f))
        return None
    
    sample = sample_conf.sample_conf
    try:
        sample.parse_file(f)
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
    return genomon_root + "/" + mode + "/" + sample_name + "/" + sample_name + suffix

def sample_to_bam_file(sample_name, mode, genomon_root, suffix):
    return genomon_root + "/bam/" + sample_name + "/" + sample_name + suffix

# for stand alone    
def sample_to_list(sample, mode, genomon_root, config):

    import genomon_post_analysis.subcode.tools as tools
    
    all_dict = {"all":[]}
    sep_dict = {"case1":[], "case2":[], "case3":[], "case4":[]}

    if mode == "qc":
        items = []
        for item in sample.qc:
            items.append(item)

        return ({"all": items}, sep_dict)
    
    if mode == "mutation":
        li = sample.mutation_call
    elif mode == "sv":
        li = sample.sv_detection
    else:
        return (all_dict, sep_dict)
        
    tmr_nrml_list = []
    tmr_nrml_none = []
    tmr_none_list = []
    tmr_none_none = []

    [section_in, section_out] = tools.get_section(mode)
    unpair = tools.config_getboolean(config, section_out, "include_unpair")
    unpanel = tools.config_getboolean(config, section_out, "include_unpanel")
    
    for item in li:
        if item[1]== None:
            if unpair == True:
                if item[2] == None:
                    if unpanel == True: tmr_none_none.append(item[0])
                else:
                    tmr_none_list.append(item[0])
        else:
            if item[2] == None:
                if unpanel == True: tmr_nrml_none.append(item[0])
            else:
                tmr_nrml_list.append(item[0])
    
    if tools.config_getboolean(config, section_out, "all_in_one") == True:
        al = []
        al.extend(tmr_nrml_list)
        al.extend(tmr_nrml_none)
        al.extend(tmr_none_list)
        al.extend(tmr_none_none)
        all_dict = {"all": al}
    
    if tools.config_getboolean(config, section_out, "separate") == True:
        sep_dict = {"case1": tmr_nrml_list, "case2": tmr_nrml_none, "case3": tmr_none_list, "case4": tmr_none_none}
    
    return(all_dict, sep_dict)
    
def write_capture_bat(path_options, ID, sample_conf, mode, config):

    cmd_header = """
genome hg19

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

    import genomon_post_analysis.subcode.tools as tools
    import genomon_post_analysis.subcode.merge as merge
    import genomon_post_analysis.subcode.data_frame as data_frame

    [section_in, section_out] = tools.get_section(mode)
    suffix_f = tools.config_getstr(config, section_in, "suffix_filt")
    data_file = sample_to_result_file(ID, mode, path_options["genomon_root"], suffix_f)
    
    # options read
    colpos = merge.load_potisions(mode, config)
    data_options = {"sept": tools.config_getstr(config, section_in, "sept"),
                    "header": tools.config_getboolean(config, section_in, "header"), 
                    "comment": tools.config_getstr(config, section_in, "comment")}
    [usecols, colsname] = merge.header_info(data_file, colpos, mode, data_options)

    try:
        if len(usecols) > 0:
            # data read
            df = data_frame.load_file(data_file, 
                        sept = tools.config_getstr(config, section_in, "sept"), 
                        header = tools.config_getboolean(config, section_in, "header"), 
                        usecol = usecols)
            df.title = colsname
            
            col_chr1 = df.name_to_index("chr1")
            col_chr2 = df.name_to_index("chr2")
            col_start = df.name_to_index("start")
            col_end = df.name_to_index("end")
        else:
            print ("column position is invalid. check your config file.")
            return False

    except IndexError as e:
        print ("column position is invalid. check your config file.")
        return False
    except Exception as e:
        print ("failure open file %s, %s" % (data_file, e.message))
        return False

    bam_tumor = sample_to_bam_file(ID, mode, path_options["genomon_root"], tools.config_getstr(config, "bam", "input_bam_suffix"))
    normal = sample_to_pair(sample_conf, mode, ID)
    bam_normal = ""
    if normal != None:
        bam_normal = sample_to_bam_file(normal, mode, path_options["genomon_root"], tools.config_getstr(config, "bam", "input_bam_suffix"))

    out_tumor_name = "%s/%s" % (path_options["output_igv_dir"], ID)
    
    capt_max = config.getint("igv", "capture_max")
    width = config.getint("igv", "capture_width")    

    capt_list = []
    capt_text = ""
    
    for i in range(len(df.data)):
        
        if len(capt_list) >= capt_max:
            continue

        chr1 = df.data[i][col_chr1]
        start = int(df.data[i][col_start])
        chr2 = df.data[i][col_chr2]
        end = int(df.data[i][col_end])
        
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
        cmd += cmd_new_tumor.format(tumor_bam = bam_tumor)
        if len(bam_normal) > 0:
            cmd += cmd_new_normal.format(normal_bam = bam_normal) 
        cmd += capt_text
        
        f = open(path_options["output_file"], "w")
        f.write(cmd)   
        f.close()
    
        return True
    else:
        return False
  
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

    import genomon_post_analysis.subcode.tools as tools
    import genomon_post_analysis.subcode.merge as merge
    import genomon_post_analysis.subcode.data_frame as data_frame
    
    import os
    
    # options read
    [section_in, section_out] = tools.get_section(mode)
    suffix_f = tools.config_getstr(config, section_in, "suffix_filt")
    data_file = sample_to_result_file(ID, mode, path_options["genomon_root"], suffix_f)
    
    # options read
    colpos = merge.load_potisions(mode, config)
    data_options = {"sept": tools.config_getstr(config, section_in, "sept"),
                    "header": tools.config_getboolean(config, section_in, "header"), 
                    "comment": tools.config_getstr(config, section_in, "comment")}
    [usecols, colsname] = merge.header_info(data_file, colpos, mode, data_options)
    
    # data read
    try:
        if len(usecols) > 0:
            df = data_frame.load_file(data_file, 
                        sept = tools.config_getstr(config, section_in, "sept"), 
                        header = tools.config_getboolean(config, section_in, "header"), 
                        usecol = usecols)
            df.title = colsname
            
            col_chr1 = df.name_to_index("chr1")
            col_chr2 = df.name_to_index("chr2")
            col_start = df.name_to_index("start")
            col_end = df.name_to_index("end")
        else:
            print ("column position is invalid. check your config file.")
            return False
    
    except IndexError as e:
        print ("column position is invalid. check your config file.")
        return False
    except Exception as e:
        print ("failure open file %s, %s" % (data_file, e.message))
        return False

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
    
    # create command text
    bed1_text = cmd_bed1.format(bedtools = bedtools, bed = out_tumor_name + ".bed")
    bed2_text = ""
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

    for i in range(len(df.data)):

        start = df.data[i][col_start] - width
        if start < 0:
            start = 0
        bed2_text += cmd_bed2.format(chr = df.data[i][col_chr1], 
                           start = start,
                           end = df.data[i][col_start] + width,
                           bed = out_tumor_name + ".bed"
                           )
        start = df.data[i][col_end] - width
        if start < 0:
            start = 0
        bed2_text += cmd_bed2.format(chr = df.data[i][col_chr2], 
                           start = start,
                           end = df.data[i][col_end] + width,
                           bed = out_tumor_name + ".bed"
                           )
    
    if len(bed2_text) > 0 :
        f_sh = open(path_options["output_file"], "w")
        f_sh.write(cmd_header.format(log = path_options["output_log_dir"])) 
        f_sh.write(bed1_text)
        f_sh.write(bed2_text)
        f_sh.write(bed3_text)
        f_sh.write(cmd_text)
        f_sh.close()
        
        return True
    else:
        return False
        
def merge_capture_bat(files, output_file, delete_flg):

    import os
    
    write_lines = []
    
    for bat_file in files:
        if os.path.exists(bat_file) == False:
            print "[WARNING] file is not exist. %s" % bat_file
            continue
        
        f = open(bat_file)
        write_lines.append(f.read()) 
        f.close()
    
    f = open(output_file, "w")
    f.writelines(write_lines)
    f.close()

    if delete_flg == True:
        for bat_file in files:
            os.remove(bat_file)
            
def merge_pickup_script(files, output_file):

    import os
    
    header = """#!/bin/bash
#
"""
    write_lines = [header]
    
    for bat_file in files:
        if os.path.exists(bat_file) == False:
            print "[WARNING] file is not exist. %s" % bat_file
            continue
        
        write_lines.append("qsub %s\nsleep 1s\n" % bat_file)
    
    f = open(output_file, "w")
    f.writelines(write_lines)
    f.close()
    
    os.chmod(output_file, 0744)
