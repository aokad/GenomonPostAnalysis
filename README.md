# GenomonPostAnalysis

Genomonが作成した結果ファイルから以下を作成します。

 - IGV captureスクリプトを作成 <font color="red">※</font>
 - 検出された変異の周りだけbamを抽出するスクリプトを作成 <font color="red">※</font>
 - サンプルごとのresult.txtを縦に連結
 
 <font color="red">※ 手動で実行してください。</font>
 
-------------------------------------------------------------------------

##Dependency

 - python >= 2.7
 - Genomon

-------------------------------------------------------------------------

##Install

```
git clone https://github.com/aokad/GenomonPostAnalysis.git
cd GenomonPostAnalysis

python setup.py build install --user
```

-------------------------------------------------------------------------

##Run

### (1) スクリプト実行

#### (1.1) all-in-one

```
cd {working dir}

genomon_pa_run all ./result {genomon_root}
```

<br>
<br>

オプション解説

```
$ genomon_pa_run
usage: genomon_post_analysis [-h] [--version] [--task_config_file TASK_CONFIG_FILE]
                             [--genomon_config_file GENOMON_CONFIG_FILE]
                             {mutation,sv,summary,all} output_dir genomon_root
```

`--task_config_file, --genomon_config_file` オプションは将来、Genomonに統合したとき用です。

設定しなければデフォルトの設定ファイルを使用します。

デフォルトの設定ファイル `genomon_post_analysis.cfg` はgenomon_post_analysisインストールディレクトリ直下にあります。

<br>
<br>


#### (1.2) svの結果だけ実行したい場合

```
cd {working dir}

genomon_pa_run sv ./result {genomon_root}
```

<br>
<br>

#### (1.3) 実行結果のディレクトリ

実行後、以下の場所にスクリプトが2つ作成されますので、それぞれ実行してください。

実行するときのカレントディレクトリはどこでもいいです。アクセス権限さえあれば。

```
./result/
├── mutation                   <====== svと同じ構成なので省略
       (省略)
       
└── summary                    <==== summaryは結合して1ファイルにするだけ。
     └── merge.csv

└── sv
     ├── bam                                              <==== 検出された変異の周りだけ切り取ったbam
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
     │   └── pickup.sh                                   ★ === (1) ===
  
     ├── capture                                          <==== IGVキャプチャ画像
     │   ├── TCGA-2J-AAB4-01_14_107236445_18_8424657.png
          (省略)
     │   ├── TCGA-YY-A8LH-01_X_147009840_X_147009922.png
     │   └── capture.bat                                  ★ === (2) ===
     ├── log
     └── merge.csv
```

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

### (2) パッケージ利用

使用可能なメソッド

<1サンプルごと>

 - write_capture_bat(data_file, output_file, output_dir, ID, mode, yml, task_config): IGV captureスクリプトを作成
 - write_pickup_script(data_file, output_file, output_dir, ID, mode, yml, task_config, genomon_config): 検出された変異の周りだけbamを抽出するスクリプトを作成

<全サンプルまとめる>

 - merge_capture_bat(files, output_file, delete_flg): write_capture_bat で作成したbatを一括実行するスクリプト作成
 - merge_pickup_script(files, output_file): write_pickup_script で作成したbatを一括実行するスクリプト作成
 - merge_result(files, output_file, mode, task_config): サンプルごとのresult.txtを縦に連結


以下はGenomon解析結果を1ファイルづつ処理し、最後にmerge関数でまとめる例です。

変数は以下の値とします。


```
working_dir = {任意}

data_file   = working_dir + "/sv/TCGA-05-5715-01/TCGA-05-5715-01.genomonSV.result.txt"
output_dir  = working_dir + "/result/sv/"
ID = "TCGA-05-5715-01"
mode = "sv"
yml = working_dir + "/sv/config/TCGA-05-5715-01.yaml"
genomon_config = "{Genomon install dir}/genomon.cfg"
task_config = "{Genomon install dir}/dna_task_param.cfg"
```

<br>
<br>

#### (2.1) IGV captureスクリプト作成

```
import genomon_post_analysis.capture

files = []

output_file = output_dir + "/capture/TCGA-05-5715-01.bat"
write_capture_bat(data_file, output_file, output_dir, ID, mode, yml, task_config)

files.append = output_file

(サンプルの数だけ繰り返す。)

# スクリプトをまとめる
output_file = output_dir + "/capture/capture.bat"
merge_capture_bat(files, output_file, True)

```

<br>
<br>

#### (2.2) 検出された変異の周りだけbamを抽出する

```
import genomon_post_analysis.capture

files = []

output_file = output_dir + "/pickup/TCGA-05-5715-01.bat"
write_pickup_script(data_file, output_file, output_dir + "/pickup", ID, mode, yml, task_config, genomon_config)

files.append = output_file

(サンプルの数だけ繰り返す。)

# スクリプトをまとめる
output_file = output_dir + "/pickup/run.bat"
merge_pickup_script(files, output_file)
```

<br>
<br>

#### (2.3) resultリストを縦に連結

```
import genomon_post_analysis.capture
import glob

files = glob.glob(working_dir + "/sv/*/*.txt")
output_file = output_dir + "/merge/result.csv"

merge_result(files, output_file, mode, task_config)


```

<br>
<br>

### (3) 設定ファイル

 - 設定ファイルはインストールディレクトリ直下にあります。
 - 設定ファイルを編集したら再度 `python setup.py build install --user` してください。
 - <font color="red">赤字は今後変更がありそうな項目</font>

genomon_post_analysis.cfg

<pre>
# 
# $Id: README.md 99 2015-12-15 08:49:47Z aokada $
# $Rev: 99 $
# 

###########
# post analysis

[capture]
use_pickup_bam = True
capture_max = 100
capture_width = 200

[pickup]
pickup_width = 800
markdup_bam_suffix = .markdup.bam
pickup_bam_suffix = .markdup.pickup.bam

# result files's specification

[result_format_mutation]
sept = \t
<font color="red">header = True</font>
<font color="red">suffix = _genomon_mutations.result.txt</font>

<font color="red">col_pos_chr1 = 0</font>
<font color="red">col_pos_start = 1</font>
<font color="red">col_pos_chr2 = 0</font>
<font color="red">col_pos_end = 2</font>

col_pos_pvalue_ebcall =
col_pos_pvalue_fisher =
col_pos_positive =

[result_format_sv]
sept = \t
<font color="red">header = False</font>
<font color="red">suffix = .genomonSV.result.txt</font>

<font color="red">col_pos_chr1 = 0</font>
<font color="red">col_pos_start = 1</font>
<font color="red">col_pos_chr2 = 3</font>
<font color="red">col_pos_end = 4</font>

col_pos_pvalue_ebcall =
col_pos_pvalue_fisher =
col_pos_positive =

[result_format_summary]
sept = \t
header = True
<font color="red">suffix = .tsv</font>

[merge_format_mutation]
# this option is only available with option 'header = True'
filters =

[merge_format_sv]
# this option is only available with option 'header = True'
# for example
# filters =  {'read_pairs_not_control': ('>=', '0.05'), 'fisher': ('>=', '2')}
filters =

[merge_format_sumarry]
# now specification, summary has no option.
filters =

###########
# tools path

[REFERENCE]
ref_fasta = /home/w3varann/database/GRCh37/GRCh37.fa

[TOOLS]
samtools  = /home/w3varann/tools/samtools-1.2/samtools
bedtools  = /home/w3varann/tools/bedtools-2.17.0/bin/bedtools
biobambam = /home/w3varann/tools/biobambam-0.0.191/bin

</pre>

