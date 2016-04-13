# -*- coding: utf-8 -*-
"""
Created on Wed Dec 02 17:43:52 2015

@author: okada

$Id: run_conf.py 138 2016-04-11 01:10:23Z aokada $
"""
prog = "genomon_pa conf"

def main(argv):
    import genomon_post_analysis.subcode.tools as tools
    import argparse
    
    parser = argparse.ArgumentParser(prog = prog)
    
    parser.add_argument("--version", action = "version", version = tools.version_text())
    parser.add_argument("--config_file", help = "config file", type = str, default = "")

    args = parser.parse_args(argv)
    
    # config
    [config, conf_file] = tools.load_config(args.config_file)
    
    tools.print_conf(config, conf_file, "Genomon Post Analysis")
