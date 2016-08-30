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

        f = inputs.lstrip("'").lstrip('"').rstrip("'").rstrip('"').split(";")
        
        li = []
        for item in f[0].split(","):
            li.append(item.lstrip(" ").rstrip(" "))
        
        return li
            
    [section_in, section_out] = tools.get_section(mode)
    
    sample_dict = {"all":[], "case1":[], "case2":[], "case3":[], "case4":[]}
    
    if tools.config_getboolean(config, section_out, "all_in_one") == True:
        al = []
        al.extend(text_to_list(args.input_file_case1, True))
        al.extend(text_to_list(args.input_file_case2, tools.config_getboolean(config, section_out, "include_unpanel")))
        al.extend(text_to_list(args.input_file_case3, tools.config_getboolean(config, section_out, "include_unpair")))
        al.extend(text_to_list(args.input_file_case4, 
                  tools.config_getboolean(config, section_out, "include_unpair") and tools.config_getboolean(config, section_out, "include_unpanel")))
        sample_dict["all"] = al
    
    if tools.config_getboolean(config, section_out, "separate") == True:
        sample_dict["case1"] = text_to_list(args.input_file_case1, True)
        sample_dict["case2"] = text_to_list(args.input_file_case2, tools.config_getboolean(config, section_out, "include_unpanel"))
        sample_dict["case3"] = text_to_list(args.input_file_case3, tools.config_getboolean(config, section_out, "include_unpair"))
        sample_dict["case4"] = text_to_list(args.input_file_case4, 
                  tools.config_getboolean(config, section_out, "include_unpair") and tools.config_getboolean(config, section_out, "include_unpanel"))
    
    return sample_dict
    
def call_image_capture(mode, ids_dict, output_dir, genomon_root, sample_conf, config):
    print "=== [%s] create script file, for IGV image capture. ===" % mode
    import os
    
    def image_capture(mode, sample_list, output_dir, genomon_root, sample_conf, config):
        
        if (os.path.exists(output_dir + "/capture") == False):
            os.mkdir(output_dir + "/capture")
        if (os.path.exists(output_dir + "/capture_script") == False):
            os.mkdir(output_dir + "/capture_script") 
            
        files_capt = []
        for ID in sample_list:

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
        
    # output dirs
    output_dir = os.path.abspath(output_dir) + "/" + mode
    
    if (os.path.exists(output_dir) == False):
        os.mkdir(output_dir)
        
    [section_in, section_out] = tools.get_section(mode)

    for key in ids_dict:
        if len(ids_dict[key]) == 0:
            continue

        dirname = tools.config_getstr(config, section_out, "output_dirname_" + key)
        
        if (os.path.exists(output_dir + "/" + dirname) == False):
            os.mkdir(output_dir + "/" + dirname)
            
        image_capture(mode, ids_dict[key], output_dir + "/" + dirname, genomon_root, sample_conf, config)
    
def call_bam_pickup(mode, ids_dict, output_dir, genomon_root, arg_samtools, arg_bedtools, sample_conf, config):
    print "=== [%s] create script file, for bam pick up. ===" % mode
    import os
    
    def bam_pickup(mode, sample_list, output_dir, genomon_root, samtools, bedtools, sample_conf, config):
        
        output_bam_dir = output_dir + "/bam"
        output_log_dir = output_dir + "/log"
        output_script_dir = output_dir + "/bam_script"        
        if (os.path.exists(output_bam_dir) == False):
            os.mkdir(output_bam_dir)
        if (os.path.exists(output_log_dir) == False):
            os.mkdir(output_log_dir)
        if (os.path.exists(output_script_dir) == False):
            os.mkdir(output_script_dir)
            
        files_pick = []
        for ID in sample_list:
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
    
    # output dirs
    output_dir = os.path.abspath(output_dir) + "/" + mode

    if (os.path.exists(output_dir) == False):
        os.mkdir(output_dir)
        
    # tools
    samtools = arg_samtools
    if samtools == "":
        samtools = tools.config_getstr(config, "tools", "samtools")
        
    bedtools = arg_bedtools
    if bedtools == "":
        bedtools = tools.config_getstr(config, "tools", "bedtools")
            
    [section_in, section_out] = tools.get_section(mode)
    
    for key in ids_dict:
        if len(ids_dict[key]) == 0:
            continue

        dirname = tools.config_getstr(config, section_out, "output_dirname_" + key)
        if (os.path.exists(output_dir + "/" + dirname) == False):
            os.mkdir(output_dir + "/" + dirname)
            
        bam_pickup(mode, ids_dict[key], output_dir + "/" + dirname, genomon_root, samtools, bedtools, sample_conf, config)
    
