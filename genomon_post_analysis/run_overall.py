# -*- coding: utf-8 -*-
"""
Created on Wed Dec 02 17:43:52 2015

@author: okada

$Id: run_overall.py 125 2016-01-14 05:17:49Z aokada $
$Rev: 125 $
"""
prog = "genomon_pa run"
version = prog + ": $Date: 2016-01-14 14:17:49 +0900 (2016/01/14 (木)) $$Rev: 125 $"

# genomon結果ファイルリスト作成
def find_file(mode, genomon_root, config):
    
    from genomon_post_analysis import tools
    import glob
    import os
    
    # result files
    [section_in, section_out] = tools.get_section(mode)
    input_file_pattern = "%s/%s/*/*%s" % (genomon_root, mode, config.get(section_in, "suffix"))
    
    files_1 = []
    files_2 = []
    for f in glob.glob(input_file_pattern):
        ID = tools.getID(f, mode, config)
        
        # dir構成が "genomon_root/{mode}/ID/ID.suffix" かどうか
        if os.path.basename(os.path.dirname(f)) != ID:
            continue
        
        # 空ファイルかどうか
        if os.path.getsize(f) == 0:
            print "[%s] skip blank file %s" % (mode, f)
            continue
        
        # normalだけの結果を分ける
        yml = genomon_root + "/sv/config/" + ID + ".yaml"
        if os.path.exists(yml) == False:
            if mode == "summary":
                files_1.append(f)
                continue
            else:
                "[%s] skip file %s, with no config file %s" % (mode, f, yml)
                continue
            
        [bam_tumor, bam_normal] = tools.load_yaml(yml)
            
        if len(bam_tumor) > 0 and len(bam_normal) > 0:
            files_1.append(f)
        else:
            files_2.append(f)
            
    return [files_1, files_2]

def call_image_capture(mode, files, output_dir, genomon_root, config):
    
    print "=== [%s] create script file, for IGV image capture. ===" % mode
    
    from genomon_post_analysis import tools
    from genomon_post_analysis import capture
    import os
    
    # output dirs
    output_dir = os.path.abspath(output_dir) + "/" + mode
    
    if (os.path.exists(output_dir) == False):
        os.mkdir(output_dir)
    if (os.path.exists(output_dir + "/capture") == False):
        os.mkdir(output_dir + "/capture")
    if (os.path.exists(output_dir + "/capture_script") == False):
        os.mkdir(output_dir + "/capture_script")
        
    # result files
    files_capt = []
    for f in files[0]:
        ID = tools.getID(f, mode, config)
        yml = genomon_root + "/sv/config/" + ID + ".yaml"
        f_capt = "%s/capture_script/%s.bat" % (output_dir, ID)
        if capture.write_capture_bat(f, f_capt, output_dir + "/capture", "", ID, mode, yml, config) == True:
            files_capt.append(f_capt)
    
    if ((config.getboolean("input", "include_normal") == True) 
      and (config.getboolean("input", mode + "_igv") == True)):
          
        for f in files[1]:
            ID = tools.getID(f, mode, config)
            yml = genomon_root + "/sv/config/" + ID + ".yaml"
            f_capt = "%s/capture_script/%s.bat" % (output_dir, ID)
            if capture.write_capture_bat(f, f_capt, output_dir + "/capture", "", ID, mode, yml, config) == True:
                files_capt.append(f_capt)
            
    capture.merge_capture_bat(files_capt, output_dir + "/capture_script/capture.bat", True)

def call_bam_pickup(mode, files, output_dir, genomon_root, config):
    
    print "=== [%s] create script file, for bam pick up. ===" % mode
    
    from genomon_post_analysis import tools
    from genomon_post_analysis import capture
    import os
    
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
        
    # result files    
    files_pick = []
    for f in files[0]:
        ID = tools.getID(f, mode, config)
        yml = genomon_root + "/sv/config/" + ID + ".yaml"
        f_pick = "%s/pickup.%s.sh" % (output_script_dir, ID)
        if capture.write_pickup_script(f, f_pick, output_bam_dir, output_log_dir, ID, mode, yml, config) == True:
            files_pick.append(f_pick)
    
    if ((config.getboolean("input", "include_normal") == True) 
      and (config.getboolean("input", mode + "_bam") == True)):
          
        for f in files[1]:
            ID = tools.getID(f, mode, config)
            yml = genomon_root + "/sv/config/" + ID + ".yaml"
            f_pick = "%s/pickup.%s.sh" % (output_script_dir, ID)
            if capture.write_pickup_script(f, f_pick, output_bam_dir, output_log_dir, ID, mode, yml, config) == True:
                files_pick.append(f_pick)
            
    capture.merge_pickup_script(files_pick, output_script_dir + "/pickup.sh")
    
def call_summary(mode, files, output_dir, genomon_root, config):
    
    print "=== [%s] merge summary file. ===" % mode
    
    from genomon_post_analysis import capture
        
    # result files
    capture.merge_result(files[0], output_dir + "/merge." + mode + ".tumor.csv", mode, config)
    
    if ((config.getboolean("input", "include_normal") == True) 
      and (config.getboolean("input", mode + "_merge") == True)):
          
        capture.merge_result(files[1], output_dir + "/merge." + mode + ".normal.csv", mode, config)
    
def main(argv):
    from genomon_post_analysis import tools
    import os
    import argparse
    
    parser = argparse.ArgumentParser(prog = prog)

    parser.add_argument("--version", action = "version", version = version)
    parser.add_argument('mode', choices=['mutation', 'sv', 'summary', 'all'], help = "analysis type")
    parser.add_argument("output_dir", help = "output file path", type = str)
    parser.add_argument("genomon_root", help = "output file path", type = str)
    parser.add_argument("--config_file", help = "config file", type = str, default = "")
    
    args = parser.parse_args(argv)
    
    # dirs
    output_dir = os.path.abspath(args.output_dir)
    if (os.path.exists(output_dir) == False):
        os.mkdir(output_dir)
        
    genomon_root = os.path.abspath(args.genomon_root)
    
    # config
    if len(args.config_file) > 0:
        [config, conf_file] = tools.load_config(args.config_file)
    else:
        [config, conf_file] = tools.load_config("")
    
    # call functions
    if args.mode == "all":
        files = find_file("sv", genomon_root, config)
        call_image_capture("sv", files, output_dir, genomon_root, config)
        call_bam_pickup("sv", files, output_dir, genomon_root, config)
        call_summary("sv", files, output_dir, genomon_root, config)

        files = find_file("mutation", genomon_root, config)
        call_image_capture("mutation", files, output_dir, genomon_root, config)
        call_bam_pickup("mutation", files, output_dir, genomon_root, config)
        call_summary("mutation", files, output_dir, genomon_root, config)
        
        files = find_file("summary", genomon_root, config)
        call_summary("summary", files, output_dir, genomon_root, config)

    elif args.mode == "summary":
        files = find_file(args.mode, genomon_root, config)
        call_summary(args.mode, files, output_dir, genomon_root, config)
        
    else:
        files = find_file(args.mode, genomon_root, config)
        call_image_capture(args.mode, files, output_dir, genomon_root, config)
        call_bam_pickup(args.mode, files, output_dir, genomon_root, config)
        call_summary(args.mode, files, output_dir, genomon_root, config)

