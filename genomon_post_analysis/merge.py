# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 13:34:10 2016

@author: okada

$Id: merge.py $
"""

import genomon_post_analysis.subcode.merge as subcode_merge

def merge_mutaion_for_paplot(files, ids, output_file, config, extract = False):

    def calc_map(header, all_header):
        mapper = [-1]*len(all_header)
        for i in range(len(all_header)):
            if all_header[i] in header:
                mapper[i] = header.index(all_header[i])
            else:
                mapper[i] = -1
        return mapper
        
    import os

    mode = "mutation"

    for file_path in files:
        if os.path.exists(file_path) == False:
            print ("[ERROR] file is not exist. %s" % file_path)
            files.remove(file_path)
            continue 
        
    if len(files) == 0:
        return
        
    option = subcode_merge._load_option(mode, config)
    if option["header"] == False:
        print ("[ERROR] header is necessary for this function.")
        return
        
    meta_text = subcode_merge._merge_metadata(files, option)

    positions = subcode_merge.load_potisions(mode, config)
    
    if extract == False:
        titles = subcode_merge._merge_title(files, mode, option, config)
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

    if ("func" in positions["option"]) == False:
        positions["option"]["func"] = "func"
    if ("exonic_func" in positions["option"]) == False:
        positions["option"]["exonic_func"] = "exonic_func"
    if ("merge_func" in positions["option"]) == False:
        positions["option"]["merge_func"] = "merge_func"
        
    if (positions["option"]["merge_func"] in titles) == False \
        and positions["option"]["func"] in titles \
        and positions["option"]["exonic_func"] in titles:
        
            pos = titles.index(positions["option"]["func"])
            if pos < titles.index(positions["option"]["exonic_func"]):
                pos = titles.index(positions["option"]["exonic_func"])
            titles.insert(pos+1, positions["option"]["merge_func"])
    
    [rep1, rep2] = subcode_merge._split_char(mode, config)
    
    # write meta-data to file
    f = open(output_file + ".tmp", mode = "w")
    f.write(meta_text)
    f.write(option["sept_out"].join(titles))
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
            
            if len(option["comment"]) > 0 and line.find(option["comment"]) == 0:
                continue
            
            line = line.replace(rep1, rep2) 
            if len(header) == 0:
                header = line.split(option["sept"])
                mapper = calc_map(header, titles)
                continue
            
            data = line.split(option["sept"])
            sort_data = []
            func = ""
            exonic = ""
            for i in range(len(titles)):
                if mapper[i] < 0:
                    # add columuns
                    if titles[i] == positions["option"]["id"]:
                        sort_data.append(ids[idx])
                    elif titles[i] == positions["option"]["merge_func"]:
                        if func.find("splicing") >= 0:
                            sort_data.append("splicing")
                        else:
                            sort_data.append(exonic)
                    else:
                        sort_data.append(option["lack"])
                else:
                    if titles[i] == positions["option"]["func"]:
                        func = data[mapper[i]]
                    elif titles[i] == positions["option"]["exonic_func"]:
                        exonic = data[mapper[i]]
                        
                    sort_data.append(data[mapper[i]])
            
            lines.append(option["sept_out"].join(sort_data) + "\n")
            lines_count += 1
            
            if (lines_count > 10000):
                f.writelines(lines)
                lines = []
                lines_count = 0

        if (lines_count > 0):
            f.writelines(lines)
        
    f.close()
    os.rename(output_file + ".tmp", output_file)

def merge_star_qc_for_paplot(files, ids, output_file, config, extract = False):
    
    def formatt (input_path):
    
        header = []
        value = []
        
        for line in open(input_path):
            cells = line.rstrip().split("|")
            if len(cells) < 2:
                continue
            
            header.append(cells[0].strip(" ").rstrip(" "))
            value.append(cells[1].strip().replace("%", ""))
        
        return {"header": "\t".join(header), "value": "\t".join(value)}
    
    import os

    for file_path in files:
        if os.path.exists(file_path) == False:
            print ("[ERROR] file is not exist. %s" % file_path)
            files.remove(file_path)
            continue 
        
    if len(files) == 0:
        return
       
    # write meta-data to file
    option = subcode_merge._load_option("starqc", config)
    meta_text = subcode_merge._merge_metadata(files, option)
    
    f = open(output_file + ".tmp", mode = "w")
    if len(meta_text) > 0:
        f.write(meta_text + "\n")
    
    for idx in range(len(files)):
        data = formatt(files[idx])
        if (idx == 0):
            f.write("id\t" + data["header"] + "\n")
            
        f.write(ids[idx] + "\t" + data["value"] + "\n")
        
    f.close()
    os.rename(output_file + ".tmp", output_file)
    
if __name__ == "__main__":
   pass
