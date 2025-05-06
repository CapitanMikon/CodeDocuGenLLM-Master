import datetime
import json
import sys


class Logger:

    def __init__(s, process_name):
        s.__filename = "" + process_name
        s.__llm_runs = None
        s.__started_date = None
        s.__ended_date = None

    def start_logging(s):
        s.__llm_runs = []
        s.__started_date = datetime.datetime.now()

    def end_logging(s):
        s.__ended_date = datetime.datetime.now()
        s.__save_log_to_file()

    def log_run(s, run_metadata, chain=None):
        new_run_data = {
            "model": run_metadata.response_metadata['model'],
            "langchain_run_id": run_metadata.id,
            "prompt_tokens": run_metadata.response_metadata['prompt_eval_count'],
            "response_tokens": run_metadata.response_metadata['eval_count'],
            "total_tokens": run_metadata.response_metadata['prompt_eval_count'] + run_metadata.response_metadata['eval_count'],
            "duration_in_seconds":  run_metadata.response_metadata['total_duration'] * (10**-9),
            "tokens_per_second": run_metadata.response_metadata['eval_count'] / run_metadata.response_metadata['eval_duration'] * 10**9,
            "started": run_metadata.response_metadata['created_at'],
        }

        if chain is not None:
            try:
                if chain.steps[len(chain.steps)-1].num_ctx is not None:
                    new_run_data["max_context_size"] = chain.steps[len(chain.steps)-1].num_ctx
            except IndexError:
                print("failed to log context_size. Reason: chain.steps[INDEX]", file=sys.stderr, flush=True)

        s.__llm_runs.append(new_run_data)

    def __save_log_to_file(s):
        data = {
            "started" : str(s.__started_date.isoformat()),
            "ended" : str(s.__ended_date.isoformat()),
            "total_seconds_taken": (s.__ended_date - s.__started_date).total_seconds(),
            "llm_runs" : s.__llm_runs,
        }

        json_obj = json.dumps(data, indent=4)

        with open(f"{s.__filename}_{s.__started_date.strftime('%H-%M-%S-%d-%m-%Y')}.log", "w") as file:
            file.write(json_obj)

