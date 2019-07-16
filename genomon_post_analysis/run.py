# -*- coding: utf-8 -*-
"""
Created on Wed Dec 02 17:43:52 2015

@author: okada
"""

import os
import genomon_post_analysis.subcode.tools as tools
import capture

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

def call_image_capture(mode, ids_dict, output_dir, genomon_root, sample_conf, config):
    print ("=== [%s] create script file, for IGV image capture. ===" % mode)

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

    for key in ids_dict:
        if len(ids_dict[key]) == 0:
            continue

        dirname = tools.config_getstr(config, "igv", "dirname_" + key)
        
        if (os.path.exists(output_dir + "/" + dirname) == False):
            os.mkdir(output_dir + "/" + dirname)
            
        image_capture(mode, ids_dict[key], output_dir + "/" + dirname, genomon_root, sample_conf, config)

def call_image_capture_merged(mode, merged_file, output_dir, genomon_root, sample_conf, config):

    print ("=== [%s] create script file, for IGV image capture. ===" % mode)

    if (os.path.exists(output_dir + "/capture") == False):
        os.mkdir(output_dir + "/capture")
    if (os.path.exists(output_dir + "/capture_script") == False):
        os.mkdir(output_dir + "/capture_script") 

    path_options = { 
        "output_file": "%s/capture_script/capture.bat" % (output_dir),
        "output_igv_dir": output_dir + "/capture",
        "bam_dir": "",
        "genomon_root": genomon_root
       }

    capture.write_capture_bat_from_merged(path_options, merged_file, sample_conf, mode, config)

def call_bam_pickup(mode, ids_dict, output_dir, genomon_root, sample_conf, config):

    print ("=== [%s] create script file, for bam pick up. ===" % mode)
    
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
    samtools = tools.config_getstr(config, "tools", "samtools")
    bedtools = tools.config_getstr(config, "tools", "bedtools")
    
    for key in ids_dict:
        if len(ids_dict[key]) == 0:
            continue

        dirname = tools.config_getstr(config, "bam", "dirname_" + key)
        if (os.path.exists(output_dir + "/" + dirname) == False):
            os.mkdir(output_dir + "/" + dirname)
            
        bam_pickup(mode, ids_dict[key], output_dir + "/" + dirname, genomon_root, samtools, bedtools, sample_conf, config)
    
def call_merge_result(mode, ids_dict, output_dir, genomon_root, config):
    
    print ("=== [%s] merge result file. ===" % mode)
    
    if config.getboolean("develop", "debug"):
        import pprint 
        pprint.pprint (ids_dict)
    
    import genomon_post_analysis.subcode.merge as subcode_merge
    import merge
    
    [section_in, section_out] = tools.get_section(mode)
    suffix_u = tools.config_getstr(config, section_in, "suffix")
    suffix_f = tools.config_getstr(config, section_in, "suffix_filt")
    
    for key in ids_dict:
        
        output_name = tools.config_getstr(config, section_out, "filename_" + key)
        if output_name == "": continue
        if len(ids_dict[key]) == 0: continue
        
        suffix = suffix_u
        if key.startswith("filt_"):
            suffix = suffix_f
            
        files = []
        for iid in ids_dict[key]:
            files.append(capture.sample_to_result_file(iid, mode, genomon_root, suffix))
                
        if mode == "mutation":
            merge.merge_mutaion_for_paplot(files, ids_dict[key], output_dir + "/" + output_name, config)
        elif mode == "starqc":
            merge.merge_star_qc_for_paplot(files, ids_dict[key], output_dir + "/" + output_name, config)
        else:
            subcode_merge.merge_result(files, ids_dict[key], output_dir + "/" + output_name, mode, config)

