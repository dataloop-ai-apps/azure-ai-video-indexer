from utils import convert_to_seconds
import dtlpy as dl
import numpy as np


class AudioIndexer:
    def __init__(self):
        self.model_name = ''

    def extract_transcripts(self, transcripts, item):
        annotations = list()
        for transcript in transcripts:
            if len(transcript['instances']) != 1:
                assert False
            annotation_definition = dl.Subtitle(text=transcript['text'],
                                                label=f"Speaker:{transcript['speakerId']}")
            annotation = dl.Annotation.new(annotation_definition=annotation_definition,
                                           automated=True,
                                           item=item,
                                           metadata={"system": {"model": {'confidence': transcript['confidence'],
                                                                          'name': self.model_name,
                                                                          }}},
                                           object_id=transcript["speakerId"],
                                           start_time=convert_to_seconds(transcript['instances'][0]['start']),
                                           end_time=convert_to_seconds(transcript['instances'][0]['end']))
            annotations.append(annotation)
        return annotations

    def extract_audio_effects(self, audio_effects, item):
        annotations = list()
        for effect in audio_effects:
            annotation_definition = dl.Classification(label=effect['type'])
            starts = list()
            ends = list()
            confidence = list()
            for instance in effect['instances']:
                starts.append(convert_to_seconds(instance['start']))
                ends.append(convert_to_seconds(instance['end']))
                confidence.append(instance['confidence'])
            annotation = dl.Annotation.new(annotation_definition=annotation_definition,
                                           automated=True,
                                           item=item,
                                           metadata={"system": {"model": {'confidence': np.mean(confidence),
                                                                          'name': self.model_name,
                                                                          }}},
                                           start_time=np.min(starts),
                                           end_time=np.max(ends))
            for start, end in zip(starts, ends):
                annotation.add_frame(annotation_definition=annotation_definition,
                                     frame_num=int(start * item.fps),
                                     object_visible=True)
                annotation.add_frame(annotation_definition=annotation_definition,
                                     frame_num=int(end * item.fps),
                                     object_visible=False)
            annotations.append(annotation)
        return annotations

    def extract_sentiments(self, sentiments, item):
        annotations = list()
        for sentiment in sentiments:
            annotation_definition = dl.Classification(label=sentiment['sentimentType'])
            starts = list()
            ends = list()
            for instance in sentiment['instances']:
                starts.append(convert_to_seconds(instance['start']))
                ends.append(convert_to_seconds(instance['end']))
            annotation = dl.Annotation.new(annotation_definition=annotation_definition,
                                           automated=True,
                                           item=item,
                                           metadata={"system": {"model": {'confidence': sentiment['averageScore'],
                                                                          'name': self.model_name,
                                                                          }}},
                                           start_time=np.min(starts),
                                           end_time=np.max(ends))
            for start, end in zip(starts, ends):
                annotation.add_frame(annotation_definition=annotation_definition,
                                     frame_num=int(start * item.fps),
                                     object_visible=True)
                annotation.add_frame(annotation_definition=annotation_definition,
                                     frame_num=int(end * item.fps),
                                     object_visible=False)
            annotations.append(annotation)
        return annotations

    def extract_emotions(self, emotions, item):
        annotations = list()
        for emotion in emotions:
            annotation_definition = dl.Classification(label=emotion['type'])
            starts = list()
            ends = list()
            confidence = list()
            for instance in emotion['instances']:
                starts.append(convert_to_seconds(instance['start']))
                ends.append(convert_to_seconds(instance['end']))
                confidence.append(instance['confidence'])
            annotation = dl.Annotation.new(annotation_definition=annotation_definition,
                                           automated=True,
                                           item=item,
                                           metadata={"system": {"model": {'confidence': np.mean(confidence),
                                                                          'name': self.model_name,
                                                                          }}},
                                           start_time=np.min(starts),
                                           end_time=np.max(ends))
            for start, end in zip(starts, ends):
                annotation.add_frame(annotation_definition=annotation_definition,
                                     frame_num=int(start * item.fps),
                                     object_visible=True)
                annotation.add_frame(annotation_definition=annotation_definition,
                                     frame_num=int(end * item.fps),
                                     object_visible=False)
            annotations.append(annotation)
        return annotations

    def extract(self, item: dl.Item, results):
        builder: dl.AnnotationCollection = item.annotations.builder()
        item.metadata['fps'] = 1000

        item.update(True)
        for video in results['videos']:
            transcripts = video['insights']['transcript']
            builder.annotations.extend(self.extract_transcripts(transcripts=transcripts, item=item))
            audio_effects = video['insights']['audioEffects']
            builder.annotations.extend(self.extract_audio_effects(audio_effects=audio_effects, item=item))
            sentiments = video['insights']['sentiments']
            builder.annotations.extend(self.extract_sentiments(sentiments=sentiments, item=item))
            # ocrs = video['insights']['ocr']
            # extract_ocr(ocrs)
            emotions = video['insights']['emotions']
            builder.annotations.extend(self.extract_emotions(emotions=emotions, item=item))

        item.annotations.upload(builder)
