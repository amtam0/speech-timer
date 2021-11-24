import io
import os
import sys
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import time
import logging
import json
import shutil
import subprocess
import flair
from flair.models import SequenceTagger
from flair.data import Sentence
from speechbrain.pretrained import EncoderASR, EncoderDecoderASR, EncoderClassifier
from text_to_num import alpha2digit
import base64
import re
from pathlib import Path
import torch

logging.basicConfig(level=logging.INFO)

def predict_flare(model, TEXT_test):
    """
    """
    sentence = Sentence(TEXT_test)
    # predict the tags
    model.predict(sentence)
    result_dict = sentence.to_dict("ner")
    result_dict["raw_text"] = TEXT_test
    return result_dict


def doc_to_spans_flare(doc):
    """
    """
    spans = []
    scores = []
    entities = []
    results = []
    zipped = []
    predictions = doc["entities"]
    for prediction in predictions:
        if not prediction:
            continue
        spans.append({
            'from_name': 'label',
            'to_name': 'text',
            'type': 'labels',
            'value': {
                'start': prediction["start_pos"],
                'end': prediction["end_pos"],
                'text': prediction["text"],
                'labels': [str(prediction["labels"][0]).split()[0]],
#                 'score': [str(prediction["labels"][0]).split()[1].strip("()")]
            }
        })
        scores.append(float(str(prediction["labels"][0]).split()[1].strip("()")))
        entities.append(str(prediction["labels"][0]).split()[0])
        results.append(prediction["text"])
    final_dict = {#"spans":spans,
                 "entities":entities,
                 "scores":scores,
                 "result":results,
                 "zipped":[list(a) for a in zip(results, entities, scores)],
                 "raw_text":doc["raw_text"]}
    return final_dict


# def speech_ner(wav_file_path="output.wav"):
#     """
#     """
#     raw_text = asr_model.transcribe_file(wav_file_path)
#     print(raw_text)
#     digit_text = alpha2digit(raw_text,
#                 "fr", relaxed=True, signed=False, ordinal_threshold=10).lower()
#     print(digit_text)
#     #alpha2digit bug
#     digit_text = digit_text.replace("une heure","1 heure").replace("une minute","1 minute")
#     return doc_to_spans_flare(predict_flare(tagger, digit_text))

def speech_ner_fr(wav_file_path="output.wav"): #NEW
    """
    """
    raw_text = asr_model_fr.transcribe_file(wav_file_path)
    print(raw_text)
    digit_text = alpha2digit(raw_text,
                "fr", relaxed=True, signed=False, ordinal_threshold=10).lower()
    print(digit_text)
    #alpha2digit bug
    digit_text = digit_text.replace("une heure","1 heure").replace("une minute","1 minute").replace("une seconde","1 seconde")
    return doc_to_spans_flare(predict_flare(tagger_fr, digit_text))

def speech_ner_en(wav_file_path="output.wav"): #NEW
    """
    """
    raw_text = asr_model_en.transcribe_file(wav_file_path)
    print(raw_text)
    digit_text = alpha2digit(raw_text,
                "en", relaxed=True, signed=False, ordinal_threshold=10).lower()
    print(digit_text)
    #alpha2digit bug
    digit_text = digit_text.replace("one hour","1 hour").replace("one minute","1 minute").replace("one second","1 seconde")
    return doc_to_spans_flare(predict_flare(tagger_en, digit_text))

def timer_format(_dict):
    """
    """
    hours = int(_dict["hours"])
    minutes = int(_dict["minutes"])
    seconds = int(_dict["seconds"])
    # minutes
    sd_minutes = seconds // 60
    # remaining seconds
    seconds = seconds - (sd_minutes * 60)
    # total time
    time = '{:02}:{:02}'.format(int(minutes)+sd_minutes+60*hours, int(seconds))
    return time