def get_sample_dic(mode, genomon_root, args, config, sample_conf):
    
    ### for stand-alone ################
    def set_sample_4type(li, mode, config):
        
        tmr_nrml_list = []
        tmr_nrml_none = []
        tmr_none_list = []
        tmr_none_none = []
        
        for item in li:
            if item[1]== None:  # pair
                if item[2] == None: # control-panel
                    tmr_none_none.append(item[0])
                else:
                    tmr_none_list.append(item[0])
            else:
                if item[2] == None:
                    tmr_nrml_none.append(item[0])
                else:
                    tmr_nrml_list.append(item[0])
        
        sample_dict = {"raw_case1":[], "raw_case2":[], "raw_case3":[], "raw_case4":[], "raw_all":[], "filt_case1":[], "filt_case2":[], "filt_case3":[], "filt_case4":[], "filt_all":[]}
        
        [section_in, section_out] = tools.get_section(mode)
        
        if tools.config_getboolean(config, section_out, "output_raw_case1") == True: sample_dict["raw_case1"].extend(tmr_nrml_list)
        if tools.config_getboolean(config, section_out, "output_raw_case2") == True: sample_dict["raw_case2"].extend(tmr_nrml_none)
        if tools.config_getboolean(config, section_out, "output_raw_case3") == True: sample_dict["raw_case3"].extend(tmr_none_list)
        if tools.config_getboolean(config, section_out, "output_raw_case4") == True: sample_dict["raw_case4"].extend(tmr_none_none)
        if tools.config_getboolean(config, section_out, "output_filt_case1") == True: sample_dict["filt_case1"].extend(tmr_nrml_list)
        if tools.config_getboolean(config, section_out, "output_filt_case2") == True: sample_dict["filt_case2"].extend(tmr_nrml_none)
        if tools.config_getboolean(config, section_out, "output_filt_case3") == True: sample_dict["filt_case3"].extend(tmr_none_list)
        if tools.config_getboolean(config, section_out, "output_filt_case4") == True: sample_dict["filt_case4"].extend(tmr_none_none)
        if tools.config_getboolean(config, section_out, "output_raw_all") == True:
            sample_dict["raw_all"].extend(tmr_nrml_list)
            sample_dict["raw_all"].extend(tmr_nrml_none)
            sample_dict["raw_all"].extend(tmr_none_list)
            sample_dict["raw_all"].extend(tmr_none_none)
        if tools.config_getboolean(config, section_out, "output_filt_all") == True:
            sample_dict["filt_all"].extend(tmr_nrml_list)
            sample_dict["filt_all"].extend(tmr_nrml_none)
            sample_dict["filt_all"].extend(tmr_none_list)
            sample_dict["filt_all"].extend(tmr_none_none)
                
        return sample_dict
    
    def set_sample_2type(li, mode, config):
        
        tmr_list = []
        tmr_none = []
        
        for item in li:
            if item[1]== None:  # control-panel
                tmr_none.append(item[0])
            else:
                tmr_list.append(item[0])
        
        sample_dict = {"raw_case1":[], "raw_case2":[], "raw_all":[], "filt_case1":[], "filt_case2":[], "filt_all":[]}
        
        [section_in, section_out] = tools.get_section(mode)
        
        if tools.config_getboolean(config, section_out, "output_raw_case1") == True: sample_dict["raw_case1"].extend(tmr_list)
        if tools.config_getboolean(config, section_out, "output_raw_case2") == True: sample_dict["raw_case2"].extend(tmr_none)
        if tools.config_getboolean(config, section_out, "output_filt_case1") == True: sample_dict["filt_case1"].extend(tmr_list)
        if tools.config_getboolean(config, section_out, "output_filt_case2") == True: sample_dict["filt_case2"].extend(tmr_none)
        if tools.config_getboolean(config, section_out, "output_raw_all") == True:
            sample_dict["raw_all"].extend(tmr_list)
            sample_dict["raw_all"].extend(tmr_none)
        if tools.config_getboolean(config, section_out, "output_filt_all") == True:
            sample_dict["filt_all"].extend(tmr_list)
            sample_dict["filt_all"].extend(tmr_none)
        
        return sample_dict
        
    if mode == "mutation":
        return set_sample_4type(sample_conf.mutation_call, mode, config)
    elif mode == "sv":
        return set_sample_4type(sample_conf.sv_detection, mode, config)
    elif mode == "fusion":
        return set_sample_2type(sample_conf.fusion, mode, config)
        
    sample_dict = {}
    
    if mode == "qc" or mode == "starqc":
        items = []
        for item in sample_conf.qc:
            items.append(item)
        
        sample_dict["raw_all"] = items
    ####################################
    
    return sample_dict

