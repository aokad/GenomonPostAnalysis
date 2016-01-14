# -*- coding: utf-8 -*-
"""
Created on Wed Dec 02 17:43:52 2015

@author: okada

$Id: run_bam.py 116 2016-01-07 05:25:14Z aokada $
$Rev: 116 $
"""
prog = "genomon_pa bam"
version = prog + ": $Date: 2016-01-07 14:25:14 +0900 (2016/01/07 (木)) $$Rev: 116 $"

def main(argv):
    from genomon_post_analysis import tools
    from genomon_post_analysis import capture
    import os
    import argparse
    
    parser = argparse.ArgumentParser(prog = prog)
    
    parser.add_argument("--version", action = "version", version = version)
    parser.add_argument('mode', choices=['mutation', 'sv'], help = "analysis type")
    parser.add_argument("input_file", help = "input file path", type = str)
    parser.add_argument("id", help = "sample name", type = str)
    parser.add_argument("output_file", help = "output file path", type = str)
    parser.add_argument("output_bam_dir", help = "output directory path", type = str)
    parser.add_argument("output_log_dir", help = "output directory path", type = str)
    parser.add_argument("genomon_root", help = "genomon root path", type = str)
    parser.add_argument("--config_file", help = "config file", type = str, default = "")
    parser.add_argument("--config_text", help = "config text", type = str, default = "")
    
    args = parser.parse_args(argv)
    
    # config
    if len(args.config_file) > 0:
        [config, conf_file] = tools.load_config(args.config_file)
    elif len(args.config_text) > 0:
        config = tools.parse_config(args.config_text)
    else:
        [config, conf_file] = tools.load_config("")
        
    # dirs
    output_bam_dir = os.path.abspath(args.output_bam_dir)
    if (os.path.exists(output_bam_dir) == False):
        os.makedirs(output_bam_dir)

    output_log_dir = os.path.abspath(args.output_log_dir)
    if (os.path.exists(output_log_dir) == False):
        os.makedirs(output_log_dir)
        
    file_dir = os.path.dirname(args.output_file)
    if (os.path.exists(file_dir) == False):
        os.makedirs(file_dir)
    
    # pair file
    yml = os.path.abspath(args.genomon_root) + "/sv/config/" + args.id + ".yaml"

    if capture.write_pickup_script(args.input_file, args.output_file, output_bam_dir, output_log_dir, args.id, args.mode, yml, config) == False:
        open(args.output_file, "w") 
