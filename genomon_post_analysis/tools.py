# -*- coding: utf-8 -*-
"""
Created on Wed Dec 02 17:43:52 2015

@author: okada

$Id: tools.py 125 2016-01-14 05:17:49Z aokada $
$Rev: 125 $
"""
    
def load_data_range(data_file, mode, config):

    import pandas
    import os
    
    if os.path.getsize(data_file) == 0:
        print "skip blank file %s" % data_file
        return [[],[]]
        
    if mode.lower() != "sv" and mode.lower() != "mutation":
        return [[],[]]
    
    [section_in, section_out] = get_section(mode)
    
    col_pos_chr1 = config.getint(section_in, "col_pos_chr1")
    col_pos_start = config.getint(section_in, "col_pos_start")
    col_pos_chr2 = config.getint(section_in, "col_pos_chr2")
    col_pos_end = config.getint(section_in, "col_pos_end")
    usecols = (col_pos_chr1, col_pos_start, col_pos_chr2, col_pos_end)
    
    skip = 0
    if config.getboolean(section_in, "header") == True:
        skip = 1
    
    # data read
    try:
        data = pandas.read_csv(data_file, header = None, usecols = usecols, skiprows = skip, sep = config.get(section_in, "sept"), engine = "python")
    except StopIteration:
        print "skip no data file %s" % data_file
        return [[],[]]
    except Exception as e:
        print "failure open data %s, %s" % (data_file, e.message)
        return [[],[]]
        
    if len(data) == 0:
        return [[],[]]
    
    data.sort([col_pos_chr1, col_pos_start])

    return [data, usecols]

def load_data_all(data_file, ID, mode, config):
    
    import pandas
    import ast
    import os
    
    if os.path.getsize(data_file) == 0:
        print "skip blank file %s" % data_file
        return []
    
    [section_in, section_out] = get_section(mode)
    
    # data read
    header = config.getboolean(section_in, "header")
    sept = config.get(section_in, "sept")
    
    if header == False:
        try:
            data = pandas.read_csv(data_file, header = None, sep = sept, engine = "python")
        except StopIteration:
            print "skip no data file %s" % data_file
            return []
        except Exception as e:
            print "failure open data %s, %s" % (data_file, e.message)
            return []
            
        if config.has_option(section_in, "col_pos_chr1") == True:
            col_pos_chr1 = config.getint(section_in, "col_pos_chr1")
        else:
            col_pos_chr1 = -1
        
        if config.has_option(section_in, "col_pos_start") == True:
            col_pos_start = config.getint(section_in, "col_pos_start")
        else:
            col_pos_start = -1
        
        if config.has_option(section_in, "col_pos_chr2") == True:
            col_pos_chr2 = config.getint(section_in, "col_pos_chr2")
        else:
            col_pos_chr2 = -1
        
        if config.has_option(section_in, "col_pos_end") == True:
            col_pos_end = config.getint(section_in, "col_pos_end")
        else:
            col_pos_end = -1
        
        titles = []
        for i in range(len(data.iloc[0])):
            if i == col_pos_chr1:
                if col_pos_chr1 == col_pos_chr2:
                    titles.append("Chr")
                else:
                    titles.append("Chr1")
            elif i == col_pos_chr2:
                titles.append("Chr2")
            elif i == col_pos_start:
                titles.append("Start")
            elif i == col_pos_end:
                titles.append("End")
            else:    
                titles.append("v%02d" % i)
                
        data.columns = titles
            
    else:
        try:
            data = pandas.read_csv(data_file, sep = sept, engine = "python")
        except StopIteration:
            print "skip no data file %s" % data_file
            return []
        except Exception as e:
            print "failure of open data %s, %s" % (data_file, e.message)
            return []
            
        titles = data.columns.get_values()
    
   # add columun "ID" 
    tmp = []
    for i in range(0,len(data[titles[0]])):
        tmp.append(ID)
    df_addition_col = pandas.DataFrame([tmp]).T
    df_addition_col.columns =["ID"]
    data_cat = pandas.concat([df_addition_col, data], axis=1)
    
    if header == False:
        return data_cat
        
    # filter
    if config.has_option(section_out, "filters") == False:
        return data_cat
    
    data_fi = data_cat    
    filters = config.get(section_out, "filters")
    
    if len(filters) > 0:
        di = ast.literal_eval(filters)
        
        for key in di:
            if (key in titles) == False:
                print ("[WARNING] colum %s is none in file %s." % (key, data_file))
                continue
                    
            ine = di[key][0]
            thr = float(di[key][1])
        
            if ine == '>':
                data_fi = data_fi[(data[key] > thr)]
            if ine == '>=':
                data_fi = data_fi[(data[key] >= thr)]
            if ine == '<':
                data_fi = data_fi[(data[key] < thr)]
            if ine == '<=':
                data_fi = data_fi[(data[key] <= thr)]
            if ine == '==':
                data_fi = data_fi[(data[key] == thr)]
            if ine == '!=':
                data_fi = data_fi[(data[key] != thr)]

    return data_fi
    
def load_yaml(f):
    
    import yaml
    
    yml = open(f)
    y_load = yaml.load(yml)
    yml.close()
    
    # normal only
    if y_load["matched_control"]["use"] == False:
        bam_normal = y_load["target"]["path_to_bam"]
        bam_tumor = ""

    else:
        bam_normal = y_load["matched_control"]["path_to_bam"]
        bam_tumor = y_load["target"]["path_to_bam"]
    
    return [bam_tumor, bam_normal]
    
def getID(result_file, mode, config):
    
    import os
    [sec_in, sec_out] = get_section(mode)

    return os.path.basename(result_file).replace(config.get(sec_in, "suffix"), "")

def get_section(mode):
    
    if mode.lower() == "sv":
        section_in = "result_format_sv"
        section_out = "merge_format_sv"
        
    elif mode.lower() == "mutation":
        section_in = "result_format_mutation"
        section_out = "merge_format_mutation"
    
    elif mode.lower() == "summary":
        section_in = "result_format_summary"
        section_out = "merge_format_summary"
    
    return [section_in, section_out]    
    
def load_config(config_file):
    
    import os
    import ConfigParser

    if len(config_file) == 0:
        config_file = os.path.dirname(os.path.abspath(__file__)) + "/../config/genomon_post_analysis.cfg"
        config_file = os.path.abspath(config_file)
    
    if os.path.exists(config_file) == False:
        return [None, config_file]
        
    config = ConfigParser.RawConfigParser()
    config.read(config_file)
    
    return [config, config_file]
    
def parse_config(config_text):
        
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    
    for item in config_text.split(" "):
        section = ""
        if item[0] == "[":
            section = item[1:len(item)-1]
            config.add_section(section)
        else:
            value = item.split("=")
            config.set(section, value[0], value[1])
    
    return config
    
    
    