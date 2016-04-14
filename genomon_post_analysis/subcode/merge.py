# -*- coding: utf-8 -*-
"""
Created on Wed Dec 02 17:43:52 2015

@author: okada

$Id: merge.py 141 2016-04-14 00:44:32Z aokada $
"""

import tools

def load_potisions(mode, config):

    [section_in, section_out] = tools.get_section(mode)
    header = tools.config_getboolean(config, section_in, "header")
    
    must = {}
    opts = {}
    for option in config.options(section_in):
        param = ""
        if option.find("col_") == 0:
            param = option.replace("col_", "")
        
        if len(param) > 0:
            if param.find("opt_") == 0:
                if header == True:
                    opts[param.replace("opt_", "")] = config.get(section_in, option)
                else:
                    opts[param.replace("opt_", "")] = config.getint(section_in, option)
            else:
                if header == True:
                    must[param] = config.get(section_in, option)
                else:
                    must[param] = config.getint(section_in, option)
                
    return {"must": must, "option": opts}
    
def _load_option(mode, config):

    [section_in, section_out] = tools.get_section(mode)
    
    # data read
    header = config.getboolean(section_in, "header")
    if header < 0:
        header = 0
    sept = config.get(section_in, "sept").replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r")
    comment = tools.config_getstr(config, section_in, "comment")
    lack = tools.config_getstr(config, section_out, "lack_column_complement")
    suffix = tools.config_getstr(config, section_in, "suffix")
    suffix_filt = tools.config_getstr(config, section_in, "suffix_filt")
    
    # return option dict
    return {"header": header, "sept": sept, "comment": comment, "lack": lack, "suffix": suffix, "suffix_filt": suffix_filt}
    
def _merge_metadata(files, option):

    import os

    # read all file's meta-data
    meta_data = []
    headers = []
    for file_path in files:
        if len(option["comment"]) == 0:
            break
        
        for line in open(file_path):
            line = line.rstrip()
            if len(line) == 0:
                continue
            
            if line.find(option["comment"]) == 0:
                data = line.split(":")
                if len(data) < 2:
                    continue
                
                meta_data.append([data[0].replace(" ", ""), data[1].strip(), file_path])
                headers.append(data[0].replace(" ", ""))
            else:
                break
    
    # merge meta-data
    headers = list(set(headers))
    headers.sort()
    meta_text = ""
    for header in headers:
        values = {}
        for meta in meta_data:
            if meta[0] == header:
                if values.has_key(meta[1]) == False:
                    values[meta[1]] = []
                values[meta[1]].append(meta[2])
                
        for key in values:
            meta_text += header + ":" + key
            if len(values[key]) != len(files):
                f_text = ""
                for f in values[key]:
                    if len(f_text) > 0:
                        f_text += ","
                    f_text += os.path.basename(f).replace(option["suffix"], "").replace(option["suffix_filt"], "")
                meta_text += ":" + f_text
            meta_text += "\n"
    
    return meta_text

def _merge_title(files, option):

    if option["header"] == False:
        return []
        
    # titles
    merged_title = []
    for file_path in files:
        title = []
        for line in open(file_path):
            
            line = line.rstrip()
            if len(line.replace(option["sept"], "")) == 0:
                continue
            
            if line.find(option["comment"]) == 0:
                continue
                
            title = line.replace(",", ";").split(option["sept"])
            break
        
        for col in title:
            if (col in merged_title) == False:
                merged_title.append(col)
    
    return merged_title

def merge_result_fast(files, ids, output_file, mode, config, extract = False):

    def calc_map(header, all_header):
        mapper = [-1]*len(all_header)
        for i in range(len(all_header)):
            if all_header[i] in header:
                mapper[i] = header.index(all_header[i])
            else:
                mapper[i] = -1
        return mapper
        
    import os

    if len(files) == 0:
        return {}
        
    for file_path in files:
        if os.path.exists(file_path) == False:
            print ("[ERROR] file is not exist. %s" % file_path)
            files.remove(file_path)
            continue 
    
    option = _load_option(mode, config)
    if option["header"] == False:
        print ("[ERROR] header is necessary for this function.")
        return {}
        
    meta_text = _merge_metadata(files, option)

    positions = load_potisions(mode, config)
    
    if extract == False:
        titles = _merge_title(files, option)
    else:
        titles = []
        for key in positions["must"]:
            titles.append(positions["must"][key])
        for key in positions["option"]:
            titles.append(positions["option"][key])

    # update positions to merged title
    if ("id" in positions["option"]) == False:
        positions["option"]["id"] = "id"
    if (positions["option"]["id"] in titles) == False:
        titles.insert(0, positions["option"]["id"])

    # write meta-data to file
    f = open(output_file, mode = "w")
    f.write(meta_text)
    f.write(",".join(titles))
    f.write("\n")
    
    for idx in range(len(files)):
        file_path = files[idx]
        
        header = []
        mapper = []
        lines = []
        lines_count = 0
        for line in open(file_path):
            line = line.rstrip()
            if len(line.replace(option["sept"], "")) == 0:
                continue
            
            if line.find(option["comment"]) == 0:
                continue
            
            line = line.replace(",", ";") 
            if len(header) == 0:
                header = line.split(option["sept"])
                mapper = calc_map(header, titles)
                continue
            
            data = line.split(option["sept"])
            sort_data = []
            for i in range(len(titles)):
                if mapper[i] < 0:
                    if titles[i] == positions["option"]["id"]:
                        sort_data.append(ids[idx])
                    else:
                        sort_data.append(option["lack"])
                else:
                    sort_data.append(data[mapper[i]])
            
            lines.append(",".join(sort_data) + "\n")
            lines_count += 1
            
            if (lines_count > 10000):
                f.writelines(lines)
                lines = []
                lines_count = 0

        if (lines_count > 0):
            f.writelines(lines)
        
    f.close()
    
    return positions
      
if __name__ == "__main__":
    pass
