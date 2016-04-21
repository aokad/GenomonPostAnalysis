# -*- coding: utf-8 -*-
"""
Created on Wed Dec 02 17:43:52 2015

@author: okada

$Id: run_overall.py 143 2016-04-15 02:28:10Z aokada $
"""
prog = "genomon_pa run"

import genomon_post_analysis.subcode.tools as tools
import capture

# for Genomon-call
def arg_to_file(mode, genomon_root, args, config):
    def text_to_list(inputs, flg):
        
        if flg == False:
            return []
            
        if len(inputs) == 0:
            return []
        
        "--input_file 'sample1_t,sample2_t;sample1_n,sample2_n'"
    
        f = inputs.lstrip("'").lstrip('"').rstrip("'").rstrip('"').split(";")
        
        li = []
        for item in f[0].split(","):
            li.append(item.lstrip(" ").rstrip(" "))
        
        return li
            
    [section_in, section_out] = tools.get_section(mode)
    
    all_dict = {"all":[]}
    if tools.config_getboolean(config, section_out, "all_in_one") == True:
        al = []
        al.extend(text_to_list(args.input_file_case1, True))
        al.extend(text_to_list(args.input_file_case2, tools.config_getboolean(config, section_out, "include_unpanel")))
        al.extend(text_to_list(args.input_file_case3, tools.config_getboolean(config, section_out, "include_unpair")))
        al.extend(text_to_list(args.input_file_case4, 
                  tools.config_getboolean(config, section_out, "include_unpair") and tools.config_getboolean(config, section_out, "include_unpanel")))
        all_dict = {"all": al}
    
    sep_dict = {"case1":[], "case2":[], "case3":[], "case4":[]}
    if tools.config_getboolean(config, section_out, "separate") == True:
        sep_dict["case1"] = text_to_list(args.input_file_case1, True)
        sep_dict["case2"] = text_to_list(args.input_file_case2, tools.config_getboolean(config, section_out, "include_unpanel"))
        sep_dict["case3"] = text_to_list(args.input_file_case3, tools.config_getboolean(config, section_out, "include_unpair"))
        sep_dict["case4"] = text_to_list(args.input_file_case4, 
                  tools.config_getboolean(config, section_out, "include_unpair") and tools.config_getboolean(config, section_out, "include_unpanel"))
    
    return(all_dict, sep_dict)
    
def call_image_capture(mode, ids_tuple, output_dir, genomon_root, sample_conf, config):
    
    print "=== [%s] create script file, for IGV image capture. ===" % mode
    import os
    
    ids = {}
    for dic in ids_tuple:
        for key in dic:
            if len(dic[key]) > 0:
                ids = dic
                break
        
    # output dirs
    output_dir = os.path.abspath(output_dir) + "/" + mode
    
    if (os.path.exists(output_dir) == False):
        os.mkdir(output_dir)
    if (os.path.exists(output_dir + "/capture") == False):
        os.mkdir(output_dir + "/capture")
    if (os.path.exists(output_dir + "/capture_script") == False):
        os.mkdir(output_dir + "/capture_script")
    
    files_capt = []
    for key in ids:
        for ID in ids[key]:

            f_capt = "%s/capture_script/%s.bat" % (output_dir, ID)
            
            path_options = { 
                "output_file": f_capt,
                "output_igv_dir": output_dir + "/capture",
                "bam_dir": "",
                "genomon_root": genomon_root
               }            

            if capture.write_capture_bat(path_options, ID, sample_conf, mode, config) == True:
                files_capt.append(f_capt)
            else:
                if os.path.exists(f_capt) == True:
                    os.remove(f_capt)

    capture.merge_capture_bat(files_capt, output_dir + "/capture_script/capture.bat", True)

def call_bam_pickup(mode, ids_tuple, output_dir, genomon_root, arg_samtools, arg_bedtools, sample_conf, config):
    
    print "=== [%s] create script file, for bam pick up. ===" % mode
    import os
    
    ids = {}
    for dic in ids_tuple:
        for key in dic:
            if len(dic[key]) > 0:
                ids = dic
                break
            
    # output dirs
    output_dir = os.path.abspath(output_dir) + "/" + mode
    output_bam_dir = output_dir + "/bam"
    output_log_dir = output_dir + "/log"
    output_script_dir = output_dir + "/bam_script"
    
    if (os.path.exists(output_dir) == False):
        os.mkdir(output_dir)
    if (os.path.exists(output_bam_dir) == False):
        os.mkdir(output_bam_dir)
    if (os.path.exists(output_log_dir) == False):
        os.mkdir(output_log_dir)
    if (os.path.exists(output_script_dir) == False):
        os.mkdir(output_script_dir)
    
    # tools
    samtools = arg_samtools
    if samtools == "":
        samtools = tools.config_getstr(config, "tools", "samtools")
        
    bedtools = arg_bedtools
    if bedtools == "":
        bedtools = tools.config_getstr(config, "tools", "bedtools")
        
    files_pick = []
    for key in ids:
        for ID in ids[key]:
            f_pick = "%s/pickup.%s.sh" % (output_script_dir, ID)
            
            path_options = {
               "output_file": f_pick,
               "output_bam_dir": output_bam_dir,
               "output_log_dir": output_log_dir,
               "genomon_root": genomon_root,
               "samtools":samtools,
               "bedtools":bedtools
               }
               
            if capture.write_pickup_script(path_options, ID, sample_conf, mode, config) == True:
                files_pick.append(f_pick)
            else:
                if os.path.exists(f_pick) == True:
                    os.remove(f_pick)
    capture.merge_pickup_script(files_pick, output_script_dir + "/pickup.sh")
    
