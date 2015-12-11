# GenomonPostAnalysis

Genomonが作成した結果ファイルから以下を作成します。

 - IGV captureスクリプトを作成
 - 検出された変異の周りだけbamを抽出するスクリプトを作成
 - サンプルごとのresult.txtを縦に連結
 
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

```
$ genomon_pa_run
usage: genomon_post_analysis [-h] [--version]
                             [--task_config_file TASK_CONFIG_FILE]
                             [--genomon_config_file GENOMON_CONFIG_FILE]
                             {mutation,sv} input_file_pattern output_dir
                             genomon_root
```

`--task_config_file, --genomon_config_file` オプションについて

genomon_post_analysisは独自のconfigファイルを持っているため、設定しなければデフォルトの設定ファイルを使用します。

デフォルトの設定ファイル `genomon_post_analysis.cfg` はgenomon_post_analysisインストールディレクトリ直下にあります。

もし、設定ファイルをGenomonに統合した場合は、`--task_config_file, --genomon_config_file` オプションでGenomonの設定ファイルを指定してください。


#### (1.1) SVの場合

```
cd {genomon working dir}

genomon_post_analysis sv "./sv/*/*.txt" ./result/ ./
```

実行後、以下の場所にスクリプトが2つ作成されますので、それぞれ実行してください。

★ (1) 検出された変異の周りだけbamを抽出するスクリプト

実行場所を問わず、以下ディレクトリ構成で出力します。

```
bash pickup.sh
```

★ (2) IGV captureスクリプト

IGVを起動して実行してください。


実行結果のディレクトリ

```
./result/
├── mutation
       (省略)
       
└── sv
     ├── bam
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
     ├── capture
     │   ├── TCGA-2J-AAB4-01_14_107236445_18_8424657.png
          (省略)
     │   ├── TCGA-YY-A8LH-01_X_147009840_X_147009922.png
     │   └── capture.bat                                  ★ === (2) ===
     ├── log
     └── merge.csv
```

-------------------------------------------------------------------------

### (2) パッケージ利用

使用可能なメソッド

 - write_capture_bat(data_file, output_file, output_dir, ID, mode, yml, task_config): IGV captureスクリプトを作成
 - write_pickup_script(data_file, output_file, output_dir, ID, mode, yml, task_config, genomon_config): 検出された変異の周りだけbamを抽出するスクリプトを作成
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

#### (2.3) resultリストを縦に連結

```
import genomon_post_analysis.capture
import glob

files = glob.glob(working_dir + "/sv/*/*.txt")
output_file = output_dir + "/merge/result.csv"

merge_result(files, output_file, mode, task_config)


```

