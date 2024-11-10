import { YOLOAnnotation, LabelInfo, BoundingBox } from '@/app/lib/types';

// TODO: Implement test and fix these two functions.
export const generateYOLOAnnotations = (boundingBoxes: BoundingBox[], imageWidth: number, imageHeight: number): YOLOAnnotation[] => {
  return boundingBoxes.map((box) => {
    if (box.label_id === undefined) {
      throw new Error('Label ID is undefined');
    }
    const xCenter = (box.x + box.width / 2) / imageWidth;
    const yCenter = (box.y + box.height / 2) / imageHeight;
    const width = box.width / imageWidth;
    const height = box.height / imageHeight;
    return {
      class_id: box.label_id,
      x_center: xCenter,
      y_center: yCenter,
      width: width,
      height: height,
    };
  });
};


// Implementation of generateBoundingBoxesFromYOLO
export const generateBoundingBoxesFromYOLO = (annotations: YOLOAnnotation[], labels: LabelInfo[], imageWidth: number, imageHeight: number): BoundingBox[] => {
    return annotations.map((annotation) => {
      // NOTE: Since the label_id is basically same as class_id, we might be able to omit this check.
        const label = labels.find((l) => l.label_id === annotation.class_id);
        if (!label) {
            throw new Error(`Label with ID ${annotation.class_id} not found`);
        }

        const x = (annotation.x_center - annotation.width / 2) * imageWidth;
        const y = (annotation.y_center - annotation.height / 2) * imageHeight;
        const width = annotation.width * imageWidth;
        const height = annotation.height * imageHeight;

        return {
            x,
            y,
            width,
            height,
            label_id: label.label_id,
            color: label.label_color,
        };
    });
};