def format_result(zipped, entities, Thresh = 0.6):
    """
    """
    wt_dict = {"seconds":0,
              "minutes":0,
              "hours":0}

    br_dict = {"seconds":0,
              "minutes":0,
              "hours":0}

    result_dict = {"nb_rounds":"2",
                   "wt":"01:00",
                  "br":"01:00"}
    Idx_to_rm = []
    #control Thresh
    for idx,zip_line in enumerate(zipped):
        if zip_line[2]<Thresh:
            Idx_to_rm.append(idx)
    for index in sorted(Idx_to_rm, reverse=True):
        del zipped[index]

    #control duplicates
    if len(entities)!=len(set(entities)):
        return result_dict
    #     pass
    else:
        #format
        for idx,zip_line in enumerate(zipped):
            if zip_line[1]=="nb_rounds":
                result_dict["nb_rounds"] = re.findall(r'\d+',zip_line[0])[0]
            if "_wt" in zip_line[1]:
                if zip_line[1]=="duration_wt_sd":
                    wt_dict["seconds"] = re.findall(r'\d+',zip_line[0])[0]
                elif zip_line[1]=="duration_wt_min":
                    wt_dict["minutes"] = re.findall(r'\d+',zip_line[0])[0]
                elif zip_line[1]=="duration_wt_hr":
                    wt_dict["hours"] = re.findall(r'\d+',zip_line[0])[0]
            if "_br" in zip_line[1]:
                if zip_line[1]=="duration_br_sd":
                    br_dict["seconds"] = re.findall(r'\d+',zip_line[0])[0]
                elif zip_line[1]=="duration_br_min":
                    br_dict["minutes"] = re.findall(r'\d+',zip_line[0])[0]
                elif zip_line[1]=="duration_br_hr":
                    br_dict["hours"] = re.findall(r'\d+',zip_line[0])[0]
        # print(br_dict)
        result_dict["br"] = timer_format(br_dict)
        result_dict["wt"] = timer_format(wt_dict)
        return result_dict

flair.cache_root = Path("/root/.flair")

# Load models
if torch.cuda.is_available():
    device_type = {"device":"cuda"}
else:
    device_type = {"device":"cpu"}
tagger_fr = SequenceTagger.load("amtam0/speech-timer")
tagger_en = SequenceTagger.load("amtam0/timer-ner-en")
asr_model_fr = EncoderASR.from_hparams(source="speechbrain/asr-wav2vec2-commonvoice-fr",
                                    savedir="./pretrained_models/asr-wav2vec2-commonvoice-fr",
                                   run_opts=device_type)
asr_model_en = EncoderDecoderASR.from_hparams(source="speechbrain/asr-wav2vec2-commonvoice-en",
                                              savedir="./pretrained_models/asr-wav2vec2-commonvoice-en",
                                             run_opts=device_type)
# asr_model_en = EncoderDecoderASR.from_hparams(source="speechbrain/asr-crdnn-rnnlm-librispeech",
#                                               savedir="./pretrained_models/asr-crdnn-rnnlm-librispeech",
#                                              run_opts=device_type)
lang_model = EncoderClassifier.from_hparams(source="speechbrain/lang-id-commonlanguage_ecapa",
                                            savedir="./pretrained_models/lang-id-commonlanguage_ecapa",
                                           run_opts=device_type)

logging.info("models are loaded")

def basic_handler(event=None,MODEL_NAME = ""): #NEW
    """
    """
    #json_keys
    body_image64 = event['body64'].encode("utf-8")
    img_path = "out.wav"
    with open(img_path, "wb") as f:
        f.write(base64.b64decode(body_image64))
    
    subprocess.call("ffmpeg -i {} -c:a pcm_f32le {} -y".format(img_path, "out_f.wav"),
                shell=True)
    
    with torch.no_grad():
        out_prob, score, index, text_lab = lang_model.classify_file('out_f.wav')
        if text_lab==["French"]:
            print("French")
            res = speech_ner_fr(wav_file_path="out_f.wav")
        elif text_lab==["English"]:
            print("English")
            res = speech_ner_en(wav_file_path="out_f.wav")
    
    return res

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

# Simple probe.
@app.route('/', methods=['GET'])
def hello():
    return 'Hello SPEECH TIMER !'

# Route http posts to this method
@app.route('/', methods=['POST'])
def run():
    start = time.time()
    data = request.json
    res = basic_handler(event=data, MODEL_NAME = str(data["model_name"]))
    formatted_res = format_result(res["zipped"], res["entities"], Thresh = 0.6)
    data["result"] = formatted_res
    data["raw"] = res
    logging.info("res {}".format(res))
    logging.info("formatted_res {}".format(formatted_res))
    data["process_time"] = "{}".format(time.time() - start)
    logging.info(f'Total time {time.time() - start:.2f}s')
    return jsonify(data)


if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'development'
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)