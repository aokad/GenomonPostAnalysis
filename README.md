[![Build Status](https://travis-ci.org/aokad/GenomonPostAnalysis.svg?branch=master)](https://travis-ci.org/aokad/GenomonPostAnalysis)
[![License](https://img.shields.io/badge/license-MIT-red.svg?style=flat)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg?style=flat)](http://genomon.readthedocs.org)
<!-- [![PyPI version](https://badge.fury.io/py/xxx.svg)](http://badge.fury.io/py/xxx)-->

# GenomonPostAnalysis

Genomonが作成した結果ファイルから以下を作成します。

 - IGV captureスクリプトを作成 <font color="red">※</font>
 - 検出された変異の周りだけbamを抽出するスクリプトを作成 <font color="red">※</font>
 - サンプルごとのresult.txtを連結
 
 <font color="red">※ 手動で実行してください。</font>
 
-------------------------------------------------------------------------

## Dependency

 - python = 2.7
 - GenomonPipeline (Install参照)
 
-------------------------------------------------------------------------

## Install

GenomonPipelineのバージョンごとに適応するバージョンが異なります。

[リリース](https://github.com/aokad/GenomonPostAnalysis/releases) のページより対応するバージョンをダウンロードしてご使用ください。

```
wget https://github.com/aokad/GenomonPostAnalysis/archive/v1.4.1.zip
unzip v1.4.1.zip
cd GenomonPostAnalysis
python setup.py build install --user
```

-------------------------------------------------------------------------

## Run

```
cd {working dir}

# dna
genomon_pa dna {output_dir} {genomon_root} {genomon_sample_sheet}

# rna
genomon_pa rna {output_dir} {genomon_root} {genomon_sample_sheet}
```

## コマンド解説

```
$ genomon_pa --help
usage: genomon_pa [-h] [--version] [--config_file CONFIG_FILE]
                  {dna,rna,mutation,sv,qc,fusion,starqc}
                  output_dir
                  genomon_root
                  sample_sheet

positional arguments:
  {mutation,sv,qc,fusion,starqc}
                        analysis type マージしたい結果
  output_dir            path to output-dir  ※ディレクトリ構成は 実行結果のディレクトリ 参照
  genomon_root          path to Genomon-working-root
  sample_sheet          path to Genomon-samplesheet.csv

optional arguments:   欄外参照
  --config_file CONFIG_FILE            config file
  -h, --help                           show this help message and exit
  --version                            show programs version number and exit
```

 - `--config_file` 

    設定しなければデフォルトの設定ファイルを使用します。

    デフォルトの設定ファイル `genomon_post_analysis.cfg` はgenomon_post_analysisインストールディレクトリ直下にあります。

    ※このファイルを編集しても変更は反映されません。--config_file オプションで変更したファイルを渡してください。

<br>
<br>


## Directory structure

実行後、以下の場所にスクリプトが2つ作成されますので、それぞれ実行してください。

実行するときのカレントディレクトリはアクセス権限さえあればどこでもいいです。

<pre>
{output_dir}
│
├── merge.mutation.txt         <====== 各結果ファイルを結合したもの
├── merge.qc.txt
├── merge.sv.txt
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

## A. License 

See document LICENSE.
