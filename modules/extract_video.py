from utils import convert_to_seconds
import dtlpy as dl
import numpy as np


class VideoIndexer:
    def __init__(self):
        self.model_name = ''

    def extract_face(self, faces, item):
        annotations = list()
        for face in faces:
            annotation_definition = dl.Classification(label=face['name'])
            starts = list()
            ends = list()
            for instance in face.get('instances', list()):
                starts.append(convert_to_seconds(instance["start"]))
                ends.append(convert_to_seconds(instance["end"]))
            annotation = dl.Annotation.new(annotation_definition=annotation_definition,
                                           automated=True,
                                           item=item,
                                           metadata={"system": {"model": {'confidence': face['confidence'],
                                                                          'name': self.model_name,
                                                                          }}},
                                           object_id=face["id"],
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

    def extract_labels(self, labels, item):
        annotations = list()
        for label in labels:
            annotation_definition = dl.Classification(label=label['name'])
            starts = list()
            ends = list()
            confidence = list()
            for instance in label.get('instances', list()):
                starts.append(convert_to_seconds(instance['start']))
                ends.append(convert_to_seconds(instance['end']))
                confidence.append(instance['confidence'])
            annotation = dl.Annotation.new(annotation_definition=annotation_definition,
                                           automated=True,
                                           item=item,
                                           metadata={"system": {"model": {'confidence': np.mean(confidence),
                                                                          'name': self.model_name,
                                                                          }}},
                                           object_id=label["id"],
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
            for instance in sentiment.get('instances', list()):
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

    def extract_detected_objects(self, detected_objects, item):
        annotations = list()
        for obj in detected_objects:
            annotation_definition = dl.Classification(label=obj['type'])
            starts = list()
            ends = list()
            confidence = list()
            for instance in obj.get('instances', list()):
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

    def extract(self, item, results):
        builder: dl.AnnotationCollection = item.annotations.builder()
        for video in results.get('videos', list()):
            video_insights = video.get('insights', dict())

            builder.annotations.extend(
                self.extract_face(faces=video_insights.get('faces', list()),
                                  item=item))

            builder.annotations.extend(
                self.extract_labels(labels=video_insights.get('labels', list()),
                                    item=item))
            builder.annotations.extend(
                self.extract_sentiments(sentiments=video_insights.get('sentiments', list()),
                                        item=item))
            # ocrs = video['insights']['ocr']
            # extract_ocr(ocrs)

            builder.annotations.extend(
                self.extract_detected_objects(detected_objects=video_insights.get('detectedObjects', list()),
                                              item=item))

        item.annotations.upload(builder)
