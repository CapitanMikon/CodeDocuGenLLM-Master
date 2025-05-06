import json
import sys
from pathlib import Path

path = Path(sys.argv[1])

with open(str(path), 'r') as file:
    file_text = file.read()

json_object = json.loads(file_text)

avg_response_tokens = 0
avg_prompt_tokens = 0
avg_total_tokens = 0
avg_tps = 0
avg_run_duration = 0
total_time_spend_generating = 0

max_total_tokens_run = json_object['llm_runs'][0]
min_total_tokens_run = json_object['llm_runs'][0]
max_response_tokens_run = json_object['llm_runs'][0]
min_response_tokens_run = json_object['llm_runs'][0]
max_prompt_tokens_run = json_object['llm_runs'][0]
min_prompt_tokens_run = json_object['llm_runs'][0]
max_tps_run = json_object['llm_runs'][0]
min_tps_run = json_object['llm_runs'][0]
max_run_duration_run = json_object['llm_runs'][0]
min_run_duration_run = json_object['llm_runs'][0]


for run in json_object['llm_runs']:
    avg_tps += run['tokens_per_second']
    avg_response_tokens += run['response_tokens']
    avg_prompt_tokens += run['prompt_tokens']
    avg_total_tokens += run['total_tokens']
    avg_run_duration += run['duration_in_seconds']
    total_time_spend_generating += run['duration_in_seconds']

    # update minmax
    if max_total_tokens_run['total_tokens'] <= run['total_tokens']:
        max_total_tokens_run = run
    if min_total_tokens_run['total_tokens'] >= run['total_tokens']:
        min_total_tokens_run = run

    if max_response_tokens_run['response_tokens'] <= run['response_tokens']:
        max_response_tokens_run = run
    if min_response_tokens_run['response_tokens'] >= run['response_tokens']:
        min_response_tokens_run = run

    if max_prompt_tokens_run['prompt_tokens'] <= run['prompt_tokens']:
        max_prompt_tokens_run = run
    if min_prompt_tokens_run['prompt_tokens'] >= run['prompt_tokens']:
        min_prompt_tokens_run = run

    if max_tps_run['tokens_per_second'] <= run['tokens_per_second']:
        max_tps_run = run
    if min_tps_run['tokens_per_second'] >= run['tokens_per_second']:
        min_tps_run = run

    if max_run_duration_run['duration_in_seconds'] <= run['duration_in_seconds']:
        max_run_duration_run = run
    if min_run_duration_run['duration_in_seconds'] >= run['duration_in_seconds']:
        min_run_duration_run = run

avg_response_tokens /= len(json_object['llm_runs'])
avg_prompt_tokens /= len(json_object['llm_runs'])
avg_total_tokens /= len(json_object['llm_runs'])
avg_tps /= len(json_object['llm_runs'])
avg_run_duration /= len(json_object['llm_runs'])

print(f"Log name: {path.stem}")
print(f"Started: {json_object['started']}")
print(f"Ended: {json_object['ended']}")

print(10 * '-' + 10 * '#' + 10 * '-')
print(f"Total script duration: {json_object['total_seconds_taken']} sec")
print(f"Total generation duration {total_time_spend_generating} sec")

print(10 * '-' + 3 * '#' + "AVG" + 3 * '#' + 10 * '-')
print(f"Avg prompt tokens: {avg_prompt_tokens}")
print(f"Avg response tokens: {avg_response_tokens}")
print(f"Avg total tokens: {avg_total_tokens}")
print(f"Avg token per second: {avg_tps}")
print(f"Avg llm generation run duration: {avg_run_duration}")

print(10 * '-' + 3 * '#' + "MIN" + 3 * '#' + 10 * '-')
print(f"Min prompt tokens: {min_prompt_tokens_run['prompt_tokens']}")
print(f"Min response tokens: {min_response_tokens_run['response_tokens']}")
print(f"Min total tokens: {min_total_tokens_run['total_tokens']}")
print(f"Min token per second: {min_tps_run['tokens_per_second']}")
print(f"Min llm generation run duration: {min_run_duration_run['duration_in_seconds']}")

print(10 * '-' + 3 * '#' + "MAX" + 3 * '#' + 10 * '-')
print(f"Max prompt tokens: {max_prompt_tokens_run['prompt_tokens']}")
print(f"Max response tokens: {max_response_tokens_run['response_tokens']}")
print(f"Max total tokens: {max_total_tokens_run['total_tokens']}")
print(f"Max token per second: {max_tps_run['tokens_per_second']}")
print(f"Max llm generation run duration: {max_run_duration_run['duration_in_seconds']}")