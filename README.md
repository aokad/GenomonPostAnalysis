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
                      {all,mutation,sv,qc,fusion,starqc} output_dir genomon_root

```
 - `{mutation,sv,qc,all}`

    実行モード
    
    - all: すべて
    - mutation / sv / qc: (DNA) 各結果のみ
    - fusion / starqc: (RNA) 各結果のみ

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

## A. License 

See document LICENSE.
