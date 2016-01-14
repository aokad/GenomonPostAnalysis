# -*- coding: utf-8 -*-
"""
Created on Wed Dec 02 17:43:52 2015

@author: okada

$Id: run_merge.py 116 2016-01-07 05:25:14Z aokada $
$Rev: 116 $
"""
prog = "genomon_pa merge"
version = prog + ": $Date: 2016-01-07 14:25:14 +0900 (2016/01/07 (木)) $$Rev: 116 $"

def main(argv):
    from genomon_post_analysis import tools
    from genomon_post_analysis import capture
    import argparse
    
    parser = argparse.ArgumentParser(prog = prog)
    
    parser.add_argument("--version", action = "version", version = version)
    parser.add_argument('mode', choices=['bam', 'igv', 'mutation', 'sv', 'summary'], help = "analysis type")
    parser.add_argument("input_files", help = "input files path", type = str)
    parser.add_argument("output_file", help = "output file path", type = str)
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
        
    # call functions
    input_list = args.input_files.split(",")
    
    if args.mode == "igv":
        capture.merge_capture_bat(input_list, args.output_file, False)
    elif args.mode == "bam":
        capture.merge_pickup_script(input_list, args.output_file)
    elif (args.mode == "mutation") or (args.mode == 'sv') or (args.mode == 'summary'):
        capture.merge_result(input_list, args.output_file, args.mode, config)
     
