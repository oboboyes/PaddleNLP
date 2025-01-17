model_item=gpt3_moe
fp_item=fp32
dp_degree=1
bs_item=8
run_mode=DP_MoE_C1
device_num=N1C1

model=gpt

# get data
cd ./tests
bash ./test_tipc/dygraph/moe/${model}/benchmark_common/prepare.sh
# run
bash ./test_tipc/dygraph/moe/${model}/benchmark_common/run_benchmark.sh ${model_item} ${fp_item} ${dp_degree} ${bs_item} ${run_mode} ${device_num} 2>&1;