def call_merge_result(mode, ids_dict, output_dir, genomon_root, config):
    
    print "=== [%s] merge result file. ===" % mode
    
    #import os 
    import genomon_post_analysis.subcode.merge as subcode_merge
    import merge
    
    [section_in, section_out] = tools.get_section(mode)
    suffix_u = tools.config_getstr(config, section_in, "suffix")
    suffix_f = tools.config_getstr(config, section_in, "suffix_filt")
    
    merge_unfilt = tools.config_getboolean(config, section_out, "include_unfilt")
    
    for key in ids_dict:
        if len(ids_dict[key]) == 0:
            continue
        
        # unfilterd
        output_name = tools.config_getstr(config, section_out, "output_" + key)

        #if output_name != "" and os.path.exists(output_dir + "/" + output_name) == False:
        if output_name != "":
            if merge_unfilt == True:
                files = []
                for iid in ids_dict[key]:
                    files.append(capture.sample_to_result_file(iid, mode, genomon_root, suffix_u))

                if mode == "mutation":
                    merge.merge_mutaion_for_paplot(files, ids_dict[key], output_dir + "/" + output_name, config)
                elif mode == "starqc":
                    merge.merge_star_qc_for_paplot(files, ids_dict[key], output_dir + "/" + output_name, config)
                else:
                    subcode_merge.merge_result(files, ids_dict[key], output_dir + "/" + output_name, mode, config)
    
        # filterd
        output_name = tools.config_getstr(config, section_out, "output_filt_" + key)
        
        #if output_name != "" and os.path.exists(output_dir + "/" + output_name) == False:
        if output_name != "":
            files = []
            for iid in ids_dict[key]:
                files.append(capture.sample_to_result_file(iid, mode, genomon_root, suffix_f))
            
            if mode == "mutation":
                merge.merge_mutaion_for_paplot(files, ids_dict[key], output_dir + "/" + output_name, config)
            elif mode == "starqc":
                merge.merge_star_qc_for_paplot(files, ids_dict[key], output_dir + "/" + output_name, config)
            else:
                subcode_merge.merge_result(files, ids_dict[key], output_dir + "/" + output_name, mode, config)
    
def main(mode, argv):

    import os
    import argparse
    
    parser = argparse.ArgumentParser(prog = prog)

    parser.add_argument("--version", action = "version", version = tools.version_text())
    parser.add_argument('mode', choices=['dna', 'rna', 'mutation', 'sv', 'qc', 'fusion', 'starqc'], help = "analysis type")
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
        if mode == "dna":
            sample_dic = capture.sample_to_list(sample_conf, "sv", genomon_root, config)
            if tools.config_getboolean(config, "igv", "enable") == True:
                call_image_capture("sv", sample_dic, output_dir, genomon_root, sample_conf, config)
            if tools.config_getboolean(config, "bam", "enable") == True:
                call_bam_pickup("sv", sample_dic, output_dir, genomon_root, args.samtools, args.bedtools, sample_conf, config)
            call_merge_result("sv", sample_dic, output_dir, genomon_root, config)
            
            sample_dic = capture.sample_to_list(sample_conf, "mutation", genomon_root, config)
            if tools.config_getboolean(config, "igv", "enable") == True:
                call_image_capture("mutation", sample_dic, output_dir, genomon_root, sample_conf, config)
            if tools.config_getboolean(config, "bam", "enable") == True:
                call_bam_pickup("mutation", sample_dic, output_dir, genomon_root, args.samtools, args.bedtools, sample_conf, config)
            call_merge_result("mutation", sample_dic, output_dir, genomon_root, config)
            
            sample_dic = capture.sample_to_list(sample_conf, "qc", genomon_root, config)
            call_merge_result("qc", sample_dic, output_dir, genomon_root,  config)
    
        elif mode == "rna":
            sample_dic = capture.sample_to_list(sample_conf, "fusionfusion", genomon_root, config)
            call_merge_result("fusion", sample_dic, output_dir, genomon_root,  config)
    
            sample_dic = capture.sample_to_list(sample_conf, "qc", genomon_root, config)
            call_merge_result("starqc", sample_dic, output_dir, genomon_root,  config)
        
    else:
        sample_dic = arg_to_file(args.mode, genomon_root, args, config)
        num = 0
        for key in sample_dic: num += len(sample_dic[key])
        if num == 0:
            sample_dic = capture.sample_to_list(sample_conf, args.mode, genomon_root, config)
            
        if args.mode == "qc":
            call_merge_result(args.mode, sample_dic, output_dir, genomon_root,  config)
        elif args.mode == "fusion":
            call_merge_result(args.mode, sample_dic, output_dir, genomon_root,  config)
        elif args.mode == "starqc":
            call_merge_result(args.mode, sample_dic, output_dir, genomon_root,  config)        
        else:
            if tools.config_getboolean(config, "igv", "enable") == True:
                call_image_capture(args.mode,  sample_dic, output_dir, genomon_root, sample_conf, config)
            if tools.config_getboolean(config, "bam", "enable") == True:
                call_bam_pickup(args.mode,  sample_dic, output_dir, genomon_root, args.samtools, args.bedtools, sample_conf, config)
            call_merge_result(args.mode, sample_dic, output_dir, genomon_root, config)
            
