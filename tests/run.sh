cd `dirname $0`

# 全部通る
output=./output1
genomon_pa mutation $output ./files/dna/ ./files/dna/sample.csv --develop:debug True
genomon_pa sv $output ./files/dna/ ./files/dna/sample.csv
genomon_pa qc $output ./files/dna/ ./files/dna/sample.csv
genomon_pa fusion $output ./files/rna/ ./files/rna/sample.csv --develop:debug True
genomon_pa starqc $output ./files/rna/ ./files/rna/sample.csv

# 出力限定
output=./output2
genomon_pa mutation $output ./files/dna/ ./files/dna/sample.csv \
--igv:enable False \
--bam:enable False \
--merge_mutation:output_raw_all False \
--merge_mutation:output_filt_all False

genomon_pa fusion $output ./files/rna/ ./files/rna/sample.csv \
--merge_fusionfusion:output_raw_all False \
--merge_fusionfusion:output_filt_all False

output=./output3
genomon_pa mutation $output ./files/dna/ ./files/dna/sample.csv \
--igv:enable False \
--bam:enable False \
--merge_mutation:output_raw_case1 False \
--merge_mutation:output_raw_case2 False \
--merge_mutation:output_raw_case3 False \
--merge_mutation:output_raw_case4 False \
--merge_mutation:output_filt_case1 False \
--merge_mutation:output_filt_case2 False \
--merge_mutation:output_filt_case3 False \
--merge_mutation:output_filt_case4 False

genomon_pa sv $output ./files/dna/ ./files/dna/sample.csv \
--igv:enable False \
--bam:enable False \
--merge_sv:output_raw_case1 False \
--merge_sv:output_raw_case2 False \
--merge_sv:output_raw_case3 False \
--merge_sv:output_raw_case4 False \
--merge_sv:output_filt_case1 False \
--merge_sv:output_filt_case2 False \
--merge_sv:output_filt_case3 False \
--merge_sv:output_filt_case4 False

genomon_pa fusion $output ./files/rna/ ./files/rna/sample.csv \
--merge_fusionfusion:output_raw_case1 False \
--merge_fusionfusion:output_raw_case2 False \
--merge_fusionfusion:output_filt_case1 False \
--merge_fusionfusion:output_filt_case2 False

output=./output4
genomon_pa mutation $output ./files/dna/ ./files/dna/sample.csv \
--igv:enable False \
--bam:enable False \
--merge_mutation:output_raw_all False \
--merge_mutation:output_filt_all False \
--merge_mutation:output_raw_case1 False \
--merge_mutation:output_raw_case2 False \
--merge_mutation:output_raw_case3 False \
--merge_mutation:output_raw_case4 False \
--merge_mutation:output_filt_case1 False \
--merge_mutation:output_filt_case2 False \
--merge_mutation:output_filt_case3 False \
--merge_mutation:output_filt_case4 False

genomon_pa sv $output ./files/dna/ ./files/dna/sample.csv \
--igv:enable False \
--bam:enable False \
--merge_sv:output_raw_all False \
--merge_sv:output_filt_all False \
--merge_sv:output_raw_case1 False \
--merge_sv:output_raw_case2 False \
--merge_sv:output_raw_case3 False \
--merge_sv:output_raw_case4 False \
--merge_sv:output_filt_case1 False \
--merge_sv:output_filt_case2 False \
--merge_sv:output_filt_case3 False \
--merge_sv:output_filt_case4 False

genomon_pa fusion $output ./files/rna/ ./files/rna/sample.csv \
--merge_fusionfusion:output_raw_all False \
--merge_fusionfusion:output_filt_all False \
--merge_fusionfusion:output_raw_case1 False \
--merge_fusionfusion:output_raw_case2 False \
--merge_fusionfusion:output_filt_case1 False \
--merge_fusionfusion:output_filt_case2 False

