# GenomonPostAnalysis

Genomonが作成した結果ファイルから以下を作成します。

 - IGV captureスクリプトを作成 <font color="red">※</font>
 - 検出された変異の周りだけbamを抽出するスクリプトを作成 <font color="red">※</font>
 - サンプルごとのresult.txtを縦に連結
 
 <font color="red">※ 手動で実行してください。</font>
 
-------------------------------------------------------------------------

##Dependency

 - python >= 2.7
 - Genomon >= 2.0.3

-------------------------------------------------------------------------

##Install

```
git clone https://github.com/aokad/GenomonPostAnalysis.git
cd GenomonPostAnalysis

python setup.py build install --user
```

-------------------------------------------------------------------------

##Run

### (1) all-in-one

```
cd {working dir}

genomon_pa run all {output_dir} {genomon_root}
```

<br>
<br>

オプション解説

```
$ genomon_pa run
usage: genomon_pa run [-h] [--version] [--config_file CONFIG_FILE]
                      {mutation,sv,qc,all} output_dir genomon_root

```
 - `{mutation,sv,qc,all}`

    実行モード
    
    - all: すべて
    - mutation / sv / qc: 各結果のみ

<br>

 - `output_dir`

    出力ディレクトリ
    
    ディレクトリ構成は (2) 実行結果のディレクトリ 参照

<br>

 - `--config_file` 

    設定しなければデフォルトの設定ファイルを使用します。

    デフォルトの設定ファイル `genomon_post_analysis.cfg` はgenomon_post_analysisインストールディレクトリ直下にあります。

    ※このファイルを編集しても変更は反映されません。--config_file オプションで変更したファイルを渡してください。

<br>
<br>


### (2) 実行結果のディレクトリ

実行後、以下の場所にスクリプトが2つ作成されますので、それぞれ実行してください。

実行するときのカレントディレクトリはどこでもいいです。アクセス権限さえあれば。

<pre>
{output_dir}
│
├── merge.mutation.csv         <====== 各結果ファイルを結合したもの
├── merge.qc.csv
├── merge.sv.csv
│
├── mutation                   <====== svと同じ構成なので省略
       (省略)

└── sv
     ├── bam                                              <==== 検出された変異の周りだけ切り取ったbam
            (スクリプトを実行するとここに出力される)
     │   ├── TCGA-2J-AAB4-01
     │   │   ├── TCGA-2J-AAB4-01.markdup.pickup.bam
     │   │   ├── TCGA-2J-AAB4-01.markdup.pickup.bam.bai
     │   │   ├── TCGA-2J-AAB4-10.markdup.pickup.bam
     │   │   └── TCGA-2J-AAB4-10.markdup.pickup.bam.bai
          (省略)
     │   └── TCGA-Z5-AAPL-01
     │       ├── TCGA-Z5-AAPL-01.markdup.pickup.bam
     │       ├── TCGA-Z5-AAPL-01.markdup.pickup.bam.bai
     │       ├── TCGA-Z5-AAPL-10.markdup.pickup.bam
     │       └── TCGA-Z5-AAPL-10.markdup.pickup.bam.bai
     ├── bam_script
     │   ├── pickup.TCGA-2J-AAB4-01.markdup.sh
          (省略)
     │   ├── pickup.TCGA-Z5-AAPL-01.markdup.sh
     │   └── pickup.sh     <font color="red">★ === (1) ===</font>
  
     ├── capture                                          <==== IGVキャプチャ画像
            (スクリプトを実行するとここに出力される)
     ├── capture_script
     │   └── capture.bat   <font color="red">★ === (2) ===</font>
     ├── log
     └── merge.csv
</pre>

<br>

★ (1) 検出された変異の周りだけbamを抽出するスクリプト

実行例

```
bash pickup.sh
```

★ (2) IGV captureスクリプト

IGVを起動して実行してください。

<br>
<br>

-------------------------------------------------------------------------

### (3) 設定ファイル

 - 設定ファイルはインストールディレクトリ直下にあります。
 - <font color="red">赤字は今後変更がありそうな項目</font>

genomon_post_analysis.cfg

<pre>
# 
# $Id: README.md 145 2016-04-18 01:10:29Z aokada $
# $Rev: 145 $
# 

###########
# post analysis
[igv]
enable = True
capture_max = 100
capture_width = 200

[bam]
enable = True
pickup_width = 800
input_bam_suffix = .markdup.bam
output_bam_suffix = .markdup.pickup.bam

# result files's specification

[result_format_mutation]
sept = \t
header = True
suffix = .genomon_mutation.result.txt
suffix_filt = .genomon_mutation.result.filt.txt
comment = #

col_chr1 = Chr
col_start = Start
col_chr2 = Chr
col_end = End

[result_format_sv]
sept = \t
header = True
suffix = .genomonSV.result.txt
suffix_filt = .genomonSV.result.filt.txt
comment = #

col_chr1 = Chr_1
col_start = Pos_1
col_chr2 = Chr_2
col_end = Pos_2

[result_format_qc]
sept = \t
header = True
suffix = .genomonQC.result.txt
comment = #

[merge_format_mutation]
lack_column_complement = NA
include_unfilt = True
include_unpair = True
include_unpanel = True
all_in_one = True
separate = True
output_all   = merge_mutation.csv
output_case1 = merge_mutation_pair_controlpanel.csv
output_case2 = merge_mutation_pair.csv
output_case3 = merge_mutation_unpair_controlpanel.csv
output_case4 = merge_mutation_unpair.csv
output_filt_all = merge_mutation_filt.csv
output_filt_case1 = merge_mutation_filt_pair_controlpanel.csv
output_filt_case2 = merge_mutation_filt_pair.csv
output_filt_case3 = merge_mutation_filt_unpair_controlpanel.csv
output_filt_case4 = merge_mutation_filt_unpair.csv

[merge_format_sv]
lack_column_complement = NA
include_unfilt = True
include_unpair = True
include_unpanel = True
all_in_one = True
separate = True
output_all   = merge_sv.csv
output_case1 = merge_sv_pair_controlpanel.csv
output_case2 = merge_sv_pair.csv
output_case3 = merge_sv_unpair_controlpanel.csv
output_case4 = merge_sv_unpair.csv
output_filt_all   = merge_sv_filt.csv
output_filt_case1 = merge_sv_filt_pair_controlpanel.csv
output_filt_case2 = merge_sv_filt_pair.csv
output_filt_case3 = merge_sv_filt_unpair_controlpanel.csv
output_filt_case4 = merge_sv_filt_unpair.csv

[merge_format_qc]
lack_column_complement = NA
include_unfilt = True
all_in_one = True
separate = False
output_all = merge_qc.csv

###########
# Stand Alone

## Invalid in the case called from Genomon
[tools]
samtools  = /home/w3varann/tools/samtools-1.2/samtools
bedtools  = /home/w3varann/tools/bedtools-2.17.0/bin/bedtools
</pre>

