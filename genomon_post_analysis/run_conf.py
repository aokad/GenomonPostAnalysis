# -*- coding: utf-8 -*-
"""
Created on Wed Dec 02 17:43:52 2015

@author: okada

$Id: run_conf.py 125 2016-01-14 05:17:49Z aokada $
$Rev: 125 $
"""
prog = "genomon_pa conf"
version = prog + ": $Date: 2016-01-14 14:17:49 +0900 (2016/01/14 (木)) $$Rev: 125 $"

def main(argv):
    from genomon_post_analysis import tools
    from genomon_post_analysis import capture
    import argparse
    
    parser = argparse.ArgumentParser(prog = prog)
    
    parser.add_argument("--version", action = "version", version = version)
    parser.add_argument("--config_file", help = "config file", type = str, default = "")
    parser.add_argument("--config_text", help = "config text", type = str, default = "")

    args = parser.parse_args(argv)
    
    # config
    if len(args.config_file) > 0:
        [config, conf_file] = tools.load_config(args.config_file)
    elif len(args.config_text) > 0:
        config = tools.parse_config(args.config_text)
        conf_file = ""
    else:
        [config, conf_file] = tools.load_config("")
    
    capture.print_conf(config, conf_file)
    