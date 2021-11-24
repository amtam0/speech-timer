from flair.models import SequenceTagger
from speechbrain.pretrained import EncoderASR, EncoderDecoderASR, EncoderClassifier

#NER
tagger_fr = SequenceTagger.load("amtam0/speech-timer")
tagger_en = SequenceTagger.load("amtam0/timer-ner-en")

#ASR
asr_model_fr = EncoderASR.from_hparams(source="speechbrain/asr-wav2vec2-commonvoice-fr",
                                savedir="./pretrained_models/asr-wav2vec2-commonvoice-fr")
asr_model_en = EncoderDecoderASR.from_hparams(source="speechbrain/asr-wav2vec2-commonvoice-en",
                                savedir="./pretrained_models/asr-wav2vec2-commonvoice-en")
# asr_model_en = EncoderDecoderASR.from_hparams(source="speechbrain/asr-crdnn-rnnlm-librispeech",
#                                 savedir="./pretrained_models/asr-crdnn-rnnlm-librispeech")

#Language detector
langu_model = EncoderClassifier.from_hparams(source="speechbrain/lang-id-commonlanguage_ecapa",
                                savedir="./pretrained_models/lang-id-commonlanguage_ecapa")