def call_merge_result(mode, ids, output_dir, genomon_root, config):
    
    print "=== [%s] merge result file. ===" % mode
    import genomon_post_analysis.subcode.merge as merge
    
    [section_in, section_out] = tools.get_section(mode)
    suffix_u = tools.config_getstr(config, section_in, "suffix")
    suffix_f = tools.config_getstr(config, section_in, "suffix_filt")
    
    merge_unfilt = tools.config_getboolean(config, section_out, "include_unfilt")
    
    for key in ids:
        # unfilterd
        output_name = tools.config_getstr(config, section_out, "output_" + key)
        if output_name != "":
            if merge_unfilt == True:
                files = []
                for iid in ids[key]:
                    files.append(capture.sample_to_result_file(iid, mode, genomon_root, suffix_u))

                merge.merge_result(files, ids[key], output_dir + "/" + output_name, mode, config)
    
        # filterd
        output_name = tools.config_getstr(config, section_out, "output_filt_" + key)
        if output_name != "":
            files = []
            for iid in ids[key]:
                files.append(capture.sample_to_result_file(iid, mode, genomon_root, suffix_f))
            
            merge.merge_result(files, ids[key], output_dir + "/" + output_name, mode, config)
    
def main(argv):

    import os
    import argparse
    
    parser = argparse.ArgumentParser(prog = prog)

    parser.add_argument("--version", action = "version", version = tools.version_text())
    parser.add_argument('mode', choices=['mutation', 'sv', 'qc', 'all'], help = "analysis type")
    parser.add_argument("output_dir", help = "output file path", type = str)
    parser.add_argument("genomon_root", help = "Genomon root path", type = str)
    parser.add_argument("sample_sheet", help = "sample file of Genomon", type = str)
    parser.add_argument("--config_file", help = "config file", type = str, default = "")
    
    # for genomon-call
    parser.add_argument("--input_file_case1", help = "input file", type = str, default = "")
    parser.add_argument("--input_file_case2", help = "input file", type = str, default = "")
    parser.add_argument("--input_file_case3", help = "input file", type = str, default = "")
    parser.add_argument("--input_file_case4", help = "input file", type = str, default = "")
    parser.add_argument("--samtools", help = "samtool's path", type = str, default = "")
    parser.add_argument("--bedtools", help = "bedtool's path", type = str, default = "")
    
    args = parser.parse_args(argv)
    
    # dirs
    output_dir = os.path.abspath(args.output_dir)
    if (os.path.exists(output_dir) == False):
        os.mkdir(output_dir)
        
    genomon_root = os.path.abspath(args.genomon_root)
    
    # config
    [config, conf_file] = tools.load_config(args.config_file)
    
    sample_conf = capture.load_sample_conf(args.sample_sheet, False)
    if sample_conf == None:
        return
        
    # call functions
    if args.mode == "all":
        (all_ids, sep_ids) = capture.sample_to_list(sample_conf, "sv", genomon_root, config)
        if tools.config_getboolean(config, "igv", "enable") == True:
            call_image_capture("sv", (all_ids, sep_ids), output_dir, genomon_root, sample_conf, config)
        if tools.config_getboolean(config, "bam", "enable") == True:
            call_bam_pickup("sv", (all_ids, sep_ids), output_dir, genomon_root, args.samtools, args.bedtools, sample_conf, config)
        call_merge_result("sv", all_ids, output_dir, genomon_root, config)
        call_merge_result("sv", sep_ids, output_dir, genomon_root, config)
        
        (all_ids, sep_ids) = capture.sample_to_list(sample_conf, "mutation", genomon_root, config)
        if tools.config_getboolean(config, "igv", "enable") == True:
            call_image_capture("mutation", (all_ids, sep_ids), output_dir, genomon_root, sample_conf, config)
        if tools.config_getboolean(config, "bam", "enable") == True:
            call_bam_pickup("mutation", (all_ids, sep_ids), output_dir, genomon_root, args.samtools, args.bedtools, sample_conf, config)
        call_merge_result("mutation", all_ids, output_dir, genomon_root, config)
        call_merge_result("mutation", sep_ids, output_dir, genomon_root, config)
        
        (all_ids, sep_ids) = capture.sample_to_list(sample_conf, "qc", genomon_root, config)
        call_merge_result("qc", all_ids, output_dir, genomon_root,  config)
        call_merge_result("qc", sep_ids, output_dir, genomon_root,  config)

    else:
        (all_ids, sep_ids) = arg_to_file(args.mode, genomon_root, args, config)
        num_al = len(all_ids["all"])
        num_sp = 0
        for key in sep_ids: num_sp += len(sep_ids[key])
        if num_al == 0 and num_sp == 0:
            (all_ids, sep_ids) = capture.sample_to_list(sample_conf, args.mode, genomon_root, config)
            
        if args.mode == "qc":
            call_merge_result(args.mode, all_ids, output_dir, genomon_root,  config)
            call_merge_result(args.mode, sep_ids, output_dir, genomon_root,  config)
        else:
            if tools.config_getboolean(config, "igv", "enable") == True:
                call_image_capture(args.mode,  (all_ids, sep_ids), output_dir, genomon_root, sample_conf, config)
            if tools.config_getboolean(config, "bam", "enable") == True:
                call_bam_pickup(args.mode,  (all_ids, sep_ids), output_dir, genomon_root, args.samtools, args.bedtools, sample_conf, config)
            call_merge_result(args.mode, all_ids, output_dir, genomon_root, config)
            call_merge_result(args.mode, sep_ids, output_dir, genomon_root, config)
            