def main():
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(prog = "genomon_pa")

    parser.add_argument("--version", action = "version", version = tools.version_text())
    parser.add_argument('mode', choices=['mutation', 'sv', 'qc', 'fusion', 'starqc'], help = "analysis type")
    parser.add_argument("output_dir", help = "path to output-dir ", type = str)
    parser.add_argument("genomon_root", help = "path to Genomon-working-root", type = str)
    parser.add_argument("sample_sheet", help = "path to Genomon-samplesheet.csv", type = str)
    parser.add_argument("--config_file", help = "config file", type = str, default = "")
    
    # for personal call
    parser.add_argument('--submode', choices=['igv', 'bam'], help = "analysis type", default = "")
    parser.add_argument("--merged_file", help = "path to merged result file, comma delimited.", type = str, default = "")
    
    #args = parser.parse_args(sys.argv[1:len(sys.argv)])
    args, option_args = parser.parse_known_args(sys.argv[1:len(sys.argv)])

    # dirs
    output_dir = os.path.abspath(args.output_dir)
    if (os.path.exists(output_dir) == False):
        os.mkdir(output_dir)
        
    genomon_root = os.path.abspath(args.genomon_root)
    
    # config
    [config, conf_file] = tools.load_config(args.config_file)
    
    for i in range(0, len(option_args), 2):
        section = option_args[i].replace("--", "").split(":")
        config.set(section[0], section[1], option_args[i+1])
        
    sample_conf = capture.load_sample_conf(args.sample_sheet, False)
    if sample_conf == None:
        return

    if config.getboolean("develop", "debug"):
        import pprint 
        print ("=== known_args ===")
        pprint.pprint (args)
        print ("=== option_args ===")
        pprint.pprint (option_args)
        print ("=== sample_conf.mutation_call ===")
        pprint.pprint (sample_conf.mutation_call)
        print ("=== sample_conf.sv_detection ===")
        pprint.pprint (sample_conf.sv_detection)
        print ("=== sample_conf.qc ===")
        pprint.pprint (sample_conf.qc)
        print ("=== sample_conf.fusion ===")
        pprint.pprint (sample_conf.fusion)
    
    # call functions
    if args.submode == "igv":
        call_image_capture_merged(args.mode, args.merged_file, output_dir, genomon_root, sample_conf, config)

    elif args.submode == "bam":
        sample_dic = get_sample_dic(args.mode, genomon_root, args, config, sample_conf)
        call_bam_pickup(args.mode,  sample_dic, output_dir, genomon_root, sample_conf, config)
                
    else:
        sample_dic = get_sample_dic(args.mode, genomon_root, args, config, sample_conf)
            
        if args.mode == "qc":
            call_merge_result(args.mode, sample_dic, output_dir, genomon_root,  config)
        elif args.mode == "fusion":
            call_merge_result(args.mode, sample_dic, output_dir, genomon_root,  config)
        elif args.mode == "starqc":
            call_merge_result(args.mode, sample_dic, output_dir, genomon_root,  config)
        else:   # "sv" or "mutation"
            if tools.config_getboolean(config, "igv", "enable") == True:
                call_image_capture(args.mode,  sample_dic, output_dir, genomon_root, sample_conf, config)
            if tools.config_getboolean(config, "bam", "enable") == True:
                call_bam_pickup(args.mode,  sample_dic, output_dir, genomon_root, sample_conf, config)
            call_merge_result(args.mode, sample_dic, output_dir, genomon_root, config)

