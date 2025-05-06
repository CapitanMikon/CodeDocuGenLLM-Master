import argparse
import json


def run_evaluate_score(input_ai_dir, input_improvedai_dir):

    with open(input_ai_dir, "r") as f:
        ai_bleu_data = json.loads(f.read())

    with open(input_improvedai_dir, "r") as f:
        improvedai_bleu_data = json.loads(f.read())

    assert len(ai_bleu_data) == len(improvedai_bleu_data)


    skipped = 0

    results_ai = {
        'description': {
            'avg_bleu': 0,
            'avg_bleu1': 0,
            'avg_bleu2': 0,
            'avg_bleu3': 0,
            'avg_bleu4': 0,
            'total': len(ai_bleu_data),
            'failed': 0,
        },
        'return': {
            'avg_bleu': 0,
            'avg_bleu1': 0,
            'avg_bleu2': 0,
            'avg_bleu3': 0,
            'avg_bleu4': 0,
            'total': len(ai_bleu_data),
            'failed': 0,
        },
        'params': {
            'avg_bleu': 0,
            'avg_bleu1': 0,
            'avg_bleu2': 0,
            'avg_bleu3': 0,
            'avg_bleu4': 0,
            'total': 0,
            'failed': 0,
        }
    }

    results_improvedai = {
        'description': {
            'avg_bleu': 0,
            'avg_bleu1': 0,
            'avg_bleu2': 0,
            'avg_bleu3': 0,
            'avg_bleu4': 0,
            'total': len(improvedai_bleu_data),
            'failed': 0,
        },
        'return': {
            'avg_bleu': 0,
            'avg_bleu1': 0,
            'avg_bleu2': 0,
            'avg_bleu3': 0,
            'avg_bleu4': 0,
            'total': len(improvedai_bleu_data),
            'failed': 0,
        },
        'params': {
            'avg_bleu': 0,
            'avg_bleu1': 0,
            'avg_bleu2': 0,
            'avg_bleu3': 0,
            'avg_bleu4': 0,
            'total': 0,
            'failed': 0,
        }
    }

    for i in range(len(ai_bleu_data)):
        assert ai_bleu_data[i]['signature'] == improvedai_bleu_data[i]['signature']

        # if ai_bleu_data[i]['bleu_desc'] is None or improvedai_bleu_data[i]['bleu_desc'] is None:
        #     skipped += 1
        #     continue

        if ai_bleu_data[i]['bleu_desc'] is None:
            results_ai['description']['failed'] += 1
            # results_ai['description']['avg_bleu'] -= 1
            #as if we added 0
        else:
            results_ai['description']['avg_bleu'] += ai_bleu_data[i]['bleu_desc']['bleu']
            results_ai['description']['avg_bleu1'] += ai_bleu_data[i]['bleu_desc']['bleu-1']
            results_ai['description']['avg_bleu2'] += ai_bleu_data[i]['bleu_desc']['bleu-2']
            results_ai['description']['avg_bleu3'] += ai_bleu_data[i]['bleu_desc']['bleu-3']
            results_ai['description']['avg_bleu4'] += ai_bleu_data[i]['bleu_desc']['bleu-4']

        if improvedai_bleu_data[i]['bleu_desc'] is None:
            results_improvedai['description']['failed'] += 1
            #as if we added 0
            # results_improvedai['description']['avg_bleu'] -= 1
        else:
            results_improvedai['description']['avg_bleu'] += improvedai_bleu_data[i]['bleu_desc']['bleu']
            results_improvedai['description']['avg_bleu1'] += improvedai_bleu_data[i]['bleu_desc']['bleu-1']
            results_improvedai['description']['avg_bleu2'] += improvedai_bleu_data[i]['bleu_desc']['bleu-2']
            results_improvedai['description']['avg_bleu3'] += improvedai_bleu_data[i]['bleu_desc']['bleu-3']
            results_improvedai['description']['avg_bleu4'] += improvedai_bleu_data[i]['bleu_desc']['bleu-4']

        ##
        if ai_bleu_data[i]['bleu_return_desc'] is None:
            #as if we added 0
            results_ai['return']['failed'] += 1
            # results_ai['return']['avg_bleu'] -= 1
        else:
            results_ai['return']['avg_bleu'] += ai_bleu_data[i]['bleu_return_desc']['bleu']
            results_ai['return']['avg_bleu1'] += ai_bleu_data[i]['bleu_return_desc']['bleu-1']
            results_ai['return']['avg_bleu2'] += ai_bleu_data[i]['bleu_return_desc']['bleu-2']
            results_ai['return']['avg_bleu3'] += ai_bleu_data[i]['bleu_return_desc']['bleu-3']
            results_ai['return']['avg_bleu4'] += ai_bleu_data[i]['bleu_return_desc']['bleu-4']

        if improvedai_bleu_data[i]['bleu_return_desc'] is None:
            results_improvedai['return']['failed'] += 1
            #as if we added 0
            # results_improvedai['return']['avg_bleu'] -= 1
        else:
            results_improvedai['return']['avg_bleu'] += improvedai_bleu_data[i]['bleu_return_desc']['bleu']
            results_improvedai['return']['avg_bleu1'] += improvedai_bleu_data[i]['bleu_return_desc']['bleu-1']
            results_improvedai['return']['avg_bleu2'] += improvedai_bleu_data[i]['bleu_return_desc']['bleu-2']
            results_improvedai['return']['avg_bleu3'] += improvedai_bleu_data[i]['bleu_return_desc']['bleu-3']
            results_improvedai['return']['avg_bleu4'] += improvedai_bleu_data[i]['bleu_return_desc']['bleu-4']
        ##

        ## params
        if ai_bleu_data[i]['bleu_params'] is None:
            #as if we added 0
            results_ai['params']['failed'] += 1
        elif len(ai_bleu_data[i]['bleu_params']) > 0:
            results_ai['params']['total'] += 1
            #for each param
            for p in ai_bleu_data[i]['bleu_params']:
                results_ai['params']['avg_bleu'] += p['bleu']
                results_ai['params']['avg_bleu1'] += p['bleu-1']
                results_ai['params']['avg_bleu2'] += p['bleu-2']
                results_ai['params']['avg_bleu3'] += p['bleu-3']
                results_ai['params']['avg_bleu4'] += p['bleu-4']

            results_ai['params']['avg_bleu'] /= len(ai_bleu_data[i]['bleu_params'])
            results_ai['params']['avg_bleu1'] /= len(ai_bleu_data[i]['bleu_params'])
            results_ai['params']['avg_bleu2'] /= len(ai_bleu_data[i]['bleu_params'])
            results_ai['params']['avg_bleu3'] /= len(ai_bleu_data[i]['bleu_params'])
            results_ai['params']['avg_bleu4'] /= len(ai_bleu_data[i]['bleu_params'])

        ##
        if improvedai_bleu_data[i]['bleu_params'] is None:
            # as if we added 0
            results_improvedai['params']['failed'] += 1
        elif len(improvedai_bleu_data[i]['bleu_params']) > 0:
            results_improvedai['params']['total'] += 1
            # for each param
            for p in improvedai_bleu_data[i]['bleu_params']:
                results_improvedai['params']['avg_bleu'] += p['bleu']
                results_improvedai['params']['avg_bleu1'] += p['bleu-1']
                results_improvedai['params']['avg_bleu2'] += p['bleu-2']
                results_improvedai['params']['avg_bleu3'] += p['bleu-3']
                results_improvedai['params']['avg_bleu4'] += p['bleu-4']

            results_improvedai['params']['avg_bleu'] /= len(improvedai_bleu_data[i]['bleu_params'])
            results_improvedai['params']['avg_bleu1'] /= len(improvedai_bleu_data[i]['bleu_params'])
            results_improvedai['params']['avg_bleu2'] /= len(improvedai_bleu_data[i]['bleu_params'])
            results_improvedai['params']['avg_bleu3'] /= len(improvedai_bleu_data[i]['bleu_params'])
            results_improvedai['params']['avg_bleu4'] /= len(improvedai_bleu_data[i]['bleu_params'])
        ##

    ## TODO: throws

    results_ai['description']['avg_bleu'] /= results_ai['description']['total'] #- results_ai['description']['failed'])
    results_improvedai['description']['avg_bleu'] /= results_improvedai['description']['total']# - results_improvedai['description']['failed'])
    diff =  results_improvedai['description']['avg_bleu'] - results_ai['description']['avg_bleu']
    print(f"Improved against normal [desc]: {diff * 100} %")

    results_ai['return']['avg_bleu'] /= results_ai['return']['total'] #- results_ai['return']['failed'])
    results_improvedai['return']['avg_bleu'] /= results_improvedai['return']['total']# - results_improvedai['return']['failed'])
    diff =  results_improvedai['return']['avg_bleu'] - results_ai['return']['avg_bleu']
    print(f"Improved against normal [return]: {diff * 100} %")

    results_ai['params']['avg_bleu'] /= results_ai['params']['total'] #- results_ai['return']['failed'])
    results_improvedai['params']['avg_bleu'] /= results_improvedai['params']['total']# - results_improvedai['return']['failed'])
    diff =  results_improvedai['params']['avg_bleu'] - results_ai['params']['avg_bleu']
    print(f"Improved against normal [params]: {diff * 100} %")

    print("Done!")
    # calculate avg bleu score for description


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='evaluate', description="")
    parser.add_argument('--ai', help="", required=True)
    parser.add_argument('--improvedai', help="", required=True)
    # parser.add_argument('--filename', help="", required=True)
    args = parser.parse_args()

    run_evaluate_score(args.ai, args.improvedai)
    # save_data(data, args.filename)